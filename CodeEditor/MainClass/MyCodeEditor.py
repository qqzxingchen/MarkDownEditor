
import sys

from PyQt5.QtWidgets import QWidget,QScrollBar,QSplitter
from PyQt5 import QtCore

from CodeEditor.MainClass.CodeTextWidget import CodeTextWidget
from CodeEditor.MainClass.LineNumberWidget import LineNumberWidget

from CodeEditor.CustomVersion.Python3Version.PythonTextDocument import PythonTextDocument

from CodeEditor.ToolClass.EditorSettings import EditorSettings






class MyCodeEditor(QWidget):

    def __init__(self,parent=None):
        QWidget.__init__(self,parent)

        self.__editorSettings = EditorSettings()
        self.__textDocument = PythonTextDocument()

        # 横纵滚动条
        self.__verticalScrollBar = QScrollBar(self)
        self.__verticalScrollBar.adjustSize()
        self.__verticalScrollBar.setMinimumWidth(self.__verticalScrollBar.width())
        self.__verticalScrollBar.setMaximumWidth(self.__verticalScrollBar.width())  
        self.__verticalScrollBar.valueChanged.connect(self.__onVScrollValueChanged)
        self.__editorSettings.startDisLineNumberChangedSignal.connect(self.__verticalScrollBar.setValue)
    
        self.__horizontalScrollBar = QScrollBar(QtCore.Qt.Horizontal,self)
        self.__horizontalScrollBar.adjustSize()
        self.__horizontalScrollBar.setMinimumHeight(self.__horizontalScrollBar.height())
        self.__horizontalScrollBar.setMaximumHeight(self.__horizontalScrollBar.height())
        self.__horizontalScrollBar.valueChanged.connect(self.__onHScrollValueChanged)
        self.__editorSettings.startDisLetterXOffChangedSignal.connect(self.__horizontalScrollBar.setValue)
        

        self.__lineNumberWidget = LineNumberWidget(self.__editorSettings,self)
        setattr(self.__lineNumberWidget,'resizeEvent',self.__onLineNumberWidgetSizeChanged)
                
        self.__codeTextWidget = CodeTextWidget(self.__textDocument,self.__editorSettings,self)
        self.__codeTextWidget.document().totalLevelTextChangedSignal.connect(self.__onCodeTextChanged)
        self.__codeTextWidget.settings().lineTextMaxPixelChangedSignal.connect(self.__onLineStrLengthChanged)
        self.__codeTextWidget.visibleLineYOffInfoChangedSignal.connect( self.__lineNumberWidget.setVisibleLineYOffInfoArray )
        
        
        self.__splitter = QSplitter(self)
        self.__splitter.addWidget( self.__lineNumberWidget )
        self.__splitter.addWidget( self.__codeTextWidget )
        self.__splitter.setCollapsible( 0,False )
        self.__splitter.setCollapsible( 1,False )

        self.setText = self.__codeTextWidget.setText
        self.getText = self.__codeTextWidget.getText



    def __onLineStrLengthChanged(self,newMaxLength):
        hMax = newMaxLength-1
        self.__horizontalScrollBar.setRange(0,hMax)
        if self.__horizontalScrollBar.value() > hMax:
            self.__horizontalScrollBar.setValue(hMax)
        
    
    def __onCodeTextChanged(self,*arg1,**arg2):        
        vMax = self.__codeTextWidget.document().getLineCount()-1
        self.__verticalScrollBar.setRange(0,vMax)
        if self.__verticalScrollBar.value() > vMax:
            self.__verticalScrollBar.setValue(vMax)


    def __onVScrollValueChanged(self):
        self.__codeTextWidget.showLineNumberAsTop(self.__verticalScrollBar.value())
        
    def __onHScrollValueChanged(self):
        self.__codeTextWidget.showLeftXOffAsLeft(self.__horizontalScrollBar.value())
    
    
    
    
    def __onLineNumberWidgetSizeChanged(self,*arg1,**arg2):
        lineNumberWidgetWidth = self.__lineNumberWidget.width()
        vScrollBarWidth = self.__verticalScrollBar.width()        
        hScrollBarHeight = self.__horizontalScrollBar.height()
        self.__horizontalScrollBar.setGeometry(lineNumberWidgetWidth,self.height()-hScrollBarHeight, \
                                               self.width()-vScrollBarWidth-lineNumberWidgetWidth,hScrollBarHeight)    
    
    def resizeEvent(self, event):
        vScrollBarWidth = self.__verticalScrollBar.width()        
        hScrollBarHeight = self.__horizontalScrollBar.height()
        self.__splitter.setGeometry( 0,0,self.width()-vScrollBarWidth,self.height()-hScrollBarHeight )
        self.__verticalScrollBar.setGeometry(self.width()-vScrollBarWidth,0,vScrollBarWidth,self.height()-hScrollBarHeight)
        self.__onLineNumberWidgetSizeChanged()
        
    def wheelEvent(self, event):
        changedV = 3 if event.angleDelta().y() < 0 else -3
        self.__verticalScrollBar.setValue( self.__verticalScrollBar.value() + changedV )
        



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs
    
    
    app = QApplication(sys.argv)
    
    mce = MyCodeEditor()
    #with codecs.open( '../tmp/temp3.txt','r','utf-8' ) as templateFileObj:
    with codecs.open( 'CodeTextWidget.py','r','utf-8' ) as templateFileObj:
        fileStr = templateFileObj.read()
        mce.setText(fileStr*25)
    mce.show()
    mce.resize(600,400)
    
    sys.exit( app.exec_() )









