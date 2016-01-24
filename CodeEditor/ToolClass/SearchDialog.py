

from PyQt5 import QtGui, QtCore

from PyQt5.QtWidgets import QDialog, QWidget

from CodeEditor.UI import UI_SearchDialog


class SearchDialog(QDialog,UI_SearchDialog.Ui_Dialog):
    
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        UI_SearchDialog.Ui_Dialog.__init__(self)
        self.setupUi(self)
        
        #self.setFocusPolicy()
        #self.setWindowOpacity( 0.8 )
    
    
    
    
    



if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    
    widget = QWidget()
    widget.show()
    
    dialog = SearchDialog(widget)
    dialog.show()

    sys.exit( app.exec_() )
