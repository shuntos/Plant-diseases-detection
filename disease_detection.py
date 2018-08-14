import cv2
import numpy as np
import tomato_gui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui,QtCore,QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QInputDialog, QLineEdit,QFileDialog
from PyQt5.QtGui import QIcon, QPixmap,QImage
import sys
from PyQt5 import QtGui
import time
import copy
import datetime
from darkflow.net.build import TFNet






options = {"model": "bin/yolo-plant.cfg", "load": "bin/yolo-plant_1500.weights", "threshold": 0.3, "demo": "data/nepal.mp4", 'gpu': 0.2}
font = cv2.FONT_HERSHEY_SIMPLEX
tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]


class MainUiClass(QMainWindow,tomato_gui.Ui_MainWindow):  #main thread
	def __init__(self,parent = None):
		super(MainUiClass,self).__init__(parent)
		self.setupUi(self)
		self.threadclass = ThreadClass()
		self.threadclass2 = ThreadClass()
   #     self.threadclass.start()
    #    self.threadclass.update_frame.connect(self.update_frame)
		frame=cv2.imread('play.jpg')
		qformat=QImage.Format_Indexed8

		if len(frame.shape)==3:
			if frame.shape[2]==4:
				qformat=QImage.Format_RGBA8888
			else:
				qformat=QImage.Format_RGB888
		outimage=QImage(frame,frame.shape[1],frame.shape[0],frame.strides[0],qformat)
		self.label.setPixmap(QPixmap.fromImage(outimage))
		self.label.setScaledContents(True)
		self.show()
		self.pushButton_1.clicked.connect(self.start_image_detect)
		self.pushButton_2.clicked.connect(self.start_video_detect)
		self.pushButton_3.clicked.connect(self.openFile)

        # Ui_Dialog.pushButton.clicked.connect(self.database)



	def openFile(self):   
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		global fileName
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
		if fileName:
			print(fileName)




        # self.checkBox_1.setChecked(True)     #########This function make check box already chicked in GUI
	def btnstate(self, b):
		if b.isChecked() == True:
			print("print hello")
		else:
			print("no hello")




	def frame_resize(self,frame):
		dim = (800, 500)
		resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
		return resized


	def frame_resize2(self,imagex):
		height, width, _ = imagex.shape
        # print(height)
        # print(width)
		dim = (width,height)
		resized_img = cv2.resize(imagex, dim, interpolation=cv2.INTER_AREA)
		return resized_img

	def draw_rectangle(self,frame,centers):
		for i in centers:
			cv2.rectangle(frame, i[2][0], i[2][1], (255, 255, 0), 3)

		return frame
	def start_image_detect(self):
		global flag
		flag=1
		self.threadclass.start()
		self.threadclass.update_frame.connect(self.update_frame)

	def start_video_detect(self):
		global flag
		flag=2

		self.threadclass.start()
		self.threadclass.update_frame.connect(self.update_frame)





 






	def convert_Qimage(self,img):  ### convert np.darray image into Qimage which is displyed in Qlabel
		qformat=QImage.Format_Indexed8
		if len(img.shape)==3:
			if img.shape[2]==4:
				qformat=QImage.Format_RGBA8888
			else:
				qformat=QImage.Format_RGB888
		outframe=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)    # it throw error for big frames or without frame_resize
		outframe=outframe.rgbSwapped()
		return outframe

	def update_frame(self,img,label):         # update lcd ,Qlabel
#        self.progressBar.setValue(val)
#        print(centers)

		imgx=copy.copy(img)

		frame=self.frame_resize(img)
		outimage=self.convert_Qimage(frame)         ##convert to Qlabel which can then displayed




        # framex=self.frame_resize(imgx)
        # orig_frame=self.convert_Qimage(framex)
		self.label.setPixmap(QPixmap.fromImage(outimage))
		self.label.setScaledContents(True)
		if label == 'None':
			self.textBrowser.setPlainText("NO Diseases Identified")
			
		else:
			self.textBrowser.setPlainText("%s"%label)
			


   
		self.show()



class ThreadClass(QtCore.QThread):
	update_frame = pyqtSignal(np.ndarray,str)   # this is for yolo detection as it return list which contain count data

	def __init__(self, parent=None):
		super(ThreadClass,self).__init__(parent)
		print("hello")
	def __del__(self):
		self.wait()
 

  





	def run(self):
		label='None'
		if flag ==2:
			cap = cv2.VideoCapture(0)
			ret, frame = cap.read()
			while True:



				if type(frame) == np.ndarray:
					result = tfnet.return_predict(frame)
				else:
					print("Reached the end of stream..")
					break
				for color, result in zip(colors, result):
					tl = (result['topleft']['x'], result['topleft']['y'])
					br = (result['bottomright']['x'], result['bottomright']['y'])
					label = result['label']
					confidence = result['confidence']
					text = '{}: {:.0f}%'.format(label, confidence * 100)
					frame = cv2.rectangle(frame, tl, br, color, 5)
					frame = cv2.putText(frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        #result=getCentroid(results)
			cap.release()
			cv2.destroyAllWindows()


		elif flag==1:
					
			frame=cv2.imread("%s"%fileName)


			if type(frame) == np.ndarray:
				result = tfnet.return_predict(frame)
			else:
				print("Reached the end of stream..")
				return
			for color, result in zip(colors, result):
				tl = (result['topleft']['x'], result['topleft']['y'])
				br = (result['bottomright']['x'], result['bottomright']['y'])
				label = result['label']
				confidence = result['confidence']
				text = '{}: {:.0f}%'.format(label, confidence * 100)
				frame = cv2.rectangle(frame, tl, br, color, 5)
				frame = cv2.putText(frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
				cv2.imwrite("bact.jpg",frame)
        #result=getCentroid(results)




			self.update_frame.emit(frame,label)
			if cv2.waitKey(5) & 0xFF == ord('q'):
				pass
		cv2.destroyAllWindows()







if __name__== '__main__':
	a=QApplication(sys.argv)
	app=MainUiClass()
	app.show()
	a.exec_()
