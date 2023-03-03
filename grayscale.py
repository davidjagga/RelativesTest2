import cv2

def grayscale(filename, destination):
    img_gray=cv2.imread(filename, 0)
    cv2.imwrite(destination, img_gray)