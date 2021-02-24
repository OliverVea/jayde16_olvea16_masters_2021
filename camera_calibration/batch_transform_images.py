from camera import Camera

import cv2
import numpy as np
import os

retval, K, d, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors, obj_points, img_points, not_used = np.load('camera_calibration_14dp_final_large.npy', allow_pickle=True)

cam = Camera(camera_matrix=K, distortion_coefficients=d)

image_size = (640*2, 480*2)
image_fov = (100, 120)

show_image = True

path = 'D:\\WindowsFolders\\Desktop\\camera_capture\\videos\\'

files = os.listdir(path)

print(f'Found {len(files)} files:')
print('\n'.join(files))

fourcc = cv2.VideoWriter_fourcc(*'HFYU')
vw = cv2.VideoWriter()

for i, file in enumerate(files):
    print(f'Undistorting file: {file}')

    vc = cv2.VideoCapture(path + file)

    vw.open(f'{file}.avi', fourcc, 21, image_size)

    while True:
        success, img = vc.read()

        if not success or cv2.waitKey(10) == 27:
            break

        img_out = cam.transform_image(img, image_size, image_fov)

        if show_image != False and (show_image == True or (isinstance(show_image, list) and show_image[i])): 
            cv2.imshow('undistorted', img_out) 

        vw.write(img_out)

    vw.release()
    
    
