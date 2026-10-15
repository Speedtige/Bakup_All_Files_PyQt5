# Magno Efren - 2022
# https://www.youtube.com/c/MagnoEfren/videos

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QIcon

##==============================================================
##==============================================================

import imutils
import cv2
import os, sys

##=========================================================================================================
##=========================================================================================================

class Path():

    ##(Dir. Raiz.)
    ## Solamente para obtener el Directorio donde se encuentra Ejecutandose la app.
    def resource_path_app():

        try:
            path_app = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

        except Exception as e:
            print(e)

        except IOError as error:
            print( error )

        return path_app

    ##==============================================================
	##==============================================================

    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for pyinstaller"""

        try:
            #PyInstaller Create a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS

        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

##=========================================================================================================
##=========================================================================================================

class MyApp(QMainWindow):

	def __init__(self, IMG_Path):
		super(MyApp, self).__init__()

		self.Aicon_App = Path.resource_path('Ico\\1.ico')
		self.setWindowIcon(QIcon(self.Aicon_App))

		file = Path.resource_path_app()
		self.File_App = os.path.join(file, "UI", "design.ui")
		loadUi(self.File_App, self)

		self.open_image.clicked.connect(self.load_image)
		self.save_image.clicked.connect(self.save_image_final)
		self.reset_edit.clicked.connect(self.reset_image)

		self.slider_one.valueChanged['int'].connect(self.tonality)
		self.slider_two.valueChanged['int'].connect(self.saturation)
		self.slider_three.valueChanged['int'].connect(self.brightness)
		self.slider_four.valueChanged['int'].connect(self.gray_scale)
		self.filename = str()

		self.label_image.setScaledContents(True)

		self.IMG_URL = IMG_Path
		self.path_IM = ""

		print(f'Este es el Path, ARG:... {self.IMG_URL}')

		MyApp.mensaje(self)

    ##==============================================================
	##==============================================================

	def mensaje(self):

		if self.IMG_URL == "":

			print("\nBacio...  Sin Nada")

			bundle_dir = Path.resource_path_app()
			self.path_IM = os.path.join(bundle_dir, "Images", "Paint.png")
			print(self.path_IM)

			MyApp.load_image_2(self, self.path_IM)

		else:

			self.IMG_URL = self.IMG_URL
			print(f'La ruta es: {self.IMG_URL}')

			MyApp.load_image_2(self, self.IMG_URL)

    ##==============================================================
	##==============================================================

	def load_image_2(self, Image_Path):

		self.filename = Image_Path

		if len(self.filename)!=0:

			self.image = cv2.imread(self.filename)
			self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)	
			image = cv2.cvtColor(self.hsv, cv2.COLOR_HSV2RGB)	
			self.set_image(image)

    ##==============================================================
	##==============================================================

	def load_image(self):

		self.filename = QFileDialog.getOpenFileName(
			filter="Image JPG(*.jpg);;Image PNG(*.png)")[0]

		if len(self.filename)!=0:

			self.image = cv2.imread(self.filename)
			self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)	
			image = cv2.cvtColor(self.hsv, cv2.COLOR_HSV2RGB)	
			self.set_image(image)

    ##==============================================================
	##==============================================================

	def set_image(self,image):

		if len(self.filename)!=0:

			frame = imutils.resize(image, width=500, height=500)
			image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
			self.label_image.setPixmap(QPixmap.fromImage(image))

    ##==============================================================
	##==============================================================

	def tonality(self,value):

		if len(self.filename)!=0:

			h,s,v = cv2.split(self.hsv)
			r = 180 - value
			h[h>r] = 180
			h[h<=r] += value		
			hsv_final = cv2.merge((h,s,v))
			img = cv2.cvtColor(hsv_final,cv2.COLOR_HSV2RGB)
			self.image_final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			self.set_image(img)

    ##==============================================================
	##==============================================================

	def saturation(self,value):

		if len(self.filename)!=0:

			h,s,v = cv2.split(self.hsv)
			r = 255 - value
			s[s>r] = 255
			s[s<=r] += value
			hsv_final = cv2.merge((h,s,v))
			img = cv2.cvtColor(hsv_final,cv2.COLOR_HSV2RGB)
			self.image_final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			self.set_image(img)

    ##==============================================================
	##==============================================================

	def brightness(self, value):

		if len(self.filename)!=0:

			h,s,v = cv2.split(self.hsv)
			r = 255 - value
			v[v>r] = 255
			v[v<=r] += value		
			hsv_final = cv2.merge((h,s,v))
			img = cv2.cvtColor(hsv_final,cv2.COLOR_HSV2RGB)
			self.image_final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			self.set_image(img)

    ##==============================================================
	##==============================================================

	def gray_scale(self, value):

		if len(self.filename)!=0:

			gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
			r = 255 - value
			gray[gray>r] = 255
			gray[gray<=r] += value
			self.image_final = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
			self.set_image(self.image_final)

    ##==============================================================
	##==============================================================

	def save_image_final(self):

		if len(self.filename)!=0:

			filename = QFileDialog.getSaveFileName(filter="JPG(*.jpg);;PNG(*.png);;BMP(*.bmp)")[0]
			cv2.imwrite(filename, self.image_final)

    ##==============================================================
	##==============================================================

	def reset_image(self):

		if len(self.filename)!=0:

			self.slider_one.setValue(0)
			self.slider_two.setValue(0)
			self.slider_three.setValue(0)
			self.slider_four.setValue(0)

##=========================================================================================================
##=========================================================================================================

if __name__ == '__main__':

    if len(sys.argv)>1:

        IMG_Path = sys.argv[1]

    else:

        IMG_Path = ""

    app = QApplication(sys.argv)
    my_app = MyApp(IMG_Path)
    my_app.show()

    sys.exit(app.exec_())

##=========================================================================================================
##=========================================================================================================