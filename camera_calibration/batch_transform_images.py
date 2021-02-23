from camera import Camera

import cv2
import numpy as np
import os


retval, K, d, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors, obj_points, img_points, not_used = np.load('camera_calibration_14dp_final.npy', allow_pickle=True)

cam = Camera(camera_matrix=K, distortion_coefficients=d)

image_size = (700, 500)
image_fov = (150, 120)

path = 'angleimages/'

files = os.listdir(path)

for file in files:
    img = cv2.imread(path + file)
    img = cam.transform_image(img, image_size, image_fov)

    cv2.imshow("undistorted", img)
    cv2.waitKey()