from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, QQmlListProperty, qmlRegisterType, QQmlComponent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, pyqtProperty, QTimer
from PyQt5.QtQuick import QQuickView
from PyQt5.Qt import QMetaObject
from PyQt5.QtWidgets import QMessageBox

import json
import os
import shutil

class MotorView:
    def __init__(self, engine, mainWindow, all_msgs, motor):
        self.engine = engine
        self.mainWindow = mainWindow
        self.all_msgs = all_msgs
        self.motor = motor
        self.loaded = False

    def load(self):
        if self.loaded:
            return
        self.view = self.mainWindow.findChild(QObject, "motorView")

        #Load Buttons
        self.back_button = self.mainWindow.findChild(QObject, "backButton")
        self.back_button.clicked.connect(self.view.pop)

        self.connect_motor_button = self.mainWindow.findChild(QObject, "connectMotorButton")
        self.connect_motor_button.clicked.connect(self.connect)

        self.set_zero_button = self.mainWindow.findChild(
            QObject, "setZeroButton")
        self.set_zero_button.clicked.connect(self.set_zero)

        self.goto_button = self.mainWindow.findChild(QObject, "goToButton")
        self.goto_button.clicked.connect(self.move_abs)

        self.incX_button = self.mainWindow.findChild(QObject,"incX")
        self.incX_button.clicked.connect(lambda: self.move_inc(0))

        self.incY_button = self.mainWindow.findChild(QObject,"incY")
        self.incY_button.clicked.connect(lambda: self.move_inc(1))
        
        self.incZ_button = self.mainWindow.findChild(QObject, "incZ")
        self.incZ_button.clicked.connect(lambda: self.move_inc(2))

        self.decX_button = self.mainWindow.findChild(QObject, "decX")
        self.decX_button.clicked.connect(lambda: self.move_dec(0))

        self.decY_button = self.mainWindow.findChild(QObject, "decY")
        self.decY_button.clicked.connect(lambda: self.move_dec(1))

        self.decZ_button = self.mainWindow.findChild(QObject, "decZ")
        self.decZ_button.clicked.connect(lambda: self.move_dec(2))

        #Fields
        self.xfield = self.mainWindow.findChild(QObject,"moveX")
        self.yfield = self.mainWindow.findChild(QObject,"moveY")
        self.zfield = self.mainWindow.findChild(QObject, "moveZ")
        self.inc_field = self.mainWindow.findChild(QObject,"moveBy")

        #Position Text Items
        self.xpos_text = self.mainWindow.findChild(QObject,"xPos")
        self.ypos_text = self.mainWindow.findChild(QObject,"yPos")
        self.zpos_text = self.mainWindow.findChild(QObject, "zPos")

        #Indicator lights
        self.motor_light = self.mainWindow.findChild(QObject,"motorIndicator")
        if self.motor.connected:
            self.motor_light.setProperty("color","green")
            self.enable_buttons()
        else:
            self.motor_light.setProperty("color", "red")
            self.disable_buttons()

    def connect(self):
        res = self.motor.connect()
        if self.motor.connected:
            self.motor_light.setProperty("color", "green")
            self.enable_buttons()
            self.update_position(res)
        else:
            self.motor_light.setProperty("color","red")
            self.disable_buttons()


    def update_position(self,pos_return=None):
        if pos_return is None:
            current_pos = self.motor.getPos()
        else:
            current_pos = pos_return
        self.xpos_text.setProperty("text",str(current_pos[0]))
        self.ypos_text.setProperty("text",str(current_pos[1]))
        self.zpos_text.setProperty("text",str(current_pos[2]))

    
    def set_zero(self):
        self.motor.set_zero()
        self.update_position()

    def move_abs(self):
        new_coord = [0,0,0]
        new_coord[0] = float(self.xfield.property("text"))
        new_coord[1] = float(self.yfield.property("text"))
        new_coord[2] = float(self.zfield.property("text"))

        res = self.motor.moveAbs(new_coord)
        self.update_position(res)
        #interval = float(self.inc_field.property("text"))
        #self.motor.test_move(interval)

    
    def move_inc(self,direction):
        interval = float(self.inc_field.property("text"))
        new_coord = [0,0,0]
        new_coord[direction] = interval

        res = self.motor.moveRel(new_coord)
        self.update_position(res)
        
    def move_dec(self,direction):
        interval = float(self.inc_field.property("text"))
        new_coord = [0, 0, 0]
        new_coord[direction] = -interval

        res = self.motor.moveRel(new_coord)
        self.update_position(res)

    def enable_buttons(self):
        self.set_zero_button.setProperty("enabled", True)
        self.goto_button.setProperty("enabled", True)
        self.incX_button.setProperty("enabled", True)
        self.incY_button.setProperty("enabled", True)
        self.incZ_button.setProperty("enabled", True)
        self.decX_button.setProperty("enabled", True)
        self.decY_button.setProperty("enabled", True)
        self.decZ_button.setProperty("enabled", True)

    def disable_buttons(self):
        self.set_zero_button.setProperty("enabled", False)
        self.goto_button.setProperty("enabled", False)
        self.incX_button.setProperty("enabled", False)
        self.incY_button.setProperty("enabled", False)
        self.incZ_button.setProperty("enabled", False)
        self.decX_button.setProperty("enabled", False)
        self.decY_button.setProperty("enabled", False)
        self.decZ_button.setProperty("enabled", False)
    
