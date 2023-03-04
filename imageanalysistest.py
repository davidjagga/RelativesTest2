import cv2

def grayscale2(mainfile, relativefile):
    img_gray=cv2.imread(mainfile, 0)
    img_gray2 = cv2.imread(relativefile, 0)
    cv2.imwrite(mainfile, img_gray)
    cv2.imwrite(relativefile, img_gray2)
    analysisDict = {
        'height': 10,
        'eyeLength': 20,
        'skinColor': 'Brown',
        'filepath': mainfile,
        'relativefilepath': relativefile
    }
    return analysisDict