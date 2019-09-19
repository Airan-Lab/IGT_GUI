import QtQuick 2.0
import QtQuick.Controls 2.4
import QtQuick.Controls.Universal 2.1
import QtQuick.Layouts 1.3
import QtQuick.Extras 1.4
import QtQuick.Dialogs 1.1

Item{
    id: loadSeq
    objectName: "loadSeqView"

    function pop() {
        stack.pop();
        stack.popped();
        return 0;
    }

    MouseArea {id: fullWindow
        anchors.fill: parent
        onPressed: fullWindow.forceActiveFocus()
    }
    GridLayout {
        id: gridLayout
        columnSpacing: 10
        columns: 2
        anchors.rightMargin: 20
        anchors.leftMargin: 20
        anchors.bottomMargin: 20
        anchors.topMargin: 20
        anchors.fill: parent



        ColumnLayout {
            id: columnLayout1
            width: 100
            height: 100
            Layout.preferredWidth: 200
            RowLayout {
                id: rowLayout
                width: 100
                height: 100

                Button {
                    id: back
                    icon.source: "Img/Back.png"
                    objectName: "backButton"
                    width: 50
                    height: 50
                    text: qsTr("Button")
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                    Layout.preferredHeight: 50
                    Layout.preferredWidth: 50
                    Layout.fillHeight: false
                    display: AbstractButton.IconOnly
                }

                Text {
                    id: text3
                    text: qsTr("Name: ")
                    font.pixelSize: 16
                    color: "white"
                }

                TextField {
                    id: fileName
                    objectName: "fileName"
                    text: qsTr("File Name")
                    placeholderText: qsTr("")
                    Layout.fillWidth: true
                    selectByMouse: true
                }
            }


            Rectangle {
                id: header
                color: "#000000"
                Layout.preferredHeight: 20
                Layout.fillWidth: true
                Text {
                    id: text1
                    color: "#ffffff"
                    text: qsTr("Pulse Sequence")
                    Layout.fillHeight: false
                    font.pixelSize: 16
                }
                Layout.minimumHeight: 10
                z: 1
                Layout.fillHeight: false
            }



            GridLayout {
                id: gridLayout3
                width: 100
                height: 100
                Layout.fillHeight: true
                columns: 2
                Layout.fillWidth: true

                ListView {
                    signal changed(int idx)
                    Layout.fillWidth: true
                    id: pulseSeqList
                    objectName: "pulseSeqList"
                    Layout.preferredWidth: 280
                    ScrollBar.vertical: ScrollBar {
                    }
                    Layout.columnSpan: 1
                    Layout.rowSpan: 4
                    z: -1
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                    Layout.fillHeight: true
                    transformOrigin: Item.Top
                    model: pulse_list.pulses
                    delegate: ItemDelegate {
                        width: parent.width
                        text: name
                        highlighted: ListView.isCurrentItem
                        onClicked: {
                            pulseSeqList.currentIndex = index;
                            pulseSeqList.forceActiveFocus();
                            pulseSeqList.changed(index)
                        }
                    }
                    Layout.preferredHeight: 217
                }

                Button {
                    id: newPulse
                    objectName: "newPulse"
                    text: qsTr("Button")
                    display: AbstractButton.IconOnly
                    icon.source: "Img/Create.png"
                    icon.color: "transparent"
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 40
                }

                Button {
                    id: deletePulse
                    text: qsTr("Button")
                    Layout.preferredHeight: 40
                    icon.color: "#00000000"
                    Layout.preferredWidth: 40
                    display: AbstractButton.IconOnly
                    icon.source: "Img/Delete.png"
                    objectName: "deletePulse"
                }

                Button {
                    id: upPulse
                    text: qsTr("Button")
                    icon.color: "#00000000"
                    Layout.preferredHeight: 40
                    display: AbstractButton.IconOnly
                    Layout.preferredWidth: 40
                    icon.source: "Img/Up.png"
                    objectName: "upPulse"
                }

                Button {
                    id: downPulse
                    text: qsTr("Button")
                    icon.color: "#00000000"
                    Layout.preferredHeight: 40
                    display: AbstractButton.IconOnly
                    Layout.preferredWidth: 40
                    icon.source: "Img/Down.png"
                    objectName: "downPulse"
                }
            }




            Rectangle {
                id: header1
                height: 20
                color: "#000000"
                Layout.fillWidth: true
                Layout.minimumHeight: 20
                Layout.fillHeight: false
            }




            Layout.rowSpan: 6
            spacing: 10
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillHeight: true


            GridLayout {
                id: gridLayout1
                width: 100
                height: 100
                columns: 2

                Text {
                    id: text10
                    color: "#ffffff"
                    text: "Pulse ID"
                    font.pixelSize: 12
                }

                TextField {
                    id: pulseID
                    text: qsTr("Pulse ID")
                    objectName: "pulseID"
                    Layout.fillWidth: true
                    selectByMouse: true
                }

                Text {
                    id: text4
                    color: "white"
                    text: "Duration (ms)"
                    font.pixelSize: 12
                }



                TextField {
                    id: duration
                    objectName: "duration"
                    text: qsTr("")
                    selectByMouse: true
                    Layout.fillWidth: true
                    validator: DoubleValidator{bottom: 0}
                }






                Text {
                    id: text5
                    color: "white"
                    text: "Delay (ms)"
                    font.pixelSize: 12
                }



                TextField {
                    id: delay
                    objectName: "delay"
                    text: qsTr("")
                    selectByMouse: true
                    Layout.fillWidth: true
                    validator: DoubleValidator{bottom: 0}
                }






                Text {
                    id: text6
                    color: "white"
                    text: "Amplitude (%)"
                    font.pixelSize: 12
                }






                TextField {
                    id: amplitude
                    objectName: "amplitude"
                    selectByMouse: true
                    Layout.fillWidth: true
                    validator: DoubleValidator{
                        bottom: 0
                        top: 100
                    }
                }







                Text {
                    id: text7
                    color: "white"
                    text: "Frequency (MHz)"
                    font.pixelSize: 12
                }



                TextField {
                    id: frequency
                    objectName: "frequency"
                    selectByMouse: true
                    Layout.fillWidth: true
                    validator: DoubleValidator{bottom: 0}
                }


                Text {
                    id: text15
                    color: "#ffffff"
                    text: "Move X (After Pulse) mm)"
                    font.pixelSize: 12
                }

                TextField {
                    id: motorX
                    text: qsTr("")
                    objectName: "motorX"
                    validator: DoubleValidator {
                        bottom: 0
                    }
                    Layout.fillWidth: true
                    selectByMouse: true
                }

                Text {
                    id: text16
                    color: "#ffffff"
                    text: "Move Y (After Pulse) mm)"
                    font.pixelSize: 12
                }

                TextField {
                    id: motorY
                    text: qsTr("")
                    objectName: "motorY"
                    validator: DoubleValidator {
                        bottom: 0
                    }
                    Layout.fillWidth: true
                    selectByMouse: true
                }

                Text {
                    id: text17
                    color: "#ffffff"
                    text: "Move Z (After Pulse) mm)"
                    font.pixelSize: 12
                }

                TextField {
                    id: motorZ
                    text: qsTr("")
                    objectName: "motorZ"
                    validator: DoubleValidator {
                        bottom: 0
                    }
                    Layout.fillWidth: true
                    selectByMouse: true
                }







            }

        }

        ColumnLayout {
            id: columnLayout
            width: 100
            height: 100
            Layout.preferredWidth: 150

            Text {
                id: gen
                color: "#ffffff"
                text: qsTr("Sequence Control")
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                font.pixelSize: 16
            }


            Button {
                id: rename
                width: 150
                text: qsTr("Reset")
                Layout.preferredWidth: 150
                icon.source: "Img/Revert.png"
                objectName: "resetButton"
            }

            Button {
                id: save
                width: 150
                text: qsTr("Save")
                Layout.preferredWidth: 150
                icon.source: "Img/Save.png"
                objectName: "saveButton"
            }

            Button {
                id: send
                width: 150
                text: qsTr("Send")
                Layout.preferredWidth: 150
                icon.source: "Img/Send.png"
                objectName: "sendButton"
            }




            Button {
                id: execute
                width: 150
                text: qsTr("Execute")
                icon.color: "#00000000"
                Layout.preferredWidth: 150
                icon.source: "Img/Execute.png"
                objectName: "executeButton"
                enabled: false
            }




            Button {
                id: stop
                text: qsTr("Stop")
                Layout.preferredWidth: 150
                icon.source: "Img/Stop.png"
                icon.color: "#00000000"
                objectName: "stopButton"
            }



            Layout.alignment: Qt.AlignRight | Qt.AlignBottom
        }


        GridLayout {
            id: indicatorGrid
            width: 100
            height: 100
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            columnSpacing: 20
            Layout.fillWidth: true
            flow: GridLayout.TopToBottom
            rows: 2

            Text {
                id: text11
                text: qsTr("Saved")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
                color: "white"
            }

            StatusIndicator {
                id: savedIndicator
                objectName: "saved"
                active: true
                color: "green"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            }

            Text {
                id: text12
                color: "#ffffff"
                text: qsTr("Sent")
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            }

            StatusIndicator {
                id: sentIndicator
                objectName: "sent"
                active: true
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            }

            Text {
                id: text13
                color: "#ffffff"
                text: qsTr("Generator")
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            }

            StatusIndicator {
                id: genIndicator
                objectName: "gen"
                active: true
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            }

            Text {
                id: text14
                color: "#ffffff"
                text: qsTr("Motor")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
            }

            StatusIndicator {
                id: motorIndicator
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                objectName: "motor"
                active: true
            }
        }

        GridLayout {
            id: gridLayout2
            width: 100
            height: 100
            Layout.fillWidth: true
            Text {
                id: text8
                color: "#ffffff"
                text: "Executions"
                font.pixelSize: 12
            }

            TextField {
                id: executionCount
                text: qsTr("")
                objectName: "executionCount"
                selectByMouse: true
                Layout.fillWidth: true
                validator: IntValidator{bottom: 1}
            }

            Text {
                id: text9
                color: "#ffffff"
                text: "Seq Delay (ms)"
                font.pixelSize: 12
            }

            TextField {
                id: seqDelay
                objectName: "seqDelay"
                text: qsTr("")
                selectByMouse: true
                Layout.fillWidth: true
                validator: DoubleValidator{bottom: 0}
            }

            columns: 2
        }


        ColumnLayout {
            id: columnLayout2
            Layout.fillHeight: true
            Text {
                id: text2
                color: "#ffffff"
                text: qsTr("Console")
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                font.pixelSize: 16
            }

            Rectangle {
                id: rectangle
                color: "#ffffff"
                Layout.fillHeight: true
                ListView {
                    id: messages
                    objectName: "messages"
                    Layout.rowSpan: 1
                    ScrollBar.vertical: ScrollBar {
                    }
                    Layout.columnSpan: 1
                    anchors.fill: parent
                    Layout.preferredWidth: 300
                    model: all_msgs.msgs
                    transformOrigin: Item.Top
                    delegate: TextEdit {
                        text: msg + '\n'
                        anchors.right: parent.right
                        anchors.leftMargin: 1
                        anchors.rightMargin: 10
                        wrapMode: Text.WordWrap
                        anchors.left: parent.left
                        readOnly: true
                        selectByMouse: true
                    }
                    z: 0
                    flickableDirection: Flickable.AutoFlickDirection
                    Layout.preferredHeight: 217
                    onCountChanged: {
                        messages.currentIndex = count - 1
                    }
                }
                Layout.fillWidth: true
                z: -4
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
            }
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignRight | Qt.AlignTop
        }



    }

    MessageDialog {
        id: savePopup
        objectName: "savePopup"
        title: "Save Sequence?"
        icon: StandardIcon.Question
        text: "Sequence is not Saved. Would you like to save your work?"
        standardButtons: StandardButton.Yes | StandardButton.No
    }
}

/*##^## Designer {
    D{i:0;autoSize:true;height:640;width:640}
}
 ##^##*/
