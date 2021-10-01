from time import sleep

#sleep (5)

#import sys,re,os,sqlite3,cv2,pytesseract
import re
import os
import sqlite3
import cv2
import pytesseract
import numpy as np
from os.path import exists

from contextlib import closing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog,QApplication
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QSize, QRect
from PIL import Image
from picamera import PiCamera

about = "This is an undergraduate project developed by OYEYOADE OLUWAGBEMILEKE FEMI with matriculation number CPE/15/2461 in partial fulfilment of the requirements for the award of Bachelors in Computer Engineering"

# Captures an image of a student's ID card
def captureImage():
    camera = PiCamera()
    camera.rotation = 180
    camera.brightness = 60
    camera.resolution = (2592, 1944)
    camera.start_preview()
    sleep(5)
    camera.capture('snapshots/pix.jpg')
    camera.close()

# obtain binarized image
def obtain_grayscale(pic):
    return cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)

#Perform Optical Character Recognition on snapped image
def performOCR():
    img = Image.open('snapshots/pix.jpg')
    cvImg = cv2.imread('newpicture.jpg')
    grayed = get_grayscale(cvImg)

    text = pytesseract.image_to_string(img)
    text = pytesseract.image_to_string(grayed)
    #print(text)
    return text

# Regular expression pattern for CPE/15/2461 matric number format
test_pattern = ['[A-Z]+/[0-9]+/[0-9]+']

# Obtain matric number in OCR output
def re_find(patterns, phrase):
    for pat in patterns:
        newText = re.findall(pat,phrase)[0]
        return(re.findall(pat,phrase)[0])

# query and fetch student's info from database using 'matric number'        
def querydb(ocrMatricID):
    dbConnection = sqlite3.connect("Database/cpe.db")
    dbCursor = dbConnection.cursor()
    databaseStudentRecord = dbCursor.execute("SELECT * FROM cpe WHERE MatricNum = ?",(ocrMatricID,)).fetchall()

    studentName= databaseStudentRecord[0:1][0][0:1][0]
    studentMatric= databaseStudentRecord[0:1][0][1:2][0]
    studentLevel= databaseStudentRecord[0:1][0][2:3][0]
    studentStatus = databaseStudentRecord[0:1][0][3:4][0]
    studentDept= databaseStudentRecord[0:1][0][4:5][0]
    studentSch= databaseStudentRecord[0:1][0][5:6][0]
    studentSession= databaseStudentRecord[0:1][0][6:7][0]
    studentPicID= databaseStudentRecord[0:1][0][7:8][0]
    studentSex = databaseStudentRecord[0:1][0][8:9][0]
    return(studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex)

    with closing(sqlite3.connect("cpe.db")) as connection:
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute("SELECT 1").fetchall()

            
class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("GUI/Homepage.ui",self)
        self.captureButton.clicked.connect(self.displayBasicInfo)
        self.previewButton.clicked.connect(self.previewSnappedImage)
        self.aboutButton.clicked.connect(self.displayAbout)
        self.shutdownButton.clicked.connect(self.shutdownRaspberry)

    def previewSnappedImage(self):
        captureImage()
        self.PreviewSpace.setScaledContents(True)
        self.image = QtGui.QPixmap("snapshots/pix.jpg")
        self.PreviewSpace.setPixmap(self.image.scaled(self.PreviewSpace.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
        ocrOutput = performOCR()
        try:
            ocrMatricID=re_find(test_pattern,ocrOutput)
            self.ocrResultLabel.setText(ocrMatricID)
        except Exception:
            self.ocrResultLabel.setText("Invalid Input")

    def displayBasicInfo(self):
        try:
            self.IDName,self.IDMatric,self.IDLevel,self.IDStatus,self.IDDept,self.IDSch,self.IDSession,self.IDPicID,self.IDSex=self.retrieveDbValues()
        except Exception:
            self.PreviewSpace.setWordWrap(True)
            self.PreviewSpace.setText("Information about student is not in database")
            widget.setCurrentIndex(1)
        else:
            self.basicScreen = BasicInfoScreen()
            widget.addWidget(self.basicScreen)
            self.deleteLater()
            widget.setCurrentIndex(widget.currentIndex()+1)
            
    def displayAbout(self):
        self.PreviewSpace.setWordWrap(True)
        self.PreviewSpace.setText(about)
    
    def retrieveDbValues(self):
        ocrMatricID=re_find(test_pattern,performOCR())
        studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex=querydb(ocrMatricID)
        return(studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex)
    
    def shutdownRaspberry(self):
        print("SHUTDOWN")
        os.system("sudo shutdown -h now")

class BasicInfoScreen(QDialog):
    def __init__(self):
        super(BasicInfoScreen,self).__init__()
        loadUi("GUI/BasicInfo.ui",self)
        ocrOutput = performOCR()
        try:
            ocrMatricID=re_find(test_pattern,ocrOutput)
            print(ocrMatricID)
        except Exception:
            print("Invalid Input")
        self.IDName,self.IDMatric,self.IDLevel,self.IDStatus,self.IDDept,self.IDSch,self.IDSession,self.IDPicID,self.IDSex=self.retrieveDbValues()
        self.slotInValues()
        self.displayFullDetailsButton.clicked.connect(self.displayDetails)
        self.displayHomepageButton.clicked.connect(self.displayHome)
        
    def retrieveDbValues(self):
        ocrMatricID=re_find(test_pattern,performOCR())
        print(ocrMatricID)
        studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex=querydb(ocrMatricID)
        return(studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex)
    
    def slotInValues(self):
        self.studentName.setText(self.IDName)
        self.studentDepartment.setText(self.IDDept)
        self.studentLevel.setText(str(self.IDLevel))
        self.studentMatric.setText(self.IDMatric)
        self.studentPicture.setScaledContents(True)
        
        objpictureURI = "Images/"+self.IDPicID+".jpg"
        if (exists(objpictureURI)== True):
            pictureURI = objpictureURI
        else:
            if (self.IDSex == "MALE"):
                pictureURI="Images/boy.jpg"
            else:
                pictureURI="Images/girl.jpg"
        self.Nimage = QtGui.QPixmap(pictureURI)
        self.studentPicture.setPixmap(self.Nimage.scaled(self.studentPicture.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
        QApplication.processEvents()

    def displayDetails(self):
        self.detailsScreen = StudentDetailsScreen()
        widget.addWidget(self.detailsScreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def displayHome(self):
        self.mainScreen = MainWindow()
        widget.addWidget(self.mainScreen)
        self.deleteLater()
        widget.setCurrentIndex(widget.currentIndex() - 1)

class StudentDetailsScreen(QDialog):
    def __init__(self):
        super(StudentDetailsScreen,self).__init__()
        loadUi("GUI/details.ui",self)
        self.IDName,self.IDMatric,self.IDLevel,self.IDStatus,self.IDDept,self.IDSch,self.IDSession,self.IDPicID,self.IDSex=self.retrieveDbValues()
        self.slotInValues()
        self.basicInfoButton.clicked.connect(self.displayBasic)
        
    def retrieveDbValues(self):
        ocrMatricID=re_find(test_pattern,performOCR())
        studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex=querydb(ocrMatricID)
        return(studentName,studentMatric,studentLevel,studentStatus,studentDept,studentSch,studentSession,studentPicID,studentSex)
    
    def slotInValues(self):
        self.studentName.setText(self.IDName)
        self.studentDepartment.setText(self.IDDept)
        self.studentLevel.setText(str(self.IDLevel))
        self.studentMatric.setText(self.IDMatric)
        self.studentSchool.setText(self.IDSch)
        self.studentSession.setText(self.IDSession)
        self.studentSex.setText(self.IDSex)
        self.studentPicture.setScaledContents(True)

        objpictureURI = "Images/"+self.IDPicID+".jpg"
        if (exists(objpictureURI)== True):
            pictureURI = objpictureURI
        else:
            if (self.IDSex == "MALE"):
                pictureURI="Images/boy.jpg"
            else:
                pictureURI="Images/girl.jpg"
        self.Nimage = QtGui.QPixmap(pictureURI)
        self.studentPicture.setPixmap(self.Nimage.scaled(self.studentPicture.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def displayBasic(self):
        self.basicScreen = BasicInfoScreen()
        widget.addWidget(self.basicScreen)
        self.deleteLater()
        widget.setCurrentIndex(widget.currentIndex()-1)


# Main Application
app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

mainScreen = MainWindow()
widget.addWidget(mainScreen)

widget.setFixedHeight(400)
widget.setFixedWidth(800)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
