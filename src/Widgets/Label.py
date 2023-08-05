from PyQt6.QtWidgets import QLabel

tabstop = 4

class Label(QLabel):
    def __init__(self,text = None):
        if text:
            newText = ""
            for c in text:
                if c == '\t':
                    newText += ' '*tabstop
                else:
                    newText += c
            super().__init__(newText)
        else:
            super().__init__()

    def setText(self, text: str) -> None:
        if text is not None:
            newText = ""
            for c in text:
                if c == '\t':
                    newText += ' '*tabstop
                else:
                    newText += c
            return super().setText(newText)
        return super().setText(text)