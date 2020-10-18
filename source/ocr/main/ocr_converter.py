from Qt import QtWidgets
from Qt import QtCompat
from Qt import QtGui
from Qt import QtCore

import cv2
import pytesseract
import argparse
import numpy as np
import os
import shutil
from functools import partial
from PIL import Image
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
# tessdata_dir_config = '--tessdata-dir r"C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
# Example config: '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
# It's important to include double quotes around the dir path.

os.environ['TESSDATA_PREFIX'] = r"C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"


class OcrImage(object):
    def __init__(self, ui=None):
        super(OcrImage, self).__init__()
        self.ui = ui
        self.connections()

    def get_image_file(self):
        print ('>>>>>', self.ui)
        dialog = QtWidgets.QFileDialog(self.ui)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_name = (dialog.selectedFiles())
            if self.ui.image_label_lb.isHidden():
                self.ui.image_label_lb.show()
            self.show_selected_image(file_name[0])
            self.image_to_text(file_name[0])

    def show_selected_image(self, img):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img))
        icon = icon.pixmap(300, 300)
        pimp01 = QtGui.QPixmap(icon)
        # pimp01 = pimp01.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        pimp_image = QtGui.QPixmap(pimp01)
        self.ui.image_label_lb.setMinimumSize(80, 80)
        self.ui.image_label_lb.setScaledContents(True)
        self.ui.image_label_lb.setPixmap(pimp_image)

    def hide_widget(self):
        if self.ui.image_converter_wd.isHidden():
            self.ui.image_converter_wd.show()
            return
        self.ui.image_converter_wd.hide()

    def open_camera(self):
        cam = cv2.VideoCapture(0)

        cv2.namedWindow("test")

        while True:
            captured_img = None
            ret, frame = cam.read()
            cv2.imshow("camera", frame)
            if not ret:
                break
            k = cv2.waitKey(1)

            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                file_path = self.get_directory_path()
                captured_img = file_path[0]
                img_name = os.path.basename(captured_img)
                cv2.imwrite(img_name, frame)
                cur_dir = os.path.dirname(__file__)
                src_path = os.path.join(cur_dir, img_name)
                dst_dir = os.path.dirname(captured_img)
                shutil.copy(src_path, dst_dir)
                os.remove(src_path)
                break
        cam.release()

        cv2.destroyAllWindows()
        if self.ui.image_label_lb.isHidden():
            self.ui.image_label_lb.show()
        self.show_selected_image(captured_img)
        self.image_to_text(captured_img)

    def get_directory_path(self):
        dialog = QtWidgets.QFileDialog(self.ui)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setDefaultSuffix('png')
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setNameFilters(['PNG (*.png)'])
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_name = (dialog.selectedFiles())

            return file_name

    def image_to_text(self, img):
        print ('>>>>', img)
        image = cv2.imread(img)

        gray = self.get_grayscale(image)
        thresh = self.thresholding(gray)
        opening = self.opening(gray)
        canny = self.canny(gray)

        d = pytesseract.image_to_data(image, output_type=Output.DICT)
        # d= pytesseract.image_to_string(image, lang='en', config=tessdata_dir_config)

        # print(d.keys())
        # print (d)
        print(d.get('text'))
        converted_text = ' '.join(d.get('text'))
        print ('>>>', converted_text)
        self.clear_text_edit(text=True)
        self.ui.image_text_te.textCursor().insertText(converted_text)

    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(self, image):
        return cv2.medianBlur(image, 5)

    # thresholding
    def thresholding(self, image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation
    def dilate(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    # erosion
    def erode(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation
    def opening(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    def canny(self, image):
        return cv2.Canny(image, 100, 200)

    # skew correction
    def deskew(self, image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)

        else:
            angle = -angle
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated

    # template matching
    def match_template(image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    def clear_text_edit(self, text=False):
        if not text:
            self.ui.image_text_te.clear()
            self.ui.image_label_lb.clear()
            self.ui.image_label_lb.hide()
        self.ui.image_text_te.clear()

    def connections(self):
            self.ui.open_file_pb.clicked.connect(partial(self.get_image_file))
            self.ui.image_hide_pb.clicked.connect(partial(self.hide_widget))
            self.ui.open_camera_pb.clicked.connect(partial(self.open_camera))
            self.ui.clear_text.clicked.connect(partial(self.clear_text_edit))


if __name__ == '__main__':
    oc = OcrImage()
    # oc.image_to_text(r"C:\Users\Sagar\Pictures\Saved Pictures\test.png")
    # oc.get_image_file()
