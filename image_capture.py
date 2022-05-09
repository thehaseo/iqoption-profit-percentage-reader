import cv2
import pytesseract
import numpy as np
import re
import threading
import time
import chime
import pyautogui
from imagesearch import imagesearch, region_grabber


class DetectScreen(threading.Thread):

    def __init__(self, main_frame, query_percentage, more_or_less, info_window_widget, tesseract_route):
                super().__init__()
                self.gui_main_frame = main_frame
                self.query_percentage = query_percentage
                self.more_or_less = more_or_less
                self.info_window = info_window_widget
                self.detener = threading.Event()
                self.daemon = True
                chime.theme("zelda")
                pytesseract.pytesseract.tesseract_cmd = tesseract_route

    def run(self):
        while True:
            if self.detener.is_set():
                return
            self.locate_portfolio_section()
            time.sleep(2)

    def set_coordinates_percentage_area(self, loc_coordinates_upleft, font_size):
        if font_size == "big":
            x_left_cord = loc_coordinates_upleft[0] + 165
            y_up_cord = loc_coordinates_upleft[1] + 15
            x_right_cord = loc_coordinates_upleft[0] + 250
            y_down_cord = loc_coordinates_upleft[1] + 40
            return (x_left_cord, y_up_cord, x_right_cord, y_down_cord)
        elif font_size == "mid":
            x_left_cord = loc_coordinates_upleft[0] + 170
            y_up_cord = loc_coordinates_upleft[1] + 18
            x_right_cord = loc_coordinates_upleft[0] + 220
            y_down_cord = loc_coordinates_upleft[1] + 35
            return (x_left_cord, y_up_cord, x_right_cord, y_down_cord)
        elif font_size == "small":
            x_left_cord = loc_coordinates_upleft[0] + 164
            y_up_cord = loc_coordinates_upleft[1] + 18
            x_right_cord = loc_coordinates_upleft[0] + 207
            y_down_cord = loc_coordinates_upleft[1] + 33
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
        img = 255-img
        return img

    def locate_portfolio_section(self):
        query_percentage = int(self.query_percentage)
        loc_coordinates_upleft = imagesearch("images/ganancia-actual-big-size-font.png")

        # If iqoption app is not fullsize screen then try to get the image samples with littler fonts
        if loc_coordinates_upleft is None:
            loc_coordinates_upleft = imagesearch("images/ganancia-actual-mid-size-font.png")
            if loc_coordinates_upleft is None:
                loc_coordinates_upleft = imagesearch("images/ganancia-actual-small-size-font.png")
                if loc_coordinates_upleft is None:
                    self.info_window.insert_text("No se encuentra la zona de ganancia actual, despliegue la aplicación de iqoption en pantalla")
                    return
                coordinates_percentage_area = self.set_coordinates_percentage_area(loc_coordinates_upleft, "small")
            else:
                coordinates_percentage_area = self.set_coordinates_percentage_area(loc_coordinates_upleft, "mid")
        else:
            coordinates_percentage_area = self.set_coordinates_percentage_area(loc_coordinates_upleft, "big")
        profit_section = region_grabber(coordinates_percentage_area)
        profit_section.save("images/screenshot.png")
        percentage_img = cv2.imread('images/screenshot.png')
        percentage_img = self.process_image(percentage_img)
        result = pytesseract.image_to_string(percentage_img, lang="eng")
        if result == None:
            self.info_window.insert_text("Hubo un error al leer el porcentaje de ganancia, el screenshot del porcentaje que dió el error se encuentra en la carpeta errors")
            with open("errors/error.txt", "a") as errors:
                errors.write(f"La cifra con el error es: {result}\n")
        percentage_in_screen = re.search(r'[+ — - = -]\d+', result)  # Search for coincidences in profit percentage with regular expression to convert it to int
        if percentage_in_screen is not None:
            percentage_in_screen = int(percentage_in_screen.group().replace("—", "-").replace("=", "-"))
            self.info_window.insert_text(f"El porcentaje de ganancia actual es: {percentage_in_screen}%")
            if self.more_or_less == "Mayor a":
                if percentage_in_screen >= query_percentage:
                    chime.success()
                    pyautogui.press("f8")
                    self.gui_main_frame.start_program() 
            if self.more_or_less == "Menor a":
                if percentage_in_screen <= query_percentage:
                    chime.success()
                    pyautogui.press("f8")
                    self.gui_main_frame.start_program()
        else:
            self.info_window.insert_text("Hubo un error al leer el porcentaje de ganancia, la cifra leída se encuentra en la carpeta errors")
            with open("errors/error.txt", "a") as errors:
                errors.write(f"La cifra con el error es: {result}\n")

    def stop(self):
        self.detener.set()