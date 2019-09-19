from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, QQmlListProperty, qmlRegisterType, QQmlComponent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, pyqtProperty, QTimer
from PyQt5.QtQuick import QQuickView
from PyQt5.Qt import QMetaObject
from PyQt5.QtWidgets import QMessageBox

import json
import os
import shutil

#QT Object to store individual sequences


class PulseParam(QObject):
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


class Pulse_Param_List(QObject):
    pulsesChanged = pyqtSignal()

    def __init__(self, pulses=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pulses = []

    @pyqtProperty(QQmlListProperty, notify=pulsesChanged)
    def pulses(self):
        return QQmlListProperty(PulseParam, self, self._pulses)

    @pulses.setter
    def pulses(self, pulses):
        if pulses != self._pulses:
            self._pulses = pulses
            self.pulsesChanged.emit()

    def set_pulses(self, pulses):
        if pulses != self._pulses:
            self._pulses = pulses
            self.pulsesChanged.emit()

    def appendPulse(self, new_pulse):
        self._pulses.append(new_pulse)
        self.pulsesChanged.emit()

class LoadSeqView:
    def __init__(self,engine,mainWindow,all_msgs,gen,motor):
        self.engine = engine
        self.mainWindow = mainWindow
        self.all_msgs = all_msgs
        self.modified = False
        self.current_idx = None
        self.gen = gen
        self.motor = motor

        self.pulse_list =  Pulse_Param_List()

        # Initialize Variables to Communicate with QML Layer
        self.engine.rootContext().setContextProperty('pulse_list', self.pulse_list)
    
    def set_modified(self):
        self.modified = True
        self.saved_light.setProperty("color","red")
        self.sent_light.setProperty("color","red")
        self.run_button.setProperty("enabled",False)

    #Load the view and connect to PyQML layer
    def load(self,fname):
        self.fname = fname
        self.view = self.mainWindow.findChild(QObject,"loadSeqView")
        
        # Connect Buttons/Fields
        self.back_button = self.mainWindow.findChild(QObject, "backButton")
        self.back_button.clicked.connect(self.unload)

        self.pulse_seq_list = self.mainWindow.findChild(QObject, "pulseSeqList")
        self.pulse_seq_list.changed.connect(self.update)

        self.create_button = self.mainWindow.findChild(QObject,"newPulse")
        self.create_button.clicked.connect(self.create)

        self.delete_button = self.mainWindow.findChild(QObject, "deletePulse")
        self.delete_button.clicked.connect(self.delete)

        self.up_button = self.mainWindow.findChild(QObject, "upPulse")
        self.up_button.clicked.connect(self.move_up)

        self.down_button = self.mainWindow.findChild(QObject, "downPulse")
        self.down_button.clicked.connect(self.move_down)

        self.save_button = self.mainWindow.findChild(QObject, "saveButton")
        self.save_button.clicked.connect(self.save)

        self.reset_button = self.mainWindow.findChild(QObject, "resetButton")
        self.reset_button.clicked.connect(self.load_file)

        self.send_button = self.mainWindow.findChild(QObject, "sendButton")
        self.send_button.clicked.connect(self.send)

        self.run_button = self.mainWindow.findChild(QObject, "executeButton")
        self.run_button.clicked.connect(self.gen.run)

        # Connect the Sequence TextFields
        self.fname_field = self.mainWindow.findChild(QObject, "fileName")
        self.fname_field.setProperty("text", self.fname)

        self.text_fields = {}
        self.text_fields["Name"] = self.mainWindow.findChild(
            QObject, "pulseID")
        self.text_fields["Duration"] = self.mainWindow.findChild(
            QObject, "duration")
        self.text_fields["Delay"] = self.mainWindow.findChild(QObject, "delay")
        self.text_fields["Amplitude"] = self.mainWindow.findChild(
            QObject, "amplitude")
        self.text_fields["Frequency"] = self.mainWindow.findChild(QObject, "frequency")
        self.text_fields["MotorX"] = self.mainWindow.findChild(
            QObject, "motorX")
        self.text_fields["MotorY"] = self.mainWindow.findChild(
            QObject, "motorY")
        self.text_fields["MotorZ"] = self.mainWindow.findChild(
            QObject, "motorZ")

        self.text_fields["ExecCount"] = self.mainWindow.findChild(
            QObject, "executionCount")
        self.text_fields["SequenceDelay"] = self.mainWindow.findChild(
            QObject, "seqDelay")

        for k in self.text_fields.keys():
            #Reason for temp default variable is here: https://stackoverflow.com/questions/46300229/connecting-multiples-signal-slot-in-a-for-loop-in-pyqt
            self.text_fields[k].editingFinished.connect(lambda temp=k: self.update_param(temp))

        # Load message dialogs
        self.save_popup = self.mainWindow.findChild(QObject, "savePopup")

        # Load Indicator Lights
        self.saved_light = self.mainWindow.findChild(QObject,"saved")
        self.sent_light = self.mainWindow.findChild(QObject,"sent")
        self.gen_light = self.mainWindow.findChild(QObject,"gen")
        self.motor_light = self.mainWindow.findChild(QObject, "motor")

        if self.gen.connected:
            self.gen_light.setProperty("color","green")

        if self.motor.connected:
            self.motor_light.setProperty("color", "green")


        # Load Sequence File
        self.load_file()

    def create_file(self):
        candidate_fname = "New_Sequence"
        num = 1
        while os.path.exists("./Sequences/"+candidate_fname+".json"):
            candidate_fname = "New_Sequence_" + str(num)
            num += 1

        shutil.copyfile('./util/New_Sequence.json',
                        "./Sequences/"+candidate_fname+".json")

        self.load(candidate_fname)

    def copy_file(self,fname):
        candidate_fname = "Copy of " + fname
        num = 1
        while os.path.exists("./Sequences/"+candidate_fname+".json"):
            candidate_fname = "Copy of " + fname + '_' + str(num)
            num += 1

        shutil.copyfile('./Sequences/' + fname + '.json',
                        "./Sequences/"+candidate_fname+".json")

        self.load(candidate_fname)
        

    def load_file(self):
        path = './Sequences/'+self.fname+'.json'
        with open(path) as f:
            self.seq_data = json.load(f)

        # Load all pulses in sequence
        self.pulse_list.set_pulses([PulseParam(p["Name"]) for p in self.seq_data['Sequence']])

        self.pulse_seq_list.setProperty("currentIndex",0)
        self.update(0)

        self.text_fields['ExecCount'].setProperty("text",self.seq_data['ExecCount'])
        self.text_fields['SequenceDelay'].setProperty(
            "text", self.seq_data['SequenceDelay'])

        self.all_msgs.appendMsg('Loaded sequence file successfully')

    def update(self,idx):
        self.current_idx = idx
            
        pulse_params = self.seq_data["Sequence"][idx]
        for k in pulse_params.keys():
            self.text_fields[k].setProperty("text",pulse_params.get(k))

    def create(self):
        new_name = "Pulse #" + str(len(self.seq_data["Sequence"]))
        new_pulse = {"Name": new_name,
            "Duration": 100,
            "Delay": 900,
            "Amplitude": 20,
            "Frequency": 0.65,
            "MotorX": 0,
            "MotorY": 0,
            "MotorZ": 0
        }

        self.seq_data["Sequence"].append(new_pulse)
        self.pulse_list.appendPulse(PulseParam(new_name))

        self.pulse_seq_list.setProperty(
            "currentIndex", len(self.seq_data["Sequence"])-1)
        self.update(len(self.seq_data["Sequence"])-1)

        self.set_modified()

    def delete(self):
        if len(self.seq_data["Sequence"]) > 0:
            self.seq_data["Sequence"].pop(self.current_idx)

            self.pulse_list.set_pulses([PulseParam(p["Name"])
                                    for p in self.seq_data['Sequence']])

            new_idx = self.current_idx - 1 if self.current_idx > 0 else 0
            
            if len(self.seq_data["Sequence"]) > 0:
                self.update(new_idx)
                self.pulse_seq_list.setProperty("currentIndex",new_idx)
            self.set_modified()

    def move_up(self):
        if len(self.seq_data["Sequence"]) > 0 and self.current_idx > 0:
            new_idx = self.current_idx - 1
            pulse = self.seq_data["Sequence"].pop(self.current_idx)
            self.seq_data["Sequence"].insert(new_idx, pulse)

            self.pulse_list.set_pulses([PulseParam(p["Name"])
                                        for p in self.seq_data['Sequence']])
            self.update(new_idx)
            self.pulse_seq_list.setProperty("currentIndex", new_idx)
            self.set_modified()

    def move_down(self):
        if len(self.seq_data["Sequence"]) > 0 and self.current_idx < len(self.seq_data["Sequence"])-1:
            new_idx = self.current_idx + 1
            pulse = self.seq_data["Sequence"].pop(self.current_idx)
            self.seq_data["Sequence"].insert(new_idx, pulse)

            self.pulse_list.set_pulses([PulseParam(p["Name"])
                                        for p in self.seq_data['Sequence']])
            self.update(new_idx)
            self.pulse_seq_list.setProperty("currentIndex", new_idx)
            self.set_modified()

    def update_param(self,k):
        new_val = self.text_fields[k].property("text")
        try:
            new_val = float(new_val)
        except:
            pass
        
        if k == 'ExecCount' or k == 'SequenceDelay':
            if self.seq_data[k] != new_val:
                self.seq_data[k] = new_val
                self.set_modified()
        else:
            if self.seq_data["Sequence"][self.current_idx][k] != new_val:
                self.seq_data["Sequence"][self.current_idx][k] = new_val
                self.set_modified()

        #Need to refresh list of pulses if necessary
        if k == 'Name':
            self.pulse_list.set_pulses([PulseParam(p["Name"])
                                    for p in self.seq_data['Sequence']])
            self.pulse_seq_list.setProperty("currentIndex",self.current_idx)

    def save(self):
        new_fname = self.fname_field.property("text")
        if new_fname != self.fname:
            if os.path.isfile('./Sequences/'+new_fname+'.json'):
                self.all_msgs.appendMsg('File already exists. Choose another one!')
                return
            os.remove('./Sequences/'+self.fname+'.json')
            self.fname = new_fname
        path = './Sequences/'+self.fname+'.json'
        with open(path,'w+') as f:
            json.dump(self.seq_data, f, indent=4)
            self.all_msgs.appendMsg('Saved sequence file successfully')
        
        self.modified = False
        self.saved_light.setProperty("color","green")

    def unload(self):
        def save_close():
            self.save()
            self.view.pop()
        
        if self.modified:
            self.save_popup.yes.connect(save_close)
            self.save_popup.no.connect(self.view.pop)
            self.save_popup.open()

        else:
            self.view.pop()

    def send(self):
        def send_true(save=False):
            if save:
                self.save()
            if self.gen.connected:
                self.gen.send_traj(self.seq_data)
                self.sent_light.setProperty("color","green")
                self.run_button.setProperty("enabled",True)
            else:
                self.all_msgs.appendMsg('Generator not connected.')

        if self.modified:
            self.save_popup.yes.connect(lambda: send_true(True))
            self.save_popup.open()

        else:
            send_true()
