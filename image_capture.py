import cv2
import pytesseract
import numpy as np
import re
import threading
import time
import chime
from imagesearch import imagesearch, region_grabber


class DetectScreen(threading.Thread):

    def __init__(self, query_percentage, more_or_less, info_window_widget):
                super().__init__()
                self.query_percentage = query_percentage
                self.more_or_less = more_or_less
                self.info_window = info_window_widget
                self.detener = threading.Event()
                self.daemon = True
                chime.theme("zelda")
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

    def run(self):
        while True:
            if self.detener.is_set():
                return
            self.locate_portfolio_section()
            time.sleep(2)

    def set_coordinates_percentage_area(self, loc_coordinates_upleft):
        x_left_cord = loc_coordinates_upleft[0] + 150
        y_up_cord = loc_coordinates_upleft[1] + 15
        x_right_cord = loc_coordinates_upleft[0] + 250
        y_down_cord = loc_coordinates_upleft[1] + 40
        return (x_left_cord, y_up_cord, x_right_cord, y_down_cord)

    # get grayscale image to improve tesseract output
    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def thresholding(self, image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def process_image(self, image):
        img = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        img = self.get_grayscale(img)
        kernel = np.ones((1, 1), np.uint8)    
        img = cv2.dilate(img, kernel, iterations=1)    
        img = cv2.erode(img, kernel, iterations=1)
        img = self.thresholding(img)
        return img

    def locate_portfolio_section(self):
        query_percentage = int(self.query_percentage)
        loc_coordinates_upleft = imagesearch("images/ganancia-actual-big-size-font.png")

        if loc_coordinates_upleft is None:
            return

        coordinates_percentage_area = self.set_coordinates_percentage_area(loc_coordinates_upleft)
        profit_section = region_grabber(coordinates_percentage_area)
        profit_section.save("images/screenshot.png")
        percentage_img = cv2.imread('images/screenshot.png')
        percentage_img = self.process_image(percentage_img)
        result = pytesseract.image_to_string(percentage_img, lang="eng")
        self.info_window.insert_text(f"El porcentaje de ganancia actual es: {result}")
        percentage_in_screen = int(re.search(r'[+ — -]\d+', result).group().replace("—", "-"))

        if self.more_or_less == "Mayor a":
            if percentage_in_screen >= query_percentage:
                chime.success()
        if self.more_or_less == "Menor a":
            if percentage_in_screen <= query_percentage:
                chime.success()

    def stop(self):
        self.detener.set()