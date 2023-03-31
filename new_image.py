import cv2
import numpy as np
import utils

img = np.zeros(((193 + 100) * 25, 2000, 3), np.uint8)
img[...] = np.array((255,255,255))

names = cv2.imread('img_nomes.jpg')
lines = utils.fatiar_vertical(names, 25)
for i, line in enumerate(lines):
    print(line.shape)
    img[i * (193 + 100):i * (193 + 100) + 193, 0:2000] = line
    cv2.imshow(f"line{i}", line)
    cv2.imshow("img", img)
    cv2.waitKey(0)
cv2.imwrite("img_nomes_2.jpg", img)
cv2.destroyAllWindows()
# cv2.imshow('img', img)
# cv2.waitKey(0)