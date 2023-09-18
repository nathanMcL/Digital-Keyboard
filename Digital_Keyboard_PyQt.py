# Digital keyboard with two text fields
# the standard keys function
# The emoji keys function
# The text field allows input from the system keyboard and digital keyboard

# The second text field is read only
# Once data is inputted, press 'enter'
# Second screen will generate the encrypted text into a caesar cipher with a shift value

# During Operation:
# *The digital keyboards additional keys do not function: capslock, shift, directional keys, F1-F12
# Use the system keyboard ATM.


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QScrollArea, QHBoxLayout, QFrame, QTextEdit
from PyQt5.QtCore import Qt
import pyautogui
import sys


class DigitalKeyboard(QWidget):
    def __init__(self):
        super(DigitalKeyboard, self).__init__()
        self.is_shift = False
        self.setWindowTitle("Digital Keyboard")
        layout = QGridLayout()
        self.button_list = []

        # Create two QTextEdit widgets (text boxes)
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit, 0, 0, 1, 12)
        self.text_edit.textChanged.connect(self.text_edited)  # Listen for changes

        self.encrypted_text_edit = QTextEdit()
        layout.addWidget(self.encrypted_text_edit, 0, 12, 1, 12)
        self.encrypted_text_edit.setReadOnly(True)  # Make the encrypted text box read-only

        # Create a Save button and add it to layout
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_text)
        layout.addWidget(save_button, 1, 24, 1, 1)

        # Create a scroll area for emojis
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)

        # Create emoji frame
        emoji_frame = QFrame()
        emoji_layout = QHBoxLayout()  # Changed to QHBoxLayout for horizontal layout
        emoji_frame.setLayout(emoji_layout)

        # Emojis list
        emojis = ['😊', '😂', '😍', '😀', '😁', '🤣', '😄', '😅', '😆', '😉', '😋', '😎', '😘', '😗', '😙', '😚', '😛',
                  '😜', '😝', '😞', '😟', '😠', '😡', '😢', '😭', '😰', '😱',
                  "👍", "👎", "👊", "✋", "👐", "🙌", "🙏", "🤝", "✌️", "🤟"]

        for emoji in emojis:
            emoji_button = QPushButton(emoji)
            emoji_button.clicked.connect(self.key_pressed)
            emoji_layout.addWidget(emoji_button)
            self.button_list.append(emoji_button)

        scroll.setWidget(emoji_frame)

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

    def key_pressed(self):
        key = self.sender().text()
        if self.is_shift:
            key = key.upper()

        cursor = self.text_edit.textCursor()

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
        elif key in self.emojis:  # you might want to make emojis a member variable for this to work
            cursor.insertText(key)
        elif key == "Shift":
            self.toggle_shift()

        self.text_edit.setTextCursor(cursor)  # Update the cursor position

        # Encrypt the text using a Caesar cipher with shift of 7 # Can change shift value
        plain_text = self.text_edit.toPlainText()
        encrypted_text = self.encrypt_caesar(plain_text, 7)
        self.encrypted_text_edit.setPlainText(encrypted_text)

    def encrypt_caesar(self, text, shift):
        encrypted_text = ""
        for char in text:
            if char.isalpha():
                shifted_char = chr(((ord(char.lower()) - ord('a') + shift) % 26) + ord('a'))
                encrypted_text += shifted_char.upper() if char.isupper() else shifted_char
            else:
                encrypted_text += char
        return encrypted_text

    def text_edited(self):
        # Encrypt the text automatically when text is edited
        plain_text = self.text_edit.toPlainText()
        if plain_text.endswith('\n'):
            encrypted_text = self.encrypt_caesar(plain_text.rstrip('\n'), 7)
            self.encrypted_text_edit.setPlainText(encrypted_text)

    def toggle_shift(self):
        self.is_shift = not self.is_shift
        for button in self.button_list:
            current_text = button.text()
            button.setText(current_text.upper() if self.is_shift else current_text.lower())

        # Save text

    def save_text(self):
        with open("saved_text.txt", "w") as f:
            f.write(self.text_edit.toPlainText())


if __name__ == "__main__":
    app = QApplication([])
    window = DigitalKeyboard()
    sys.exit(app.exec_())
