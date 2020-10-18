import os
import sys

# import customDarkPalette

from Qt import QtWidgets
from Qt import QtCompat
# from Qt import QtGui

from ocr.main.ocr_converter import OcrImage
from ocr.main.voice_to_text import VoiceToText

cur_dir = os.path.dirname(os.path.dirname(__file__))
UI = os.path.join(cur_dir, 'ui', 'ocr_ui.ui')


class Ocr(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ocr, self).__init__()

        self.ui = QtCompat.loadUi(UI)
        self.setCentralWidget(self.ui)
        self.setWindowTitle('OCR')

        self.ui.voice_wd.hide()
        self.ui.text_wd.hide()
        # self.ui.image_converter_wd.hide()

        OcrImage(ui=self.ui)
        VoiceToText(ui=self.ui)

    def connections(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # customDarkPalette.customDarkPalette(app)
    ocr = Ocr()
    ocr.show()
    sys.exit(app.exec_())
