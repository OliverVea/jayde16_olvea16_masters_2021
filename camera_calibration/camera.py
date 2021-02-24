import cv2
import numpy as np

from math import sin, cos, pi

from enum import Enum

class CameraModels(Enum):
    DEFAULT = 0
    FISHEYE = 1

class Camera:
    def __init__(self, camera_matrix, distortion_coefficients, camera_model: str = None):
        self.K = camera_matrix
        self.d = distortion_coefficients
        self.type = camera_model

        if camera_model == CameraModels.FISHEYE:
            self.projectPoints = cv2.fisheye.projectPoints
            self.getOptimalNewCameraMatrix = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify
            self.initUndistortRectifyMap = cv2.fisheye.initUndistortRectifyMap

        else:
            self.projectPoints = cv2.projectPoints
            self.getOptimalNewCameraMatrix = cv2.getOptimalNewCameraMatrix
            self.initUndistortRectifyMap = cv2.initUndistortRectifyMap
    
    def transform_image(self, input, size: tuple, fov: tuple):
        input_size = (input.shape[1], input.shape[0])

        # Translating FOV from angles to radians.
        c = 1 / 2 * pi / 180
        va, ha = fov[1] * c, fov[0] * c
        
        # Edge (center-)points of ROI in 3D space
        pts = np.array([
            (sin(-ha), 0, cos(-ha)), 
            (sin(ha), 0, cos(ha)),
            (0, sin(-va), cos(-va)), 
            (0, sin(va), cos(va))])

        # Edge (center-)points in pixel coordinates
        pts, _ = self.projectPoints(pts, rvec=np.zeros((3,1)), tvec=np.zeros((3,1)), cameraMatrix=self.K, distCoeffs=self.d)

        # Calculating the necessary upscaling to crop the ROI to the desired image size.
        width = max(pts[:,0,0]) - min(pts[:,0,0])
        height = max(pts[:,0,1]) - min(pts[:,0,1])
        
        scale = (size[0] / width, size[1] / height)
        uncropped_size = (int(scale[0] * input_size[0]), int(scale[1] * input_size[1]))

        # Calculating new camera matrix (nK)
        nK, _ = self.getOptimalNewCameraMatrix(cameraMatrix=self.K, distCoeffs=self.d, imageSize=input_size, newImgSize=uncropped_size, alpha=0.0)

        # Undistoring image
        map1, map2 = self.initUndistortRectifyMap(cameraMatrix=self.K, distCoeffs=self.d, R=np.eye(3,3), newCameraMatrix=nK, size=uncropped_size, m1type=cv2.CV_32FC1)
        output = cv2.remap(input, map1, map2, interpolation=cv2.INTER_CUBIC)
        
        # Extracting principal point (center of camera)
        x, y = nK[0][2], nK[1][2]

        # Calculating ROI bounding box coordinates
        x1, y1, x2, y2 = x - size[0] / 2, y - size[1] / 2, x + size[0] / 2, y + size[1] / 2
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Extracting ROI
        output = output[y1:y2, x1:x2]

        return output