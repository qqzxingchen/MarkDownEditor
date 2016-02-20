

from PyQt5 import QtGui, QtCore

from PyQt5.QtWidgets import QDialog, QWidget

from CodeEditor.UI import UI_SearchDialog


class SearchDialog(QDialog,UI_SearchDialog.Ui_Dialog):
    
    findButtonClickedSignal = QtCore.pyqtSignal()
    replaceOrFindButtonClickedSignal = QtCore.pyqtSignal()
    replaceButtonClickedSignal = QtCore.pyqtSignal()
    replaceAllButtonClickedSignal = QtCore.pyqtSignal()
    
    NAMES_COMBOBOX = ['findComboBox', \
                      'replaceWithComboBox']
    NAMES_RADIO = ['forwardDirectionRadio', \
                   'backwardDirectionRadio', \
                   'allScopeRadio', \
                   'selectedLineScopeRadio']
    NAMES_CHECKBOX = ['caseSensitiveOptionsCheckBox' , \
                      'wrapSearchOptionsCheckBox' , \
                      'wholeWordOptionsCheckBox' , \
                      'incrementalOptionsCheckBox' , \
                      'regularExpressionsOptionsCheckBox' ]


    
    def setInfo(self,text = ''):
        if isinstance(text, str) == False:
            text = ''
        self.infoLabel.setText(text)
    
    
    def querySettings(self):
        retuDict = {}
        for controlName in SearchDialog.NAMES_COMBOBOX:
            retuDict[controlName] = getattr(self, controlName).currentText()
        for controlName in SearchDialog.NAMES_RADIO:
            retuDict[controlName] = getattr(self, controlName).isChecked()
        for controlName in SearchDialog.NAMES_CHECKBOX:
            retuDict[controlName] = getattr(self, controlName).checkState() == QtCore.Qt.Checked
        return retuDict
    
    def show(self,settings = None):
        if settings != None:
            for controlName in SearchDialog.NAMES_COMBOBOX:
                v = settings.get(controlName) 
                if isinstance(v, str) :
                    self.insertTextToComboBox(controlName, v)
            for controlName in SearchDialog.NAMES_RADIO:
                v = settings.get(controlName)
                if isinstance(v, bool):
                    getattr(self, controlName).setChecked(v)
            for controlName in SearchDialog.NAMES_CHECKBOX:
                v = settings.get(controlName)
                if isinstance(v, bool):
                    getattr(self, controlName).setCheckState( QtCore.Qt.Checked if v == True else QtCore.Qt.Unchecked )
        QDialog.show(self)
                
    def hide(self):
        QDialog.hide(self)
    
    
            
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        UI_SearchDialog.Ui_Dialog.__init__(self)
        self.setupUi(self)
        
        self.forwardDirectionRadio.setChecked(True)
        self.allScopeRadio.setChecked(True)
        self.wrapSearchOptionsCheckBox.setCheckState( QtCore.Qt.Checked )

        #self.setFocusPolicy()
        #self.setWindowOpacity( 0.8 )
    
        self.findButton.clicked.connect( self.findButtonClickedSignal )
        self.replaceOrFindButton.clicked.connect( self.replaceOrFindButtonClickedSignal )
        self.replaceButton.clicked.connect( self.replaceButtonClickedSignal )
        self.replaceAllButton.clicked.connect( self.replaceAllButtonClickedSignal )
        self.closeButton.clicked.connect( self.hide )

        
        

            
    def closeEvent(self, event):
        self.hide()
        event.ignore()
    
    def insertTextToComboBox(self,controlName,value,selected = True):        
        control = getattr(self,controlName)
        if control == None or value == '':
            return False
        
        index = control.findText(value)
        if index == -1:
            control.insertItem( 0,value )
            index = 0

        if selected == True:
            control.setCurrentIndex(index)
        
        return True


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    
    widget = QWidget()
    widget.show()
    
    dialog = SearchDialog(widget)
    dialog.show()

    
    dialog.findButtonClickedSignal.connect( lambda : print ('find') )
    dialog.replaceOrFindButtonClickedSignal.connect( lambda : print ('replaceOrFind') )
    dialog.replaceButtonClickedSignal.connect( lambda : print ('replace') )
    dialog.replaceAllButtonClickedSignal.connect( lambda : print ('replaceAll') )
    
    #dialog.findButton.clicked.connect( lambda : dialog.insertTextToComboBox('findComboBox', '1') )
    
    
    sys.exit( app.exec_() )










