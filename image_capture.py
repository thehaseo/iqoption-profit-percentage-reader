from imagesearch import imagesearch, region_grabber
import cv2
import pytesseract
import numpy as np
import re


def set_coordinates_percentage_area(loc_coordinates_upleft):
    x_left_cord = loc_coordinates_upleft[0] + 150
    y_up_cord = loc_coordinates_upleft[1] + 15
    x_right_cord = loc_coordinates_upleft[0] + 250
    y_down_cord = loc_coordinates_upleft[1] + 40
    return (x_left_cord, y_up_cord, x_right_cord, y_down_cord)


# get grayscale image to improve tesseract output
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def process_image(image):
    img = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    img = get_grayscale(img)
    kernel = np.ones((1, 1), np.uint8)    
    img = cv2.dilate(img, kernel, iterations=1)    
    img = cv2.erode(img, kernel, iterations=1)
    img = thresholding(img)
    return img


def locate_portfolio_section(percentage):
    print(percentage)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    loc_coordinates_upleft = imagesearch("images/ganancia-actual-big-size-font.png")
    coordinates_percentage_area = set_coordinates_percentage_area(loc_coordinates_upleft)
    profit_section = region_grabber(coordinates_percentage_area)
    profit_section.save("images/screenshot.png")
    percentage_img = cv2.imread('images/screenshot.png')
    percentage_img = process_image(percentage_img)
    result = pytesseract.image_to_string(percentage_img, lang="eng")
    percentage = int(re.search(r'[+ -]+\d+', result).group())
    print(percentage)
