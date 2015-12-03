
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui
from PyQt5 import QtCore

from CodeEditor.TextDocument import TextDocument
from CodeEditor.TextCursor import TextCursor
from CodeEditor.CodeEditorGlobalDefines import CEGlobalDefines




class CodeTextEditWidget(QWidget):
    # 当文本内容发生改变时，该信号将会被发射
    textChangedSignal = QtCore.pyqtSignal( TextDocument)
    
    # 当绘制文本时，单行文本最大像素长度改变时，该信号被发射
    # int 指代的是新的最大宽度
    lineStrLengthChangedSignal = QtCore.pyqtSignal( int )
    
    
    # 修改字体，注意，当前只支持等宽字体
    def setFont(self,fontObj = QtGui.QFont('Consolas',11)):
        fontObj.setBold(True)
        self.__font = fontObj
        self.__textDocument.setFont(self.__font)
        self.__fontMetrics = self.__textDocument.getFontMetrics()
        self.update()
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics
    
    
    def setText(self,text):
        self.__textDocument.setText(text)
        self.textChangedSignal.emit(self.__textDocument)
    def getText(self):
        return self.__textDocument.getText()


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
        self.setAttribute( QtCore.Qt.WA_InputMethodEnabled,True )           # 使得窗口可以调用输入法进行输入
        self.__initData()
    
    
    def __initData(self):
        self.__textDocument = TextDocument()
        self.setFont()
        self.setEditAble()

        self.__lineNumberRightXOff = 44     # 行号将会右对齐于 self.__lineNumberRightXOff 标示的一条竖线
        self.__lineTextLeftXOff = 64        # 文本将会左对齐于 self.__lineTextLeftXOff 标示的一条竖线
        
        self.__startDisLineNumber = 0       # 当前将会从第 startDisLineNumber 行开始显示
        self.__startDisLetterXOff = 0       # 每行文本将会向左偏移 startDisLetterNumber 个像素
        
        self.__lineTextMaxPixels = 0         # 当前文本在绘制时，最大的像素数（横轴滚动条将会根据它设置的maxrange）
        
        self.__cursor = TextCursor(self)
        self.__cursor.cursorPosChangedSignal.connect(self.__onCursorPosChanged)
        self.__cursor.initPos( self.__transGloPosByCurPos(self.__lineTextLeftXOff,CEGlobalDefines.TextYOff),(0,0) )
        

    
    
        
    def __resetLineStrMaxPixels(self,newPixelLength):
        if self.__lineTextMaxPixels != newPixelLength:
            self.__lineTextMaxPixels = newPixelLength
            self.lineStrLengthChangedSignal.emit(self.__lineTextMaxPixels)
    
    # 根据光标的全局位置，计算出当前视口下光标的实际位置
    # 返回tuple
    def __transCurPosByGloPos(self,x,y):
        return (x + self.__lineTextLeftXOff - self.__startDisLetterXOff, \
                y - self.__fontMetrics.lineSpacing() * self.__startDisLineNumber)
        
    # 根据光标在当前视口下的位置，计算出光标的全局位置
    # 返回tuple
    def __transGloPosByCurPos(self,x,y):
        return (x - (self.__lineTextLeftXOff - self.__startDisLetterXOff), \
                y + self.__fontMetrics.lineSpacing() * self.__startDisLineNumber )




    # 当光标的位置改变时，需要刷新原来的行以及新行
    def __onCursorPosChanged(self):
        self.__updateLineIndexRect( self.__cursor.getCursorIndexPos(False)[1],self.__fontMetrics.lineSpacing() )
        self.__updateLineIndexRect( self.__cursor.getCursorIndexPos()[1],self.__fontMetrics.lineSpacing() )


    # 以当前的设置为准，更新第lineIndex对应的矩形区域
    def __updateLineIndexRect(self,lineIndex,height):
        for item in self.__calcAnyVisibleYOff():
            if item['lineIndex'] == lineIndex:
                self.update( 0, item['lineYOff'],self.width(),height )
                break
    
    
    
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__onLeftMousePressed(event.x(),event.y())
        elif event.button() == QtCore.Qt.RightButton:
            newPointSize = self.__font.pointSize()+1
            font = QtGui.QFont( "Consolas",newPointSize )
            self.setFont(font)
            
    def __onLeftMousePressed(self, x, y):
        y = max([y,CEGlobalDefines.TextYOff])
        x = max([x,self.__lineTextLeftXOff])
        
        lineIndex = self.__startDisLineNumber + int((y-CEGlobalDefines.TextYOff)/self.__fontMetrics.lineSpacing())
        if lineIndex > self.__textDocument.getLineCount()-1:
            lineIndex = self.__textDocument.getLineCount()-1
                
        lineTopYOff = (lineIndex-self.__startDisLineNumber)*self.__fontMetrics.lineSpacing() + CEGlobalDefines.TextYOff
        charWidthArray = self.__textDocument.getCharWidthArrayByIndex(lineIndex)
                
        startX = self.__lineTextLeftXOff - self.__startDisLetterXOff
        xIndex = 0
        
        while xIndex < len(charWidthArray):
            charWidth = charWidthArray[xIndex]
            startX += charWidth + CEGlobalDefines.CharDistancePixel
            xIndex += 1
            if startX >= x:
                break
        if startX > x:
            if ( startX - (charWidth + CEGlobalDefines.CharDistancePixel)/2 > x ):
                startX -= (charWidth + CEGlobalDefines.CharDistancePixel)
                xIndex -= 1
        
        cursorPos = self.__transGloPosByCurPos( startX,lineTopYOff )
        self.__cursor.setGlobalCursorPos( cursorPos,( xIndex,lineIndex ) )


    def keyPressEvent(self, event):
        if event.key() == 0x31:
            xPos,yPos = self.__cursor.getCursorIndexPos()
            self.__textDocument.insertTextWithoutLineBreak( self.__cursor.getCursorIndexPos() , 'xc')
            self.__updateLineIndexRect(yPos, self.__fontMetrics.lineSpacing())
        elif event.key() == 0x32:
            xPos,yPos = self.__cursor.getCursorIndexPos()
            self.__textDocument.insertLineBreak( self.__cursor.getCursorIndexPos() )
            self.__updateLineIndexRect(yPos, self.height())
        elif event.key() == 0x33:
            xPos,yPos = self.__cursor.getCursorIndexPos()
            self.__textDocument.deleteText(self.__cursor.getCursorIndexPos(),1 )        
            self.__updateLineIndexRect(yPos, self.height())

            
            
            

    



    # 计算每行文本的y偏移（行号和文本的y偏移都一样）
    def __calcAnyVisibleYOff(self):
        yOffArray = []
        for i in range( self.__startDisLineNumber,self.__textDocument.getLineCount() ):
            curY = CEGlobalDefines.TextYOff + self.__fontMetrics.lineSpacing() * (i-self.__startDisLineNumber)
            if curY > self.height():
                break
            yOffArray.append( {'lineIndex':i,'lineYOff':curY} )
        return yOffArray
    
      

    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        painter.setFont(self.__font)
        
        visibleLineYOffInfoArray = self.__calcAnyVisibleYOff()
        
        painter.save()
        self.__drawLineNumber(painter,visibleLineYOffInfoArray)
        painter.restore()
        
        painter.save()
        self.__drawLineText(painter,visibleLineYOffInfoArray,event.rect())
        painter.restore()
        
        painter.save()
        self.__refreshCursor(painter,visibleLineYOffInfoArray)
        painter.restore()
                
        QWidget.paintEvent(self,event)


        
    # 绘制行号        
    def __drawLineNumber(self,painter,visibleLineYOffInfoArray):
        painter.setPen(CEGlobalDefines.LineNumberPen)   
        for item in visibleLineYOffInfoArray:
            curY = item['lineYOff']
            index = item['lineIndex']
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(index+1) )
            lineNumberRect.moveRight( self.__lineNumberRightXOff - lineNumberRect.x() )
            painter.drawText( lineNumberRect,0,str(index+1) )


    # 绘制每行文本
    def __drawLineText(self,painter,visibleLineYOffInfoArray,redrawRect):
        
        # 绘制文本时，需要设置裁剪区域
        painter.setClipRect( QtCore.QRect( self.__lineTextLeftXOff,0,self.width()-self.__lineTextLeftXOff,self.height() ),QtCore.Qt.IntersectClip )
        for item in visibleLineYOffInfoArray:
            lineYOff = item['lineYOff']
            lineIndex = item['lineIndex']
            pixmapObj = self.__textDocument.getNormalLineTextPixmapByIndex(lineIndex)
            if lineYOff >= redrawRect.y() and lineYOff <= redrawRect.y() + redrawRect.height():            
                painter.drawPixmap( self.__lineTextLeftXOff - self.__startDisLetterXOff , lineYOff,pixmapObj )

        self.__resetLineStrMaxPixels(self.__textDocument.getMaxLineWidth())
            
        
    # 绘制鼠标相关
    def __refreshCursor(self,painter,visibleLineYOffInfoArray):
        drawCursorSign = False
        for item in visibleLineYOffInfoArray:
            if item['lineIndex'] == self.__cursor.getCursorIndexPos()[1]:     
                drawCursorSign = True
        
        if drawCursorSign == False:
            self.__cursor.hide()
        else:
            painter.setClipRect( QtCore.QRect( self.__lineTextLeftXOff,0,self.width()-self.__lineTextLeftXOff,self.height() ),QtCore.Qt.IntersectClip )
            
            cursorPos = self.__transCurPosByGloPos( self.__cursor.getCursorPixelPos()[0],self.__cursor.getCursorPixelPos()[1] )
            self.__cursor.setGeometry(cursorPos[0],cursorPos[1],CEGlobalDefines.CursorWidth,self.__fontMetrics.lineSpacing())
                    
            lineTextRect = QtCore.QRect( self.__lineTextLeftXOff,cursorPos[1], \
                                         self.width()-self.__lineTextLeftXOff,self.__fontMetrics.lineSpacing() )
            painter.fillRect( lineTextRect ,CEGlobalDefines.LineSelectedBKBrush)







        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs

    app = QApplication(sys.argv)

    mce = CodeTextEditWidget()
    with codecs.open( '../tmp/temp.txt','r','utf-8' ) as templateFileObj:
        fileStr = templateFileObj.read()
        mce.setText(fileStr)
    mce.show()
    mce.resize( QtCore.QSize( 600,400 ) )
    
    
    
    sys.exit( app.exec_() )



