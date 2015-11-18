
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui
from PyQt5 import QtCore

from CodeEditor.TextDocument import TextDocument
from CodeEditor.TextCursor import TextCursor
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines


class CodeTextEditWidget(QWidget):
    # 其中 bool 指代的是文本改变之后，文本的行数有没有发生改变
    # 为True则表示行数发生改变
    textChangedSignal = QtCore.pyqtSignal( bool )       
    
    # 修改字体，注意，当前只支持等宽字体
    def setFont(self,fontObj = QtGui.QFont('Consolas')):
        fontObj.setBold(True)
        self.__font = fontObj
        self.__fontMetrics = QtGui.QFontMetrics(self.__font)
        self.update()
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics
    
    
    def setTextDocument(self,textDocument = None):
        if textDocument == None:
            self.__textDocument = TextDocument()
        else:
            self.__textDocument = textDocument
        self.update()
        self.textChangedSignal.emit(True)
    def getTextDocument(self):
        return self.__textDocument


    def setEditAble(self,canEdit=True):
        if canEdit == True:
            self.__editAble = True
        else:
            self.__editAble = False
    def isEditAble(self):
        return self.__editAble

    
    def setLineRightAndTextLeftX(self,lineRightX,textLeftX):
        self.__lineNumberRightXOff = lineRightX
        self.__lineTextLeftXOff = textLeftX
        self.update()
    def getLineNumberRightXOff(self):
        return self.__lineNumberRightXOff
    def getTextLeftXOff(self):
        return self.__lineTextLeftXOff
    
    
    
    
    def showLineNumberAsTop(self,lineNumber,update=True):
        if lineNumber < 0:
            self.__startDisLineNumber = 0
        elif lineNumber >= self.__textDocument.getLineCount():
            self.__startDisLineNumber = self.__textDocument.getLineCount()-1
        else:
            self.__startDisLineNumber = int(lineNumber)
        if update == True:
            self.update()
    def showLeftXOffAsLeft(self,xOff,update=True):
        if xOff < 0:
            self.__startDisLetterXOff = 0
        else:
            self.__startDisLetterXOff = int(xOff)
        if update == True:
            self.update()
        
        
        
        
        
        
        
        
        
        
        
    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.__initData()
    
    
    def __initData(self):
        self.__textDocument = TextDocument()
        self.setFont()
        self.setEditAble()

        self.__lineNumberRightXOff = 24     # 行号将会右对齐于 self.__lineNumberRightXOff 标示的一条竖线
        self.__lineTextLeftXOff = 40            # 文本将会左对齐于 self.__lineTextLeftXOff 标示的一条竖线
        
        self.__startDisLineNumber = 0       # 当前将会从第 startDisLineNumber 行开始显示
        self.__startDisLetterXOff = 0       # 每行文本将会向左偏移 startDisLetterNumber 个像素
        
        self.__cursor = TextCursor(self)
        self.__cursor.cursorVisibleChangedSignal.connect(self.onCursorVisibleChanged)
        self.__cursor.initPos( QtCore.QRect( self.__lineTextLeftXOff,CodeEditorGlobalDefines.TextYOff,2,self.__fontMetrics.ascent() ) )
        
    
    def onCursorVisibleChanged(self):
        self.update( self.__cursor.getNewPos() )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    def mousePressEvent(self, event):
        
        if event.button() == QtCore.Qt.LeftButton:
            self.showLineNumberAsTop(self.__startDisLineNumber+1)
        else:
            self.showLeftXOffAsLeft(self.__startDisLetterXOff+1)
    
    
    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        painter.setFont(self.__font)

        painter.save()
        self.__drawLineNumber(painter)
        painter.restore()
        
        painter.save()
        self.__drawLineText(painter, event.rect())
        painter.restore()
        
        self.__drawCursor(painter)
        
        QWidget.paintEvent(self,event)
    
    
    def __drawCursor(self,painter):
        painter.fillRect( self.__cursor.getNewPos(), QtCore.Qt.SolidPattern if self.__cursor.isNeedShowCursor() else QtCore.Qt.NoBrush)
        
        
    # 绘制行号        
    def __drawLineNumber(self,painter):
        pen = QtGui.QPen()
        pen.setColor( QtGui.QColor(255,0,0) )        
        painter.setPen(pen)
        for i in range( self.__startDisLineNumber,self.__textDocument.getLineCount() ):
            curY = CodeEditorGlobalDefines.TextYOff + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(i+1) )
            lineNumberRect.moveRight( self.__lineNumberRightXOff - lineNumberRect.x() )
            painter.drawText( lineNumberRect,0,str(i+1) )


    # 绘制每行文本
    def __drawLineText(self,painter,redrawRect):
        
        '''
        if isinstance(self.__textDocument.userData.get('lineCharWidthInfo'), list) == False:
            self.__textDocument.userData['lineCharWidthInfo'] = []
        lineCharWidthInfo = self.__textDocument.userData['lineCharWidthInfo']
        '''
        
        
        pen = QtGui.QPen() 
        pen.setColor( QtGui.QColor(0,0,0) )
        painter.setPen(pen)
        # 绘制文本时，需要设置裁剪区域
        painter.setClipRect( QtCore.QRect( self.__lineTextLeftXOff,0,self.width()-self.__lineTextLeftXOff,self.height() ),QtCore.Qt.IntersectClip )
        for i in range( self.__startDisLineNumber,self.__textDocument.getLineCount() ):
            curY = CodeEditorGlobalDefines.TextYOff + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            
            curLineStr = self.__textDocument.getTextByLineNumber(i)
            curXOff = self.__lineTextLeftXOff-self.__startDisLetterXOff
            for curChar in curLineStr:
                r = painter.boundingRect(curXOff,curY,0,0,0,curChar)
                if redrawRect.intersects( r ) or redrawRect.contains( r ) or r.contains( redrawRect ):
                    painter.drawText(r,0,curChar)
                curXOff += r.width() + CodeEditorGlobalDefines.CharDistancePixel
                        
            
            '''
            curLineStr = self.__textDocument.getTextByLineNumber(i)
            lineStrRect = painter.boundingRect(self.__lineTextLeftXOff-self.__startDisLetterXOff, curY, 0,0,0,curLineStr)
            if event.rect().intersects( lineStrRect ) or event.rect().contains( lineStrRect ) or lineStrRect.contains( event.rect() ):
                painter.drawText(lineStrRect,0,curLineStr )    
            '''









        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs

    app = QApplication(sys.argv)

    mte = CodeTextEditWidget()
    with codecs.open( '../tmp/temp.txt','r','utf-8' ) as templateFileObj:
        fileStr = templateFileObj.read()
        mte.setTextDocument(TextDocument(fileStr))
    mte.show()
    
    
    
    sys.exit( app.exec_() )



