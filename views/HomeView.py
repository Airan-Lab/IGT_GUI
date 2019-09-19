import sys
import util.io as io
import glob
import ntpath
import util.FUS_Helper as FUS_Helper
import os

import views.LoadSeqView as LoadSeq

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, QQmlListProperty, qmlRegisterType, QQmlComponent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, pyqtProperty, QTimer
from PyQt5.QtQuick import QQuickView

#QT Object to store individual sequences
class Seq(QObject):
    nameChanged = pyqtSignal()

    def __init__(self, name='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name

    @pyqtProperty('QString', notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name != self._name:
            self._name = name
            self.nameChanged.emit()

#QT Object to store all of the ultrasound sequences


class Seq_List(QObject):
    seqsChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seqs = []

        #Scan for sequences
        io.check_folder('./Sequences')
        for fname in glob.glob('./Sequences/*.json'):
            self._seqs.append(Seq(ntpath.splitext(ntpath.basename(fname))[0]))

    @pyqtProperty(QQmlListProperty, notify=seqsChanged)
    def seqs(self):
        return QQmlListProperty(Seq, self, self._seqs)

    @seqs.setter
    def seqs(self, seqs):
        if seqs != self._seqs:
            self._seqs = seqs
            self.seqsChanged.emit()

    def appendSeq(self, new_seq):
        self._seqs.append(new_seq)
        self.seqsChanged.emit()

    def refresh_seqs(self):
        #Scan for sequences
        io.check_folder('./Sequences')
        self.seqs = []
        for fname in glob.glob('./Sequences/*.json'):
            self._seqs.append(Seq(ntpath.splitext(ntpath.basename(fname))[0]))
        
        self.seqsChanged.emit()



class Message(QObject):
    msgChanged = pyqtSignal()

    def __init__(self, msg='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msg = msg

    @pyqtProperty('QString', notify=msgChanged)
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, msg):
        if name != self._msg:
            self._msg = msg
            self.msgChanged.emit()


#QT Object to store all of the ultrasound sequences
class Message_List(QObject):
    msgsChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msgs = []

    @pyqtProperty(QQmlListProperty, notify=msgsChanged)
    def msgs(self):
        return QQmlListProperty(Seq, self, self._msgs)

    @msgs.setter
    def msgs(self, msgs):
        if msgs != self._msgs:
            self._msgs = msg
            self.msgsChanged.emit()

    def appendMsg(self, new_msg):
        self._msgs.append(Message(new_msg))
        self.msgsChanged.emit()

class HomeView:
    def __init__(self,engine,mainWindow,all_msgs,gen,stackView):
        self.engine = engine
        self.mainWindow = mainWindow
        self.all_seqs = Seq_List()
        self.all_msgs = all_msgs
        self.gen = gen
        self.stackView = stackView

        # Initialize Variables to Communicate with QML Layer
        self.engine.rootContext().setContextProperty('all_seqs', self.all_seqs)

    def load_views(self,load_seq_view,motor_view):
        self.load_seq_view = load_seq_view
        self.motor_view = motor_view


    def load(self):
        #Connect Buttons + Signals for home window
        self.connect_button = self.mainWindow.findChild(QObject, "connectButton")
        self.connect_button.clicked.connect(self.gen.connect)

        self.shutdown_button = self.mainWindow.findChild(QObject, "shutdownButton")
        self.shutdown_button.clicked.connect(self.gen.close)

        self.sequence_list = self.mainWindow.findChild(QObject, "sequencesList")

        self.load_button = self.mainWindow.findChild(QObject, "loadButton")
        self.load_button.clicked.connect(self.load_clicked)

        self.create_button = self.mainWindow.findChild(QObject, "createButton")
        self.create_button.clicked.connect(self.create_clicked)

        self.delete_button = self.mainWindow.findChild(QObject, "deleteButton")
        self.delete_button.clicked.connect(self.delete_clicked)

        self.copy_button = self.mainWindow.findChild(QObject, "copyButton")
        self.copy_button.clicked.connect(self.copy_clicked)

        self.motor_button = self.mainWindow.findChild(QObject,"motorButton")
        self.motor_button.clicked.connect(self.motor_clicked) #commented out because nothing that needs to be passed

        self.stackView.popped.connect(self.all_seqs.refresh_seqs)

        self.all_msgs.appendMsg('Hello World')

    def load_clicked(self):
        fname = self.all_seqs.seqs[self.sequence_list.property("currentIndex")].name
        try:
            self.load_seq_view.load(fname)
        except:
            self.all_msgs.appendMsg("Error loading file. Check to make sure Sequence File is formatted in JSON and valid.")

    def copy_clicked(self):
        fname = self.all_seqs.seqs[self.sequence_list.property(
            "currentIndex")].name
        try:
            self.load_seq_view.copy_file(fname)
        except:
            self.all_msgs.appendMsg(
                "Error loading file. Check to make sure Sequence File is formatted in JSON and valid.")

    def create_clicked(self):
        self.load_seq_view.create_file()
        self.all_seqs.refresh_seqs()

    def delete_clicked(self):
        fname = self.all_seqs.seqs[self.sequence_list.property(
            "currentIndex")].name
        os.remove('./Sequences/'+fname+'.json')
        self.all_seqs.refresh_seqs()

    def motor_clicked(self):
        self.motor_view.load()
        #try:
        #    self.motor_view.load()
        #except:
        #    self.all_msgs.appendMsg(
        #        "Error loading Motor View.")
