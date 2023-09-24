# The purpose of this program:
# Decrypt the Text_editor.py message
# Created a dropdown menu
# Created a clear function to clear all the data before closing
# Created a save function that saves and decrypts the message back into AES format
# Created a dark theme feature

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QPushButton,
                             QMenuBar, QMenu, QAction, QFileDialog)
from cryptography.fernet import Fernet


class TextDecryptor(QMainWindow):

    def __init__(self):
        super().__init__()

        # Setting up the main window
        self.setWindowTitle("MacN_ Text Decryptor")
        self.setGeometry(100, 100, 800, 600)

        # Encrypted text input
        self.encrypted_text_input = QTextEdit(self)
        self.encrypted_text_input.setPlaceholderText("Paste the encrypted text here")

        # Key input
        self.key_input = QTextEdit(self)
        self.key_input.setPlaceholderText("Enter the generated AES key here")

        # Decrypted text display
        self.decrypted_text_display = QTextEdit(self)
        self.decrypted_text_display.setReadOnly(True)

        # Decrypt button
        self.decrypt_button = QPushButton("Decrypt", self)
        self.decrypt_button.clicked.connect(self.decrypt_text)

        # Introduce a boolean attribute to keep track of the theme
        self.dark_theme = False # Default is light theme

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Encrypted Text:"))
        main_layout.addWidget(self.encrypted_text_input)
        main_layout.addWidget(QLabel("AES Key:"))
        main_layout.addWidget(self.key_input)
        main_layout.addWidget(self.decrypt_button)
        main_layout.addWidget(QLabel("Decrypted Text:"))
        main_layout.addWidget(self.decrypted_text_display)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Create the menu bar
        self.create_menu_bar()

    # Create a menu bar function
    def create_menu_bar(self):
        menubar = self.menuBar()
        actions_menu = QMenu("Menu", self)
        menubar.addMenu(actions_menu)

        # Clear text option
        clear_action = QAction("Clear Text", self)
        clear_action.triggered.connect(self.clear_fields)
        actions_menu.addAction(clear_action)

        # Save the Decrypted message option
        save_action = QAction("Save Decrypted Text", self)
        save_action.triggered.connect(self.save_decrypted_text)
        actions_menu.addAction(save_action)

        # Toggle theme option
        toggle_theme_action = QAction("Dark Theme", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        actions_menu.addAction(toggle_theme_action)

    # Decrypt the text
    def decrypt_text(self):
        encrypted_text = self.encrypted_text_input.toPlainText().encode()
        key = self.key_input.toPlainText().encode()

        cipher = Fernet(key)
        try:
            decrypted_text = cipher.decrypt(encrypted_text)
            self.decrypted_text_display.setPlainText(decrypted_text.decode('utf-8'))
        except:
            self.decrypted_text_display.setPlainText("Decryption failed. Please check the encrypted text and key.")

    # Save the decrypted text
    def save_decrypted_text(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Encrypted Text", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            # Fetch the decrypted text
            decrypted_text = self.decrypted_text_display.toPlainText()

            # Re-encrypt the text using the provided AES key
            key = self.key_input.toPlainText().encode()
            cipher = Fernet(key)
            encrypted_text = cipher.encrypt(decrypted_text.encode())

            # Save the encrypted content to the file
            with open(file_name, 'wb') as file:
                file.write(encrypted_text)

    # Clear the Encrypted and Decrypted text fields
    def clear_fields(self):
        self.encrypted_text_input.clear()
        self.key_input.clear()  # If you want to clear the AES key input
        self.decrypted_text_display.clear()

        # toggle dark or light theme
    def toggle_theme(self):
        dark_palette = QPalette()
        light_palette = QApplication.style().standardPalette()  # default light theme palette

        # If a dark theme is currently applied, change to light, else change to dark
        if self.dark_theme:
            QApplication.setPalette(light_palette)
            self.dark_theme = False
        else:
            # Set colors for the dark theme
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Menu bar, Decryption option
            dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

            QApplication.setPalette(dark_palette)
            self.dark_theme = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextDecryptor()
    window.show()
    sys.exit(app.exec_())
