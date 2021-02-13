import cv2
import numpy as np

filename = '2021-02-13_15-15-13.yuv'

height = 616
width = 816

frame_size = int(height * width * 1.5) 
shape = (int(height * 1.5), width)

f = open(filename, 'rb')

def read_uint10(byte_buf):
    data = np.frombuffer(byte_buf, dtype=np.uint8)
    #data = np.append(data, 0)
    # 5 bytes contain 4 10-bit pixels (5x8 == 4x10)
    b1, b2, b3, b4, b5 = np.reshape(data, (data.shape[0]//5, 5)).astype(np.uint16).T
    o1 = ((b2 % 4) << 8) + b1
    o2 = ((b3 % 16) << 6) + (b2 >> 2)
    o3 = ((b4 % 64) << 4) + (b3 >> 4)
    o4 = (b5 << 2) + (b4 >> 6)

    unpacked =  np.reshape(np.concatenate((o1[:, None], o2[:, None], o3[:, None], o4[:, None]), axis=1),  4*o1.shape[0])
    unpacked = unpacked.astype(np.uint8)
    return unpacked
 
def read_yuv():
    try:
        raw = f.read(frame_size)
        yuv = np.frombuffer(raw, dtype=np.uint8)
        yuv = yuv.reshape(shape)
    except Exception as e:
        print(e)
        return False, None

    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGRA_I420)

    return True, bgr

while True:
    ret, frame = read_yuv()
    if ret:
        cv2.imshow("frame", frame)
        cv2.waitKey()
    else:
        break