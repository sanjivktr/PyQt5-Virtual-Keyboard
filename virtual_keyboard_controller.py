""" ui module
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import threading
import time


class KeyButton(QtWidgets.QPushButton):
    """ KeyButton class to be used by AlphaNeumericVirtualKeyboard class
    """
    key_button_clicked_signal = QtCore.pyqtSignal(str)

    def __init__(self, key, parent=None):
        """ KeyButton class constructor

        Parameters
        ----------
        key : str
            key of the button
        parent : QWidget, optional
            Parent widget (the default is None)
        """
        super(KeyButton, self).__init__(parent)
        self._key = key
        self.set_key(key)
        self.clicked.connect(self.emit_key)
        if key == "Backspace":
            self.setStyleSheet("QPushButton {min-width: 100px;font-size: 20px; font-family: Noto Sans CJK JP;max-width: 200px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        elif key == "  ":
            self.setStyleSheet("QPushButton {min-width: 100px;font-size: 20px;font-family: Noto Sans CJK JP; max-width: 200px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        elif key == " ":
            self.setStyleSheet("QPushButton {min-width: 450px;font-size: 20px;font-family: Noto Sans CJK JP; max-width: 550px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        else:
            self.setStyleSheet("QPushButton {min-width: 80px;font-size: 20px;font-family: Noto Sans CJK JP; max-width: 80px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def set_key(self, key):
        """ KeyButton class method to set the key and text of button

        Parameters
        ----------
        key : str
            key of the button
        """
        self._key = key
        if key == ' ':
            self.setText('Space')
            # self.resize(300, 60)
        elif key == '  ':
            self.setText('Enter')
        else:
            self.setText(key)

    def emit_key(self):
        """ KeyButton class method to return key as a qt signal
        """
        self.key_button_clicked_signal.emit(str(self._key))

    def sizeHint(self):
        """ KeyButton class method to return size

        Returns
        -------
        QSize
            Size of the created button
        """
        return QtCore.QSize(80, 80)

    def keyDisabled(self, flag):
        self.setDisabled(flag)


class AlphaNeumericVirtualKeyboard(QtWidgets.QWidget):
    """ AlphaNeumericVirtualKeyboard class
    """
    def __init__(self, source, x_pos=0, y_pos=0, parent=None):
        """ AlphaNeumericVirtualKeyboard class constructor

        Parameters
        ----------
       source : QLineEdit
            lineedit to which characters will be added
        x_pos : int, optional
            X position of the keypad pop up (the default is 0)
        y_pos : int, optional
            Y position of the keypad pop up (the default is 0)
        parent : QWidget, optional
            Parent widget (the default is None)
        """
        super(AlphaNeumericVirtualKeyboard, self).__init__(parent)

        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.capsLock = 1
        self.numberOnly = 2
        self.fractionNumber = 3
        self.constraint = 0
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.source = source
        self.parent = parent
        self.moveUp = False
        # self.global_layout = QtWidgets.QVBoxLayout(parent)
        self.keys_layout = QtWidgets.QGridLayout(self)
        self.isBackKeyPressed = False
        self.threadPool = QtCore.QThreadPool()
        self.keyPressHandler = None
        self.backSpaceSignal = BackSpaceSignal()
        self.animationSignal = signalAnimation()
        self.animationSignalForClose = signalAnimation()
        self.callback_method = None
        self.back_button = KeyButton("Backspace", self)
        self.caps_button = KeyButton("Caps", self)
        self.sym_button = KeyButton("?!@#", self)
        self.close_button = KeyButton("Close", self)
        self.sym_state = False
        self.caps_state = False
        self.isHidden = True
        self.close_ui_scroll = None
        self.key_list_by_lines_lower = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '.'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', 'Backspace'],
        ['Caps', ' ', 'Sym', 'Close', '  ']]

        self.key_list_by_lines_caps = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '.'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', 'Backspace'],
        ['Caps', ' ', 'Sym', 'Close' , '  ']]

        self.key_list_by_lines_sym = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['~', '`', '@', '#', '$', '%', '^', '&&', '*', '('],
        [')', '_', '-', '+', '=', '|', '[', ']', '{', "'"],
        ['}', '"', '<', '>', '?', '/', '\\', '!', 'Backspace'],
        ['Caps', ' ', 'Sym', 'Close', '  ']]

        self.array_buttons = [[0 for x in range(10)] for y in range(5)]

    def convert_to_caps(self):
        """ AlphaNeumericVirtualKeyboard class method to convert keys between upper and lower case
        """
        keys = None
        if not self.caps_state:
            self.caps_state = 1
            self.sym_state = 0
            keys = self.key_list_by_lines_caps
            self.caps_button.setStyleSheet("background-color:rgb(29, 150, 255);font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px; min-height:42px; max-height: 42px; width: 120px;")
        else:
            self.caps_state = 0
            keys = self.key_list_by_lines_lower
            self.caps_button.setStyleSheet("QPushButton {font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);min-height:42px; max-height: 42px; width: 120px;}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        for lineIndex, line in enumerate(keys):
            for keyIndex, key in enumerate(line):
                if key != ' ' and key != '  'and key != 'Backspace' and key != 'CAPS' and key != 'Close' and key != 'Sym':
                    button = self.array_buttons[lineIndex][keyIndex]
                    button.setText(key)
        self.sym_button.setStyleSheet("QPushButton {font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);min-height:42px; max-height: 42px; width: 120px;}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        self.sym_state = 0

    def hide(self, animation=False):
        QtWidgets.QWidget.hide(self)
        self.isHidden = True

    def open_symbol(self):
        keys = None
        if not self.sym_state:
            self.sym_state = 1
            keys = self.key_list_by_lines_sym
            self.sym_button.setStyleSheet("background-color:rgb(29, 150, 255);font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px; min-height:42px; max-height: 42px; width: 120px;")
        elif self.caps_state:
            self.sym_state = 0
            keys = self.key_list_by_lines_caps
            self.sym_button.setStyleSheet("QPushButton {font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);min-height:42px; max-height: 42px; width: 120px;}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        else:
            self.sym_state = 0
            keys = self.key_list_by_lines_lower
            self.sym_button.setStyleSheet("QPushButton {font-size: 20px;font-family: Noto Sans CJK JP;border: 3px solid #8f8f91;border-radius: 8px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);min-height:42px; max-height: 42px; width: 120px;}\nQPushButton:pressed {background-color: rgb(29, 150, 255);}")
        for lineIndex, line in enumerate(keys):
            for keyIndex, key in enumerate(line):
                if key != ' ' and key != '  ' and key != 'Backspace' and key != 'Caps' and key != 'Close' and key != 'Sym':
                    button = self.array_buttons[lineIndex][keyIndex]
                    button.setText(key)

    def display(self, source=None, event=None, ui_Scroll=None, closeButtonEnable=False, call_back=None, constraint=0, moveUp=False):
        """ AlphaNeumericVirtualKeyboard class method to display virtual keypad

        Parameters
        ----------
        source : QLineEdit
            lineedit to which characters will be added
        x_pos : int, optional
            X position of the keypad pop up (the default is 0)
        y_pos : int, optional
            Y position of the keypad pop up (the default is 0)
        """
        x_pos = 420
        y_pos = 700
        self.moveUp = moveUp
        if ui_Scroll:
            self.close_ui_scroll = ui_Scroll
            ui_Scroll.show()
        if self.isHidden:
            for lineIndex, line in enumerate(self.key_list_by_lines_lower):
                for keyIndex, key in enumerate(line):
                    if isinstance(self.array_buttons[lineIndex][keyIndex], KeyButton):
                        continue
                    if key == ' ':
                        button = KeyButton(key, self.parent)
                        self.array_buttons[lineIndex][keyIndex] = button
                        self.keys_layout.addWidget(button, lineIndex, keyIndex, 1, 5)
                        button.key_button_clicked_signal.connect(lambda key: self.add_input_by_key(key))
                    elif key == '  ':
                        button = KeyButton(key, self.parent)
                        self.array_buttons[lineIndex][keyIndex] = button
                        self.keys_layout.addWidget(button, lineIndex, 8, 1, 2)
                        button.key_button_clicked_signal.connect(lambda key: self.add_input_by_key(key))
                    elif key == 'Backspace':
                        self.array_buttons[lineIndex][keyIndex] = self.back_button
                        self.keys_layout.addWidget(self.back_button, lineIndex, keyIndex, 1, 2)
                        self.backSpaceSignal.signal.connect(self.backspace)
                        self.back_button.mousePressEvent = self.backspacePressEvent
                        self.back_button.mouseReleaseEvent = self.backspaceReleaseEvent
                        self.back_button.mouseDoubleClickEvent = self.backsapceDoubleClick
                    elif key == 'Caps':
                        self.array_buttons[lineIndex][keyIndex] = self.caps_button
                        self.keys_layout.addWidget(self.caps_button, lineIndex, keyIndex)
                        self.caps_button.key_button_clicked_signal.connect(self.convert_to_caps)
                        if self.caps_state == 1:
                            self.caps_button.setStyleSheet("background-color:rgb(29, 150, 255);border: 3px solid #8f8f91;border-radius: 8px; min-height:42px; max-height: 42px; width: 120px;")
                    elif key == 'Close':
                        self.array_buttons[lineIndex][keyIndex] = self.close_button
                        self.keys_layout.addWidget(self.close_button, lineIndex, 7)
                        self.close_button.key_button_clicked_signal.connect(self.close_handler)
                    elif key == 'Sym':
                        self.array_buttons[lineIndex][keyIndex] = self.sym_button
                        self.keys_layout.addWidget(self.sym_button, lineIndex, 6)
                        self.sym_button.key_button_clicked_signal.connect(self.open_symbol)
                        if self.sym_state == 1:
                            self.sym_button.setStyleSheet("background-color:rgb(29, 150, 255);border: 3px solid #8f8f91;border-radius: 8px;min-height:42px; max-height: 42px; width: 120px;")
                    else:
                        button = KeyButton(key, self.parent)
                        self.array_buttons[lineIndex][keyIndex] = button
                        self.keys_layout.addWidget(button, lineIndex, keyIndex)
                        button.key_button_clicked_signal.connect(lambda key: self.add_input_by_key(key))

            # self.global_layout.addLayout(self.keys_layout)
            self.move(self.x_pos, self.y_pos * 2)
            self.show()
            self.animationSignal.signal.connect(self.showAnimate)
            animate = AnimationThread(self.animationSignal.signal, self)
            animate.start()
            self.isHidden = False
        self.set_source(event, source, call_back)
        self.constraint = constraint

        for lineIndex, line in enumerate(self.key_list_by_lines_lower):
            for keyIndex, key in enumerate(line):
                if(lineIndex):
                    button = self.array_buttons[lineIndex][keyIndex]
                    button.setDisabled(False)

        if constraint == self.capsLock:
            self.caps_button.setDisabled(True)
            self.caps_state = 0
            self.convert_to_caps()
        elif constraint == self.numberOnly or constraint == self.fractionNumber:
            for lineIndex, line in enumerate(self.key_list_by_lines_lower):
                for keyIndex, key in enumerate(line):
                    if(lineIndex):
                        button = self.array_buttons[lineIndex][keyIndex]
                        if not (button.text() == "Backspace" or button.text() == "Enter") and ((constraint == self.fractionNumber and not button.text() == ".") or constraint == self.numberOnly):
                            button.setDisabled(True)
        else:
            self.caps_state = 1
            self.caps_button.setDisabled(False)
            self.convert_to_caps()

        if x_pos:
            self.x_pos = x_pos
        if y_pos:
            self.y_pos = y_pos
        self.close_button.keyDisabled(closeButtonEnable)
        # self.move(self.x_pos, self.y_pos)

    def showAnimate(self, val):
        self.move(self.x_pos, 2 * self.y_pos - self.y_pos * (val) / 25)

    def backspacePressEvent(self, event):
        QtWidgets.QPushButton.mousePressEvent(self.back_button, event)
        self.keyPressHandler = keyPressHandlerThread(self.backSpaceSignal.signal, "Backspace", self)
        self.keyPressHandler.start()

    def backspaceReleaseEvent(self, event):
        QtWidgets.QPushButton.mouseReleaseEvent(self.back_button, event)
        self.keyPressHandler.setisKeyRelease(True)

    def backsapceDoubleClick(self, event):
        pass

    def set_source(self, event, source, call_back=None):
        self.callback_method = call_back
        self.source = source
        if source and event:
            if isinstance(self.source, QtWidgets.QLineEdit):
                QtWidgets.QLineEdit.mousePressEvent(source, event)
            elif isinstance(self.source, QtWidgets.QTextEdit):
                QtWidgets.QTextEdit.mousePressEvent(source, event)

    def get_button_by_key(self, key):
        """ AlphaNeumericVirtualKeyboard class method to get the handle of button by name

        Parameters
        ----------
        key : str
            key of the button

        Returns
        -------
        QPushbutton
            handle of the button with the assigned key
        """
        return getattr(self, "keyButton" + key.capitalize())

    def get_key(self, val):
        if not self.sym_state:
            return (val.lower(), val.capitalize())[self.caps_state]
        else:
            for i, e in enumerate(self.key_list_by_lines_lower):
                try:
                    pos = i, e.index(val)
                    retval = self.key_list_by_lines_sym[pos[0]][pos[1]]
                    if retval == "&&":
                        retval = "&"
                    return retval
                except ValueError:
                    pass

    def add_input_by_key(self, key):
        """ AlphaNeumericVirtualKeyboard class method to update lineedit when a key is pressed

        Parameters
        ----------
        key : str
            key to be added to the lineedit
        """
        if not self.source:
            return

        key_to_add = self.get_key(key)
        if isinstance(self.source, QtWidgets.QGraphicsTextItem):
            cursor = self.source.textCursor()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            if not start == end and start > end:
                temp = start
                start = end
                end = temp

            input_text = self.source.toPlainText()
            if(key_to_add == '  '):
                key_to_add = "\n"
            output_string = input_text[:start] + key_to_add + input_text[end:]
            self.source.setPlainText(output_string)
            new_cursor = QtGui.QTextCursor(cursor)
            new_cursor.setPosition(start + 1, 0)
            self.source.setTextCursor(new_cursor)
            if self.callback_method:
                self.callback_method("textChange")
        else:
            if(key_to_add == '  '):
                eventPress = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier)
                QtCore.QCoreApplication.postEvent(self.source, eventPress)
                eventRelease = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier)
                QtCore.QCoreApplication.postEvent(self.source, eventRelease)
                return
            else:
                if self.constraint == self.fractionNumber and "." in self.source.text() and key_to_add == ".":
                    return
                eventPress = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_1, QtCore.Qt.NoModifier, key_to_add)
                QtCore.QCoreApplication.postEvent(self.source, eventPress)
                eventRelease = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_1, QtCore.Qt.NoModifier, key_to_add)
                QtCore.QCoreApplication.postEvent(self.source, eventRelease)
                return

    def backspace(self):
        """ AlphaNeumericVirtualKeyboard class method to do backspace
        """
        if isinstance(self.source, QtWidgets.QGraphicsTextItem):
            cursor = self.source.textCursor()
            # cursor_position = cursor.position()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            if not start == end and start > end:
                temp = start
                start = end
                end = temp
            elif start == end:
                start = start - 1
            if start > -1:
                input_text = self.source.toPlainText()
                output_string = input_text[:start] + input_text[end:]
                self.source.setPlainText(output_string)
                new_cursor = QtGui.QTextCursor(cursor)
                new_cursor.setPosition(start, 0)
                self.source.setTextCursor(new_cursor)
                if self.callback_method:
                    self.callback_method("textChange")

        else:
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Backspace, QtCore.Qt.NoModifier)
            QtCore.QCoreApplication.postEvent(self.source, event)

    def close_handler(self):
        """ AlphaNeumericVirtualKeyboard class method to close the Virtual Keyboard pop up
        """
        if self.callback_method:
            self.callback_method("keyboard hidden")
        self.animationSignalForClose.signal.connect(self.closeAnimate)
        animate = AnimationThread(self.animationSignalForClose.signal, self)
        animate.start()

    def closeAnimate(self, val):
        self.move(self.x_pos, self.y_pos + self.y_pos * (val) / 25)
        if val == 25:
            self.hide()
            if self.close_ui_scroll:
                self.close_ui_scroll.hide()

    def paintEvent(self, event):
        """ Overrides resizeEvent method in QtGui.QWidget

        Parameters
        ----------
        event : QResizeEvent
            event handle raised by resize event

        """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 10, 10)
        QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon())
        pen = QtGui.QPen(QtCore.Qt.gray, 1)
        painter.setPen(pen)
        painter.fillPath(path, QtCore.Qt.gray)
        painter.drawPath(path)
        painter.end()

    def resizeEvent(self, event):
        """ Overrides method in QtGui.QWidget

        Parameters
        ----------
        event : QtCore.QEvent
            Event handle when AddPatientScreen widget resizes

        """
        self.resize(1070, 315)
        event.accept()


class BackSpaceSignal (QtCore.QObject):
    signal = QtCore.pyqtSignal()


class signalAnimation (QtCore.QObject):
    signal = QtCore.pyqtSignal(int)


class AnimationThread (QtCore.QThread):

    def __init__(self, signal, parent):
        super(AnimationThread, self).__init__(parent)
        self.signal = signal

    def run(self):
        for i in range(25):
            self.signal.emit(i + 1)
            time.sleep(0.01)


class keyPressHandlerThread (QtCore.QThread):

    def __init__(self, signal, key, parent):
        super(keyPressHandlerThread, self).__init__(parent)
        self.signal = signal
        self.key = key
        self.isKeyRelease = False
        self.threadIsStarted = False
        self.lock = threading.Lock()

    def setisKeyRelease(self, flag):
        self.lock.acquire()
        self.isKeyRelease = flag
        self.lock.release()

    def checkKeyRelease(self):
        self.lock.acquire()
        val = self.isKeyRelease
        self.lock.release()
        return val

    def run(self):
        if self.key == "Backspace":
            self.setisKeyRelease(False)
            self.signal.emit()
            time.sleep(1)
            while True:
                if not self.checkKeyRelease():
                    self.signal.emit()
                    time.sleep(0.05)
                else:
                    break
        # self.threadIsStarted = False
