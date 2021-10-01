import cv2,pytesseract
import numpy as np

img = cv2.imread('newpicture.jpg')

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


grayed = get_grayscale(img)

cv2.imshow('Grayscale Image',grayed)
cv2.waitKey(0)
cv2.destroyWindow('Grayscale Image')

def performOCR():
    text = pytesseract.image_to_string(grayed)
    print(text)
    #return text

performOCR()