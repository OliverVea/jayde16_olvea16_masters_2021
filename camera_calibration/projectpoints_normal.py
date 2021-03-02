import cv2
import numpy as np
from math import tan, pi, cos, sin

from camera_calibration import CameraModels

img = cv2.imread('angleimages/vlcsnap-2021-02-22-22h23m07s859.png')

camera_model = CameraModels.FISHEYE
retval, cameraMatrix, distCoeffs, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors, obj_points, img_points, not_used = np.load('camera_calibration_14dp_final.npy', allow_pickle=True)


DIM = (816, 616)
camera_fov = 220

def get_xyz(r, a1, a2: float = 0):
    a1, a2 = a1 * pi / 180, a2 * pi / 180

    z = r * sin(a2) * cos(a1)
    x = r * sin(a2) * sin(a1)
    y = r * cos(a2)

    return x, y, z

# Oliver FOV Stuff 
out_fov = (150, 120)
a = 700
out_size = (a, a * out_fov[1] / out_fov[0])

va = out_fov[1] / 2
ha = out_fov[0] / 2

va = va * pi / 180
ha = ha * pi / 180

pts = np.array([
    (sin(-ha), 0, cos(-ha)), 
    (sin(ha), 0, cos(ha)),
    (0, sin(-va), cos(-va)), 
    (0, sin(va), cos(va)), 
])

#pts = np.array([tuple(get_xyz(1, a1, a2)) for a1, a2 in zip(a1s, a2s)])

pts, _ = cv2.projectPoints(pts, rvec=np.zeros((3,1)), tvec=np.zeros((3,1)), cameraMatrix=cameraMatrix, distCoeffs=distCoeffs)

x = [pt[0][0] for pt in pts]
y = [pt[0][1] for pt in pts]

width = max(x) - min(x)
height = max(y) - min(y)

scale = (out_size[0] / width, out_size[1] / height)
uncropped_size = (int(scale[0] * DIM[0]), int(scale[1] * DIM[1]))
#uncropped_size = DIM
# / Oliver FOV Stuff

line_lenghts = [304, 320, 355, 270, 222, 200, 185]
angles = [0, 15, 30, 45, 60, 75, 85]

first = True
for length, angle in zip(line_lenghts, angles):
    x, _, z = get_xyz(length, angle)
    if first:
        object_points = np.array([[x, 0, z]]).reshape(1,1,3)
        first = False
    else:
        object_points = np.concatenate((object_points, np.array([[x, 0, z]]).reshape(1,1,3)))

newImgSize = tuple(d * 2 for d in DIM)

new_camera_matrix, validPixROI	= cv2.getOptimalNewCameraMatrix(cameraMatrix=cameraMatrix, distCoeffs=distCoeffs, imageSize=DIM, newImgSize=uncropped_size, alpha=0.0)

image_points, jacobian = cv2.projectPoints(object_points, rvec=np.zeros((3,1)), tvec=np.zeros((3,1)), cameraMatrix=cameraMatrix, distCoeffs=distCoeffs)

undistorted_points = cv2.undistortPoints(src=image_points, cameraMatrix=cameraMatrix, distCoeffs=distCoeffs, P=cameraMatrix)

map1, map2 = cv2.initUndistortRectifyMap( cameraMatrix=cameraMatrix, distCoeffs=distCoeffs, R=np.eye(3,3),newCameraMatrix=new_camera_matrix, size=uncropped_size, m1type=cv2.CV_32FC1)

undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_CUBIC)

# Center points
x, y = new_camera_matrix[0][2], new_camera_matrix[1][2]
#x, y = int(uncropped_size[0] / 2), int(uncropped_size[1] / 2)

# Bounding box coordinates
x1, y1, x2, y2 = x - out_size[0] / 2, y - out_size[1] / 2, x + out_size[0] / 2, y + out_size[1] / 2
x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

undistorted_img = undistorted_img[y1:y2, x1:x2]

cv2.drawMarker(img, (round(cameraMatrix[0][2]), round(cameraMatrix[1][2])),  (0, 0, 255), cv2.MARKER_CROSS, 1000, 1)
#cv2.drawMarker(undistorted_img, (round(cameraMatrix[0][2]), round(cameraMatrix[1][2])),  (0, 0, 255), cv2.MARKER_CROSS, 1000, 1)

for i, point in enumerate(pts):
    img = cv2.circle(img, (round(point[0][0]),round(point[0][1])), 1, ((1-i/len(image_points))*255,0,i*255/len(image_points)), thickness=5, lineType=8)

for i, point in enumerate(undistorted_points):
    undistorted_img = cv2.circle(undistorted_img, (round(out_size[0] / 2),round(out_size[1] / 2)), 1, ((1-i/len(image_points))*255,0,i*255/len(image_points)), thickness=5, lineType=8)

cv2.imshow("distorted", img)
cv2.imshow("undistorted", undistorted_img)
cv2.waitKey()

dummy = 0
