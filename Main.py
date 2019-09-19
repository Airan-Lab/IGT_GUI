import sys
import util.io as io
import glob
import ntpath
import util.FUS_Helper as FUS_Helper
import util.MotorXYZ as MotorXYZ

import views.LoadSeqView as LoadSeqView
import views.HomeView as HomeView
import views.MotorView as MotorView

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine,QQmlListProperty,qmlRegisterType, QQmlComponent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, pyqtProperty, QTimer
from PyQt5.QtQuick import QQuickView


if __name__ == "__main__":
    #Generate Message Dialogs
    all_msgs = HomeView.Message_List()
    motor = MotorXYZ.MotorsXYZ(all_msgs)
    gen = FUS_Helper.FUS_GEN(all_msgs,motor=motor)

    #Initialize QML Types
    qmlRegisterType(HomeView.Seq, 'IGT_GUI', 1, 0, 'Seq')
    qmlRegisterType(HomeView.Seq_List, 'IGT_GUI', 1, 0, 'Seq_List')
    qmlRegisterType(HomeView.Message,'IGT_GUI', 1, 0, 'Message')
    qmlRegisterType(HomeView.Message_List,'IGT_GUI', 1, 0, 'Message_List')

    # Activate the actual QML Application
    sys_argv = sys.argv
    sys_argv += ['--style', 'universal']
    app = QGuiApplication(sys_argv)
    engine=QQmlApplicationEngine()

    # Initialize Variables to Communicate with QML Layer
    engine.rootContext().setContextProperty('all_msgs', all_msgs)

    # Initialize the Main View
    component = QQmlComponent(engine)
    component.loadUrl(QUrl("MainWindow.qml"))

    mainWindow = component.create()
    stackView = mainWindow.findChild(QObject, "stack")

    # Generate the Views
    home_view = HomeView.HomeView(engine,mainWindow,all_msgs,gen,stackView)
    load_seq_view = LoadSeqView.LoadSeqView(engine, mainWindow, all_msgs,gen,motor)
    motor_view = MotorView.MotorView(engine,mainWindow,all_msgs,motor)

    home_view.load_views(load_seq_view,motor_view)

    # Load the home view
    home_view.load()

    

    #Timer Loop to allow for ctrl-c abortion
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    #Cleanup for quitting
    def app_quit():
        if gen.connected:
            gen.close()
        if motor.connected:
            motor.close_com()

        app.quit()

    engine.quit.connect(app_quit)
    sys.exit(app.exec_())
