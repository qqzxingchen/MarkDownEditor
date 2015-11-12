
import sys

from PyQt5.QtWidgets import QTextEdit
from PyQt5 import QtCore


class TextEditor(QTextEdit):
    
    textChangeSignal = QtCore.pyqtSignal(dict)
    KEY_ORIGINALTXET = "originalData"
    
    def __init__(self, *args, **kwargs):
        QTextEdit.__init__(self, *args, **kwargs)
        self.textChanged.connect(self.__onTextChanged)
    
    def __onTextChanged(self):
        data = {}
        data[TextEditor.KEY_ORIGINALTXET] = self.toPlainText()
        self.textChangeSignal.emit(data)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    def onEditorDataChanged(data):
        print (data)
    
    editor = TextEditor()
    editor.show()
    editor.textChangeSignal.connect(onEditorDataChanged)
    
    sys.exit( app.exec_() )



