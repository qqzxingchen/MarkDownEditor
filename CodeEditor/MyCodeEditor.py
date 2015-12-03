
import sys

from PyQt5.QtWidgets import QWidget,QScrollBar
from PyQt5 import QtCore

from CodeEditor.CodeTextEditWidget import CodeTextEditWidget
from CodeEditor.TextDocument import TextDocument

class MyCodeEditor(QWidget):

    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        
        self.__initData()


    def __initData(self):
        self.__codeTextWidget = CodeTextEditWidget(self)
        self.__codeTextWidget.textChangedSignal.connect(self.__onCodeTextChanged)
        self.__codeTextWidget.lineStrLengthChangedSignal.connect(self.__onLineStrLengthChanged)
        
        # 横纵滚动条
        self.__verticalScrollBar = QScrollBar(self)
        self.__verticalScrollBar.adjustSize()
        self.__verticalScrollBar.setMinimumWidth(self.__verticalScrollBar.width())
        self.__verticalScrollBar.setMaximumWidth(self.__verticalScrollBar.width())  
        self.__verticalScrollBar.valueChanged.connect(self.__onVScrollValueChanged)
        
        self.__horizontalScrollBar = QScrollBar(QtCore.Qt.Horizontal,self)
        self.__horizontalScrollBar.adjustSize()
        self.__horizontalScrollBar.setMinimumHeight(self.__horizontalScrollBar.height())
        self.__horizontalScrollBar.setMaximumHeight(self.__horizontalScrollBar.height())
        self.__horizontalScrollBar.valueChanged.connect(self.__onHScrollValueChanged)
        
        self.setText = self.__codeTextWidget.setText

    def __onLineStrLengthChanged(self,newMaxLength):
        hMax = newMaxLength-1
        self.__horizontalScrollBar.setRange(0,hMax)
        if self.__horizontalScrollBar.value() > hMax:
            self.__horizontalScrollBar.setValue(hMax)
        
    
    def __onCodeTextChanged(self,newTextDocument):        
        vMax = newTextDocument.getLineCount()-1
        self.__verticalScrollBar.setRange(0,vMax)
        if self.__verticalScrollBar.value() > vMax:
            self.__verticalScrollBar.setValue(vMax)


    def __onVScrollValueChanged(self):
        self.__codeTextWidget.showLineNumberAsTop(self.__verticalScrollBar.value())
        
    def __onHScrollValueChanged(self):
        self.__codeTextWidget.showLeftXOffAsLeft(self.__horizontalScrollBar.value())
        
    
    def resizeEvent(self, event):
        vScrollBarWidth = self.__verticalScrollBar.width()        
        hScrollBarHeight = self.__horizontalScrollBar.height()
        self.__codeTextWidget.setGeometry( 0,0,self.width()-vScrollBarWidth,self.height()-hScrollBarHeight )        
        self.__verticalScrollBar.setGeometry(self.width()-vScrollBarWidth,0,vScrollBarWidth,self.height()-hScrollBarHeight)

        codeTextLeftXOff = self.__codeTextWidget.getTextLeftXOff()
        self.__horizontalScrollBar.setGeometry(codeTextLeftXOff,self.height()-hScrollBarHeight,self.width()-vScrollBarWidth-codeTextLeftXOff,hScrollBarHeight)        
        
    '''
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__verticalScrollBar.setValue( self.__verticalScrollBar.value()+1 )
        else:
            self.__horizontalScrollBar.setValue( self.__horizontalScrollBar.value()+1 )
    ''' 
    

        

        




if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs
    
    
    app = QApplication(sys.argv)
    
    mce = MyCodeEditor()
    with codecs.open( '../tmp/temp.txt','r','utf-8' ) as templateFileObj:
        fileStr = templateFileObj.read()
        mce.setText(fileStr)
    mce.show()
    mce.resize(600,400)
    
    sys.exit( app.exec_() )









