import QtQuick 2.0
import QtQuick.Controls 2.4
import QtQuick.Controls.Universal 2.1
import QtQuick.Layouts 1.3

Item{
    id: home
    objectName: "home"
    GridLayout {
        id: gridLayout
        objectName: "homeGrid"
        x: 20
        y: 20
        anchors.rightMargin: 20
        anchors.leftMargin: 20
        anchors.bottomMargin: 20
        anchors.topMargin: 20
        columnSpacing: 8
        rowSpacing: 15
        rows: 3
        columns: 2
        anchors.fill: parent

        ColumnLayout {
            id: columnLayout1
            width: 100
            height: 100
            spacing: 10
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillHeight: true
            Layout.rowSpan: 3

            Rectangle{
                id: header
                width: 300
                color: "black"
                z: 1
                Layout.minimumHeight: 10
                Layout.fillHeight: true
                Text {
                    id: text1
                    text: qsTr("Sequences Found")
                    Layout.fillHeight: false
                    font.pixelSize: 16
                    color: "white"
                }
            }

            ListView {
                id: sequencesList
                objectName: "sequencesList"
                z: -1
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignLeft | Qt.AlignBottom

                Layout.rowSpan: 1
                Layout.columnSpan: 1
                transformOrigin: Item.Top
                Layout.preferredHeight: 217
                Layout.preferredWidth: 300
                delegate: ItemDelegate {
                    text: name
                    width: parent.width
                    highlighted: ListView.isCurrentItem
                    onClicked: sequencesList.currentIndex = index
                }
                model: all_seqs.seqs
                ScrollBar.vertical: ScrollBar {}
            }

            Rectangle {
                id: header1
                width: 300
                height: 20
                color: "#000000"
                Layout.minimumWidth: 300
                Layout.fillHeight: false
                Layout.minimumHeight: 20
            }

        }

        Column {
            id: column
            width: 115
            height: 400
            Layout.alignment: Qt.AlignRight | Qt.AlignTop
            Layout.minimumWidth: 150
            spacing: 5

            Text {
                id: sequences
                text: qsTr("Sequences")
                anchors.right: parent.right
                anchors.rightMargin: 0
                color: "white"
                font.pixelSize: 16
            }

            Button {
                id: load_seq
                width: 150
                objectName: "loadButton"
                text: qsTr("Load")
                icon.source: "Img/Load.png"
                onClicked: stack.push(Qt.resolvedUrl('Load_Sequence.qml'))
            }


            Button {
                id: create_seq
                objectName: "createButton"
                width: 150
                text: qsTr("Create")
                icon.color: "transparent"
                icon.source: "Img/Create.png"
                onClicked: stack.push(Qt.resolvedUrl('Load_Sequence.qml'))
            }


            Button {
                id: copy_seq
                objectName: "copyButton"
                width: 150
                text: qsTr("Copy")
                icon.source: "Img/Copy.png"
                onClicked: stack.push(Qt.resolvedUrl('Load_Sequence.qml'))
            }

            Button {
                id: delete_seq
                objectName: "deleteButton"
                width: 150
                text: qsTr("Delete")
                icon.color: "transparent"
                icon.source: "Img/Delete.png"
            }



        }


        ColumnLayout {
            id: columnLayout
            width: 100
            height: 100
            Layout.preferredWidth: 150
            Layout.alignment: Qt.AlignRight | Qt.AlignBottom

            Text {
                id: gen
                text: qsTr("Generator")
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                color: "white"
                font.pixelSize: 16
            }

            Button {
                id: connect
                objectName: "connectButton"
                width: 150
                text: qsTr("Connect")
                Layout.preferredWidth: 150
                icon.source: "Img/Connect.png"
            }


            Button {
                id: shutdown
                objectName:"shutdownButton"
                width: 150
                text: qsTr("Shutdown")
                icon.color: "transparent"
                icon.source: "Img/Shutdown.png"
                Layout.preferredWidth: 150
            }


            Button {
                id: target
                text: qsTr("Motor")
                objectName: "motorButton"
                Layout.preferredWidth: 150
                icon.source: "Img/target.png"
                onClicked: stack.push(Qt.resolvedUrl('Motor.qml'))
            }

        }

        ColumnLayout {
            id: columnLayout2
            width: 100
            height: 100
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter

            Text {
                id: text2
                text: qsTr("Console")
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                font.pixelSize: 16
                color: "white"
            }

            Rectangle {
                id: rectangle
                color: "#ffffff"
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                Layout.fillWidth: true
                Layout.fillHeight: true
                z: -4

                ListView {
                    id: messages
                    flickableDirection: Flickable.AutoFlickDirection
                    anchors.fill: parent
                    z: 0


                    Layout.rowSpan: 1
                    Layout.columnSpan: 1
                    transformOrigin: Item.Top
                    Layout.preferredHeight: 217
                    Layout.preferredWidth: 300

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

                    model: all_msgs.msgs
                    ScrollBar.vertical: ScrollBar {}
                    onCountChanged: {
                        messages.currentIndex = count - 1
                    }
                }
            }

        }









    }
}
/*##^## Designer {
    D{i:0;autoSize:true;height:640;width:640}
}
 ##^##*/
