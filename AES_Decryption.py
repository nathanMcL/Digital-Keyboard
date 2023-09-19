# The purpose of this program:
# Input an encrypted AES text
# Input the provided AES key provided by Digital_Keyboard_encryption.py
# Press Decrypt and the message will decrypt the message. See uploaded screenshot.


import sys
import base64
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from cryptography.fernet import Fernet


# AES Decryption
class AESDecryption(QWidget):
    def __init__(self):
        super(AESDecryption, self).__init__()

        # Set window title and initial size
        self.setWindowTitle("AES Decrypter")
        self.resize(500, 700)  # Set initial window size

        layout = QVBoxLayout()

        self.label1 = QLabel("Enter AES Encrypted Text:")
        layout.addWidget(self.label1)

        self.text_edit_encrypted = QTextEdit()

        # Scale to fit content
        self.text_edit_encrypted.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.text_edit_encrypted)

        self.label2 = QLabel("Enter AES Key:")
        layout.addWidget(self.label2)

        self.text_edit_key = QTextEdit()

        # Scale to fit content
        self.text_edit_key.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.text_edit_key)

        self.decrypt_button = QPushButton("Decrypt")
        layout.addWidget(self.decrypt_button)

        self.decrypt_button.clicked.connect(self.decrypt_text)

        self.setLayout(layout)

    # Decrypt the text
    def decrypt_text(self):
        encrypted_text = self.text_edit_encrypted.toPlainText()
        aes_key = self.text_edit_key.toPlainText()

        try:
            cipher = Fernet(aes_key.encode())
            decrypted_text = cipher.decrypt(base64.urlsafe_b64decode(encrypted_text)).decode()
            self.text_edit_encrypted.setPlainText(decrypted_text)
        except:
            self.text_edit_encrypted.setPlainText("Invalid Key or Encrypted Text")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AESDecryption()
    window.show()
    sys.exit(app.exec_())
