
import sys

from PyQt5.QtWidgets import QTextEdit, QWidget, QScrollBar, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QFontMetrics, QPainter


class MyTextEdit(QWidget):
    
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self,*args,**kwargs)

        self.__initData()
        fm = self.__fontMetrics
        print (fm.height(),fm.leading(),fm.lineSpacing())

    
    def resizeEvent(self, event):
        vScrollBarWidth = self.__verticalScrollBar.width()        
        hScrollBarHeight = self.__horizontalScrollBar.height()
        self.__textWidget.setGeometry( 0,0,self.width()-vScrollBarWidth,self.height()-hScrollBarHeight )
        self.__verticalScrollBar.setGeometry(self.width()-vScrollBarWidth,0,vScrollBarWidth,self.height())
        self.__horizontalScrollBar.setGeometry(0,self.height()-hScrollBarHeight,self.width()-vScrollBarWidth,hScrollBarHeight)

    def __paintEvent(self, event):
        painter = QPainter(self.__textWidget)
        painter.setFont(self.__font)

        needDrawInfos = []
        

        for i in range( self.__startDisLineNumber,len(self.__resourceStrLineRanges) ):
            curY = self.__offY + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            
            curLineStr = self.__resourceStrLineRanges[i] 

            curLineStrRect = painter.boundingRect(self.__offX, curY, 0,0,0,curLineStr)
            curLineStrRect.setLeft( curLineStrRect.left()-self.__fontMetrics.width(curLineStr[0:self.__startDisLetterNumber]) )
            needDrawInfos.append( { 'rect':curLineStrRect,'str':curLineStr } )
            
            
            
            
            
        for info in needDrawInfos:
            #if event.rect().
            
            painter.drawText(info['rect'],0,info['str'] )
        
        print (event.rect(),event.region().boundingRect())
        
    
    
    def __initData(self):
        # 显示文本时，将会按照以下偏移进行
        self.__offX = 4
        self.__offY = 4
        
        # 当前将会从第 startDisLineNumber 行开始显示
        self.__startDisLineNumber = 0
        
        # 每行将会从第 startDisLetterNumber 个字符开始显示
        self.__startDisLetterNumber = 2
        
        
        self.__font = QFont('Consolas')
        self.__fontMetrics = QFontMetrics(self.__font)
        
        self.__verticalScrollBar = QScrollBar(self)
        self.__verticalScrollBar.adjustSize()
        self.__verticalScrollBar.setMinimumWidth(self.__verticalScrollBar.width())
        self.__verticalScrollBar.setMaximumWidth(self.__verticalScrollBar.width())
        
        self.__horizontalScrollBar = QScrollBar(QtCore.Qt.Horizontal,self)
        self.__horizontalScrollBar.adjustSize()
        self.__horizontalScrollBar.setMinimumHeight(self.__horizontalScrollBar.height())
        self.__horizontalScrollBar.setMaximumHeight(self.__horizontalScrollBar.height())
        
        
        self.__textWidget = QWidget(self)
        setattr(self.__textWidget, 'paintEvent', self.__paintEvent)
        
        
        self.__resourceStr = ''
        for i in range(100):
            self.__resourceStr += str(i)+'tempStrasd asd asd asd asd \n'
        self.__resourceStrLineRanges = self.__resourceStr.split('\n')

        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    mte = MyTextEdit()
    mte.show()
    
    
    
    sys.exit( app.exec_() )



