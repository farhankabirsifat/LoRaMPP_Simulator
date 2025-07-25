from PyQt5.QtWidgets import QTextEdit


class Logger(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("""
                    QTextEdit {
                        background-color: #f9f9f9;
                        color: #333333;
                        font-family: Consolas, monospace;
                        font-size: 10pt;
                        border: 1px solid #dddddd;
                        border-radius: 4px;
                    }
                """)

    def log(self, message):
        self.append(message)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())