# The purpose of this program:
# Decrypt the Text_editor.py message

import sys
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

    def decrypt_text(self):
        encrypted_text = self.encrypted_text_input.toPlainText().encode()
        key = self.key_input.toPlainText().encode()

        cipher = Fernet(key)
        try:
            decrypted_text = cipher.decrypt(encrypted_text)
            self.decrypted_text_display.setPlainText(decrypted_text.decode('utf-8'))
        except:
            self.decrypted_text_display.setPlainText("Decryption failed. Please check the encrypted text and key.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextDecryptor()
    window.show()
    sys.exit(app.exec_())
