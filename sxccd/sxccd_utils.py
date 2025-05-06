import numpy as np


def decLH(LH):
    return LH[0] + 256*LH[1]


def dec2bytes(num, lg=2):
    return (num).to_bytes(lg, byteorder="little")


def dec2image(data, h, w):
    img_sz = int(len(data)/2)
    img = np.zeros((img_sz,1), dtype=np.uint32)
    for i in range(img_sz):
        img[i] = decLH( data[2*i:(2*i+2)])
    img = np.reshape(img, (h, w))
    return img
