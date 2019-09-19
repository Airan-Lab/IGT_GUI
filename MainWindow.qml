import QtQuick 2.0
import QtQuick.Controls 2.4
import QtQuick.Controls.Universal 2.1
import QtQuick.Layouts 1.3

//import IGT_GUI 1.0

ApplicationWindow{
    visible: true
    width: 640
    height: 640
    title: qsTr("IGT Control System")

    Universal.theme: Universal.Dark
    //Universal.accent: Universal.Violet
    id: mainwindowview
    objectName: "mainviewwindow"

    StackView {
        signal popped()
        id: stack
        objectName: "stack"
        anchors.fill: parent
        initialItem: {item: Qt.resolvedUrl("Home.qml")}
    }
}
