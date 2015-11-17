
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QColor, QPen
from PyQt5 import QtCore


class CodeTextEditWidget(QWidget):
    # 其中bool指代的是文本改变之后，文本的行数有没有发生改变
    # 为True则表示行数发生改变
    textChangedSignal = QtCore.pyqtSignal( bool )       
    
    # 修改字体，注意，当前只支持等宽字体
    def setFont(self,fontObj=QFont('Consolas')):
        self.__font = fontObj
        self.__fontMetrics = QFontMetrics(self.__font)
        self.update()
    
    def setText(self,text=''):
        self.__text = text
        
        splitN = self.__text.split('\n')
        splitRN = self.__text.split('\r\n')
        self.__splitedText = splitRN if len(splitN) == len(splitRN) else splitN
        
        self.update()
        self.textChangedSignal.emit(True)
    
    def setEditAble(self,canEdit=True):
        if canEdit == True:
            self.__editAble = True
        else:
            self.__editAble = False
    
    def setLineRightAndTextLeftX(self,lineRightX,textLeftX):
        self.__lineNumberRightXOff = lineRightX
        self.__textLeftXOff = textLeftX
        self.update()
    def getLineRightAndTextLeftX(self):
        return (self.__lineNumberRightXOff,self.__textLeftXOff)
    
    def getMaxLineNumber(self):
        return len(self.__splitedText)
    def getMaxLetterNumber(self):
        maxNumber = 0
        for l in self.__splitedText:
            if len(l) > maxNumber:
                maxNumber = len(l)
        return maxNumber
    
    
    
    
    
    
    def showLineNumberAsTop(self,lineNumber,update=True):
        if lineNumber < 0:
            self.__startDisLineNumber = 0
        elif lineNumber >= len(self.__splitedText):
            self.__startDisLineNumber = len(self.__splitedText)-1
        else:
            self.__startDisLineNumber = int(lineNumber)
        if update == True:
            self.update()
    def showLetterNumberAsLeft(self,letterNumber,update=True):
        if letterNumber < 0:
            self.__startDisLetterNumber = 0
        else:
            self.__startDisLetterNumber = int(letterNumber)
        if update == True:
            self.update()
        
        
    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        setattr(self, 'paintEvent', self.paintEvent)
        self.__initData()

    
    def __initData(self):
        self.setFont()
        self.setText()
        self.setEditAble()

        self.__offY = 4
        self.__lineNumberRightXOff = 24     # 行号将会右对齐于x=20的一条竖线
        self.__textLeftXOff = 40            # 文本将会左对齐于x=24的一条竖线
                
        self.__startDisLineNumber = 0       # 当前将会从第 startDisLineNumber 行开始显示
        self.__startDisLetterNumber = 0     # 每行将会从第 startDisLetterNumber 个字符开始显示
    
    
    def mousePressEvent(self, event):
        cur = self.getLineRightAndTextLeftX()
        self.setLineRightAndTextLeftX( cur[0]+1 ,cur[1]+1)
        '''
        if event.button() == QtCore.Qt.LeftButton:
            self.showLineNumberAsTop(self.__startDisLineNumber+1)
        else:
            self.showLetterNumberAsLeft(self.__startDisLetterNumber+1)
        '''
    
    def paintEvent(self,event):        
        painter = QPainter(self)
        painter.setFont(self.__font)
        pen = QPen()
        
        pen.setColor( QColor(255,0,0) )        
        painter.setPen(pen)
        # 绘制行号
        for i in range( self.__startDisLineNumber,len(self.__splitedText) ):
            curY = self.__offY + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(i+1) )
            lineNumberRect.moveRight( self.__lineNumberRightXOff - lineNumberRect.x() )
            painter.drawText( lineNumberRect,0,str(i+1) )
        
        
        pen.setColor( QColor(0,0,0) )
        painter.setPen(pen)
        # 绘制文本
        for i in range( self.__startDisLineNumber,len(self.__splitedText) ):
            curY = self.__offY + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            
            curLineStr = self.__splitedText[i]
            curLineStr = curLineStr[self.__startDisLetterNumber:len(curLineStr)]
            lineStrRect = painter.boundingRect(self.__textLeftXOff, curY, 0,0,0,curLineStr)
            if event.rect().intersects( lineStrRect ) or event.rect().contains( lineStrRect ) or lineStrRect.contains( event.rect() ):
                painter.drawText(lineStrRect,0,curLineStr )    










        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs

    app = QApplication(sys.argv)

    mte = CodeTextEditWidget()
    with codecs.open( '../tmp/temp.txt','r','utf-8' ) as templateFileObj:
        mte.setText( templateFileObj.read() )
    mte.show()
    
    
    
    sys.exit( app.exec_() )



