import QtQuick 2.0
import QtQuick.Controls 2.4
import QtQuick.Controls.Universal 2.1
import QtQuick.Layouts 1.3
import QtQuick.Extras 1.4
import QtQuick.Dialogs 1.1

Item{
    id: motor
    objectName: "motorView"

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
        rowSpacing: 10
        columnSpacing: 10
        columns: 2
        anchors.rightMargin: 20
        anchors.leftMargin: 20
        anchors.bottomMargin: 20
        anchors.topMargin: 20
        anchors.fill: parent




        RowLayout {
            id: rowLayout
            width: 100
            height: 100
            Layout.columnSpan: 2

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
                id: text1
                color: "#ffffff"
                text: qsTr("Motor Control")
                font.pixelSize: 20
            }
        }

        RowLayout {
            id: connectButtons
            Layout.preferredWidth: 600
            spacing: 15
            Layout.fillHeight: false
            Layout.fillWidth: true
            Layout.columnSpan: 2

            Button {
                id: connect
                objectName: "connectMotorButton"
                width: 150
                text: qsTr("Connect")
                Layout.preferredWidth: 150
                icon.source: "Img/Connect.png"
            }

            Button {
                id: setzero
                text: qsTr("Set/Go to Zero")
                objectName: "setZeroButton"
                Layout.preferredWidth: 150
                icon.source: "Img/Home.png"
            }

            GridLayout {
                id: indicatorGrid
                width: 100
                height: 100
                Layout.preferredWidth: -1
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                columnSpacing: 20
                Layout.fillWidth: true
                flow: GridLayout.TopToBottom
                rows: 2

                Text {
                    id: text14
                    color: "#ffffff"
                    text: qsTr("Connected")
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    font.pixelSize: 12
                }

                StatusIndicator {
                    id: motorIndicator
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    objectName: "motorIndicator"
                    active: true
                }
            }
        }



        GridLayout {
            id: gotoGrid
            width: 100
            height: 100
            Layout.columnSpan: 2
            rows: 2
            Layout.fillWidth: true



            Text {
                id: xLabel
                color: "#ffffff"
                text: "X"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
            }





            Text {
                id: yLabel
                color: "#ffffff"
                text: "Y"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
            }




            Text {
                id: zLabel
                color: "#ffffff"
                text: "Z"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
            }


            Text {
                id: spacer
                color: "#ffffff"
                text: ""
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 12
            }



            TextField {
                id: moveX
                text: qsTr("0")
                objectName: "moveX"
                selectByMouse: true
                Layout.fillWidth: true
                validator: DoubleValidator{}
            }











            TextField {
                id: moveY
                objectName: "moveY"
                text: qsTr("0")
                selectByMouse: true
                Layout.fillWidth: true
                validator: DoubleValidator{}
            }








            TextField {
                id: moveZ
                text: qsTr("0")
                validator: DoubleValidator {}
                Layout.fillWidth: true
                selectByMouse: true
                objectName: "moveZ"
            }


            columns: 4

            Button {
                id: goTo
                width: 150
                text: qsTr("Go To")
                Layout.rowSpan: 1
                Layout.columnSpan: 1
                icon.source: "Img/GoTo.png"
                Layout.preferredWidth: 150
                objectName: "goToButton"
            }

        }




        GridLayout {
            id: incrementGrid
            width: 100
            height: 100
            Layout.fillHeight: false
            Layout.fillWidth: false
            columnSpacing: 5
            rowSpacing: 5
            rows: 5
            columns: 6


            //ROW 0
            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            Text {
                id: yIncrement
                color: "#ffffff"
                text: qsTr("Y")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            Text {
                id: zIncrement
                color: "#ffffff"
                text: qsTr("Z")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            //ROW 1
            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            Button {
                id: incY
                objectName: "incY"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                focusPolicy: Qt.NoFocus
                display: AbstractButton.IconOnly
                icon.source: "Img/Up.png"
                icon.color: "transparent"
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            Button {
                id: decZ
                objectName: "decZ"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                display: AbstractButton.IconOnly
                icon.source: "Img/Up.png"
                icon.color: "transparent"
            }

            Text {
                id: moveBy
                color: "#ffffff"
                text: qsTr("Move by (mm)")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            //ROW 2
            Text {
                id: xIncrement
                color: "#ffffff"
                text: qsTr("X")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }


            Button {
                id: decX
                objectName: "decX"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                display: AbstractButton.IconOnly
                icon.source: "Img/Left.png"
                icon.color: "transparent"
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            Button {
                id: incX
                objectName: "incX"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                display: AbstractButton.IconOnly
                icon.source: "Img/Right.png"
                icon.color: "transparent"
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            TextField {
                id: moveByField
                text: qsTr("5")
                objectName: "moveBy"
                selectByMouse: true
                Layout.fillWidth: true
                validator: DoubleValidator{bottom: 0}
            }



            //ROW 3
            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

            Button {
                id: decY
                objectName: "decY"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                focusPolicy: Qt.NoFocus
                display: AbstractButton.IconOnly
                icon.source: "Img/Down.png"
                icon.color: "transparent"
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }


            Button {
                id: incZ
                objectName: "incZ"
                text: qsTr("Button")
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                display: AbstractButton.IconOnly
                icon.source: "Img/Down.png"
                icon.color: "transparent"
            }

            Item {
                // spacer item
                Layout.fillWidth: true
                Layout.fillHeight: true
                // to visualize the spacer
            }

        }

        GridLayout {
            id: positionGrid
            width: 100
            height: 100
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            columnSpacing: 5
            columns: 2


            Text {
                id: element
                color: "#ffffff"
                text: qsTr("Current Position")
                Layout.columnSpan: 2
                font.bold: true
                font.underline: true
                font.pixelSize: 16
            }

            Text {
                id: xText
                color: "#ffffff"
                text: qsTr("X: ")
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Text {
                id: xPos
                objectName: "xPos"
                color: "#ffffff"
                text: qsTr("0")
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Text {
                id: yText
                color: "#ffffff"
                text: qsTr("Y:")
                lineHeight: 1
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Text {
                id: yPos
                objectName: "yPos"
                color: "#ffffff"
                text: qsTr("0")
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Text {
                id: zText
                color: "#ffffff"
                text: qsTr("Z:")
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }

            Text {
                id: zPos
                objectName: "zPos"
                color: "#ffffff"
                text: qsTr("0")
                font.pixelSize: 16
                font.underline: false
                font.bold: false
                Layout.columnSpan: 1
            }
        }




        ColumnLayout {
            id: consoleGrid
            x: -3
            y: 8
            Layout.columnSpan: 2
            Text {
                id: text2
                color: "#ffffff"
                text: qsTr("Console")
                font.pixelSize: 16
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            }

            Rectangle {
                id: rectangle
                color: "#ffffff"
                ListView {
                    id: messages
                    Layout.preferredWidth: 300
                    flickableDirection: Flickable.AutoFlickDirection
                    z: 0
                    delegate: TextEdit {
                        text: msg + '\n'
                        anchors.right: parent.right
                        wrapMode: Text.WordWrap
                        anchors.leftMargin: 1
                        readOnly: true
                        anchors.left: parent.left
                        anchors.rightMargin: 10
                        selectByMouse: true
                    }
                    Layout.preferredHeight: 217
                    model: all_msgs.msgs
                    transformOrigin: Item.Top
                    ScrollBar.vertical: ScrollBar {
                    }
                    anchors.fill: parent
                    Layout.rowSpan: 1
                    Layout.columnSpan: 1
                    objectName: "messages"
                    onCountChanged: {
                        messages.currentIndex = count - 1
                    }
                }
                z: -4
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                Layout.fillWidth: true
                Layout.fillHeight: true

            }
            Layout.alignment: Qt.AlignRight | Qt.AlignTop
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

}


































































































































































































































/*##^## Designer {
    D{i:0;autoSize:true;height:640;width:640}
}
 ##^##*/
