# The purpose of this Text Editor:
# Created the Save, Save As, Open, Clear, Undo, Redo, and Close choices
# Toggle a dark or light theme
# Toggle random color text theme
# Created a Font style menu
# Created a Font size menu
# Created an Autosave feature that lets you choose to autosave every five or ten minutes
# Created line numbers to the left side of the text screen
# Needed to change dark theme text green, text not visible while the line is being highlighted

# Encrypt the text
# Generates the Encryption key
# Use Text_Editor_Decryption.py to decrypt messages

# all the things work :)

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel,
                             QMenuBar, QMenu, QAction, QFileDialog, QFontDialog, QComboBox, QWidgetAction, QTabWidget,
                             QActionGroup, QPlainTextEdit)
from PyQt5.QtGui import QIcon, QPalette, QColor, QTextCharFormat, QFont, QFontDatabase, QTextFormat, QPainter
from cryptography.fernet import Fernet
from PyQt5.QtCore import QTimer, QSize, QRect, Qt
import random  # for generating random colors


# Class to introduce line numbering to the text editor
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


# Main editor class which inherits from QPlainTextEdit
class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(300)  # trying to adjust, so maybe green isn't necessary
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


# Main class for the text editor application, inheriting from QMainWindow
class TextEditor(QMainWindow):

    def __init__(self):
        super().__init__()

        # Generate Fernet key
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

        # Setting up the main window
        self.setWindowTitle("MacN_ Text Editor")
        self.setGeometry(100, 100, 1000, 800)

        # Status bar
        self.status_bar = self.statusBar()

        # Main text editor
        self.text_edit = CodeEditor(self)
        self.text_edit.textChanged.connect(self.update_word_count)  # Status bar word count
        self.text_edit.textChanged.connect(self.update_encrypted_text)

        # Encrypted text display
        self.encrypted_text_display = QTextEdit(self)
        self.encrypted_text_display.setReadOnly(True)

        # Key display
        self.key_display = QTextEdit(self.key.decode())
        self.key_display.setReadOnly(True)

        # Introduce a boolean attribute to keep track of the random color feature
        self.random_color = False

        # Introduce a boolean attribute to keep track of the theme
        self.dark_theme = False  # Default is light theme

        # Font ComboBox
        self.font_combobox = QComboBox(self)
        self.font_combobox.addItems(QFontDatabase().families())
        self.font_combobox.currentTextChanged.connect(self.change_font)

        # Font Size ComboBox
        self.font_size_combobox = QComboBox(self)
        for i in range(8, 33, 2):  # Adding sizes 8, 10,...,32
            self.font_size_combobox.addItem(str(i))
        self.font_size_combobox.setCurrentText('12')  # Default size set to 12
        self.font_size_combobox.currentTextChanged.connect(self.change_font_size)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Text:"))
        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(QLabel("Encrypted Text:"))
        main_layout.addWidget(self.encrypted_text_display)
        main_layout.addWidget(QLabel("AES Key:"))
        main_layout.addWidget(self.key_display)

        # Adding font ComboBoxes to the layout
        main_layout.addWidget(self.font_combobox)
        main_layout.addWidget(self.font_size_combobox)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize autosave timer and current filename
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.current_filename = None

        # Create the menu bar
        self.create_menu_bar()

    # Functions to create and handle the menu bar
    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        # Clear action
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_fields)
        file_menu.addAction(clear_action)

        # 'Undo' last input feature
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.text_edit.undo)
        file_menu.addAction(undo_action)

        # 'Redo' last input feature
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.triggered.connect(self.text_edit.redo)
        file_menu.addAction(redo_action)

        # Toggle theme action
        toggle_theme_action = QAction("Toggle Theme", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        file_menu.addAction(toggle_theme_action)

        # Toggle random text color action
        toggle_random_color_action = QAction("Toggle Random Color", self)
        toggle_random_color_action.triggered.connect(self.toggle_random_color)
        file_menu.addAction(toggle_random_color_action)

        # "Close" action
        close_action = QAction("Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(self.close)  # Connect to the closed method
        file_menu.addAction(close_action)

        # Font ComboBox
        font_menu = QMenu("Font", self)
        font_widget_action = QWidgetAction(self)
        font_widget_action.setDefaultWidget(self.font_combobox)
        font_menu.addAction(font_widget_action)
        menubar.addMenu(font_menu)

        # Font Size ComboBox
        font_size_menu = QMenu("Size", self)
        font_size_widget_action = QWidgetAction(self)
        font_size_widget_action.setDefaultWidget(self.font_size_combobox)
        font_size_menu.addAction(font_size_widget_action)
        menubar.addMenu(font_size_menu)

        # Create auto-save menu
        autosave_menu = QMenu("AutoSave", self)
        autosave_5min_action = QAction("Every 5 minutes", self)
        autosave_5min_action.setCheckable(True)
        autosave_5min_action.triggered.connect(lambda: self.set_autosave_interval(5))

        autosave_10min_action = QAction("Every 10 minutes", self)
        autosave_10min_action.setCheckable(True)
        autosave_10min_action.triggered.connect(lambda: self.set_autosave_interval(10))

        # Group the actions to ensure that only one option can be active
        autosave_action_group = QActionGroup(self)
        autosave_action_group.addAction(autosave_5min_action)
        autosave_action_group.addAction(autosave_10min_action)

        autosave_menu.addAction(autosave_5min_action)
        autosave_menu.addAction(autosave_10min_action)
        self.menuBar().addMenu(autosave_menu)

    # Autosave interval function
    def set_autosave_interval(self, minutes):
        self.autosave_timer.start(minutes * 60 * 1000)  # Convert minutes to milliseconds

    # Autosave timer setup function
    def autosave(self):
        if self.current_filename:
            with open(self.current_filename, 'w') as file:
                file.write(self.text_edit.toPlainText())
        else:
            self.save_file()

    # Function to open a file
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.text_edit.setPlainText(file.read())
                self.current_filename = file_name

    # Function to save a file
    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
                self.current_filename = file_name

    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
                self.current_filename = file_name  # Update the current filename

    # Toggle random color
    def toggle_random_color(self):
        self.random_color = not self.random_color

    def update_encrypted_text(self):
        plain_text = self.text_edit.toPlainText()
        # Apply random color if the feature is enabled
        if self.random_color:
            self.apply_random_color()
        encrypted_text = self.cipher.encrypt(plain_text.encode())
        self.encrypted_text_display.setPlainText(encrypted_text.decode())

    def clear_fields(self):
        self.text_edit.clear()
        self.encrypted_text_display.clear()
        self.status_bar.showMessage("Word count: 0")  # for word count

    # toggle dark or light theme
    def toggle_theme(self):
        dark_palette = QPalette()
        light_palette = QApplication.style().standardPalette()  # default light theme palette

        # If a dark theme is currently applied, change to light, else change to dark
        if self.dark_theme:
            QApplication.setPalette(light_palette)
            self.status_bar.setStyleSheet("color: black")  # Set the status bar text color for light theme
            self.dark_theme = False
        else:
            # Set colors for the dark theme
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Text, QColor(0, 255, 0))  # Text box text
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # File drop down
            dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

            QApplication.setPalette(dark_palette)
            self.status_bar.setStyleSheet("color: white")  # Set the status bar text color for dark theme
            self.dark_theme = True

    # Apply the random text color
    def apply_random_color(self):
        # Generate a random color
        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Create a QTextCharFormat object with the color
        char_format = QTextCharFormat()
        char_format.setForeground(color)

        # Temporarily block the signals to avoid recursion
        self.text_edit.blockSignals(True)

        # Apply the color to the last character entered
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.Left, cursor.KeepAnchor)
        cursor.mergeCharFormat(char_format)
        self.text_edit.mergeCurrentCharFormat(char_format)

        # Unblock the signals
        self.text_edit.blockSignals(False)

    # Change font based on the ComboBox selection
    def change_font(self, font_name):
        font = QFont(font_name)
        font_size = int(self.font_size_combobox.currentText())
        font.setPointSize(font_size)
        self.text_edit.setFont(font)

    # Change font size based on the ComboBox selection
    def change_font_size(self, size):
        font_name = self.font_combobox.currentText()
        font = QFont(font_name)
        font.setPointSize(int(size))
        self.text_edit.setFont(font)

    # Status bar word count
    def update_word_count(self):
        text = self.text_edit.toPlainText()
        word_count = len(text.split())
        self.status_bar.showMessage(f"Word count: {word_count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TextEditor()
    main_window.show()
    sys.exit(app.exec_())
