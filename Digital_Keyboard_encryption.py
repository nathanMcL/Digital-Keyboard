# Digital keyboard
# Two text fields One read only
# the standard keys function
# The emoji keys function :p
# The save button saves the text file :)
# The text field allows input from the system keyboard and digital keyboard
# The Direction arrow keys function :) kinda :\

# The second text field is read only
# Once data is inputted, press 'enter'
# Second screen will generate an AES encrypted text of your plain text message

# During Operation:
# *The digital keyboards additional keys do not function: capslock, shift :(
# Use the system keyboard ATM.
# Added lines of code that should have fixed caps lock and shift from closing program without error, unexpectedly :(
# But, check out them emojis always adding more :) !!!

import base64
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QScrollArea, QHBoxLayout, QFrame, QTextEdit
from cryptography.fernet import Fernet
from PyQt5.QtGui import QTextCursor


# Define the main class inheriting from QWidget
class DigitalKeyboard(QWidget):
    def __init__(self):
        super(DigitalKeyboard, self).__init__()

        # Emojis list
        emojis = ['😊', '😂', '😍', '😀', '😁', '🤣', '😄', '😅', '😆', '😉', '😋', '😎', '😘', '😗', '😙', '😚', '😛',
                  '😜', '😝', '😞', '😟', '😠', '😡', '😢', '😭', '😰', '😱', "🥸", "🥵", "🥶", "🥴", "😵", "🤯", '🌕', '🦄',
                  "👍", "👎", "👊", "✋", "👐", "🙌", "🙏", "🤝", "✌️", "🤟", "💃", "🕺", "🕴️", ]

        # Initialize internal variables
        self.is_shift = False
        self.is_capslock = False  # Add this ine to keep track of the Caps Lock status
        self.setWindowTitle("Digital Keyboard")

        # Initialize grid layout
        layout = QGridLayout()

        # Initialize a list to store buttons
        self.button_list = []
        self.emojis = emojis  # Save emojis to the object

        # Create two QTextEdit widgets (text boxes)
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit, 0, 0, 1, 12)
        self.text_edit.textChanged.connect(self.text_edited)  # Listen for changes

        self.encrypted_text_edit = QTextEdit()
        layout.addWidget(self.encrypted_text_edit, 0, 12, 1, 12)
        self.encrypted_text_edit.setReadOnly(True)  # Make the encrypted text box read-only

        # Generate a random encryption key
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Debugging line; NEVER print a key in production
        print(f"Encryption Key: {self.encryption_key.decode()}")

        # Create a Save button and add it to layout
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_text)
        layout.addWidget(save_button, 1, 24, 1, 1)

        # Create a scrollable area for emoji buttons
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)

        # Create emoji frame
        emoji_frame = QFrame()
        emoji_layout = QHBoxLayout()  # Changed to QHBoxLayout for horizontal layout
        emoji_frame.setLayout(emoji_layout)

        # Create and add emoji buttons to the layout
        for emoji in emojis:
            emoji_button = QPushButton(emoji)
            emoji_button.clicked.connect(self.key_pressed)
            emoji_layout.addWidget(emoji_button)
            self.button_list.append(emoji_button)

        scroll.setWidget(emoji_frame)

        # Define keyboard layout and buttons
        self.rows = [
            ['Play', 'Pause', 'Stop', 'Next', 'Prev'],  # Media keys
            ['@', '#', '$', '%', '^'],  # Special characters
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
            ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
            ['Up', 'Down', 'Left', 'Right'],
            ['Space']
        ]

        # Create and add buttons for keyboard layout
        for i, row in enumerate(self.rows):
            for j, button_text in enumerate(row):
                button = QPushButton(button_text)
                button.clicked.connect(self.key_pressed)
                layout.addWidget(button, i + 1, j)  # Adjust the row index by adding 1
                self.button_list.append(button)

        # Add the scroll area to the layout
        layout.addWidget(scroll, 2, 0, 1, len(self.rows[0]))

        self.setLayout(layout)
        self.show()

    # Event handler for button clicks
    def key_pressed(self):
        key = self.sender().text()
        # print(f"Key pressed: {key}")  # Debugging line

        cursor = self.text_edit.textCursor()  # Initialize cursor here, just once

        # If Caps Lock is enabled, make the character uppercase
        if self.is_capslock and len(key) == 1:
            key = key.upper()

        # If Shift is pressed, also make the character uppercase
        if self.is_shift and len(key) == 1:
            key = key.upper()

        if len(key) == 1:
            cursor.insertText(key)
        elif key == 'Backspace':
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
        elif key == 'Enter':
            cursor.insertText('\n')
        elif key == 'Space':
            cursor.insertText(' ')
        elif key == 'Tab':
            cursor.insertText('\t')
        elif key in self.emojis:  # you might want to make emojis a member variable for this to work :p
            cursor.insertText(key)
        elif key == "Shift":
            self.toggle_shift()
        elif key == "Caps":  # Handle the Caps button
            self.toggle_capslock()

        # Adding functionality for directional keys
        elif key == 'Up':
            cursor.movePosition(QTextCursor.Up)
        elif key == 'Down':
            cursor.movePosition(QTextCursor.Down)
        elif key == 'Left':
            cursor.movePosition(QTextCursor.Left)
        elif key == 'Right':
            cursor.movePosition(QTextCursor.Right)

        # Make sure the cursor is visible
        self.text_edit.ensureCursorVisible()

        # Update the cursor position
        self.text_edit.setTextCursor(cursor)

        # Encrypt the text using AES
        plain_text = self.text_edit.toPlainText()
        encrypted_text = self.encrypt_text(plain_text)
        self.encrypted_text_edit.setPlainText(encrypted_text)

    # AES encryption
    def encrypt_text(self, text):
        encoded_text = text.encode()
        encrypted_text = self.cipher_suite.encrypt(encoded_text)
        return base64.urlsafe_b64encode(encrypted_text).decode()

    # Event handler for text changes in the QTextEdit
    def text_edited(self):
        # Use the encrypt_text function, not encrypt_caesar
        plain_text = self.text_edit.toPlainText()
        if plain_text.endswith('\n'):
            encrypted_text = self.encrypt_text(plain_text.rstrip('\n'))
            self.encrypted_text_edit.setPlainText(encrypted_text)

    # Toggle Shift key
    def toggle_shift(self):
        self.is_shift = not self.is_shift
        for button in self.button_list:
            current_text = button.text()
            button.setText(current_text.upper() if self.is_shift else current_text.lower())

    # Toggle Caps Lock key
    def toggle_capslock(self):
        self.is_capslock = not self.is_capslock
        for button in self.button_list:
            current_text = button.text()
            if len(current_text) == 1 and current_text.isalpha():  # Only affect alphabetical characters
                new_text = current_text.upper() if self.is_capslock else current_text.lower()
                if new_text != current_text:
                    button.setText(new_text)

    # Update button text based on Shift or Caps Lock state
    def update_buttons(self):
        for button in self.button_list:
            current_text = button.text()
            if self.is_shift or self.is_capslock:
                button.setText(current_text.upper())
            else:
                button.setText(current_text.lower())

    # Save the text in the QTextEdit to a file
    def save_text(self):
        with open("DigitalKeyBoard_text.txt", "w") as f:
            f.write(self.text_edit.toPlainText())


if __name__ == "__main__":
    app = QApplication([])
    window = DigitalKeyboard()
    sys.exit(app.exec_())
