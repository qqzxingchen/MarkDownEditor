

from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtWidgets import QWidget

from CodeEditor.MainClass.TextDocument import TextDocument
from CodeEditor.MainClass.TextCursor import TextCursor
from CodeEditor.MainClass.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF

from CodeEditor.ToolClass.EditorSettings import EditorSettings
from CodeEditor.ToolClass.RetuInfo import RetuInfo
from CodeEditor.ToolClass.SelectedTextManager import SelectedTextManager


class __EventFilter__(QtCore.QObject):
    def __init__(self,listenerFunc,parent = None):
        QtCore.QObject.__init__(self,parent)
        self.__listenerFunc = listenerFunc

    def eventFilter(self, obj, event):
        retu = self.__listenerFunc(obj,event)
        return (retu == True)


class BaseTextWidget(QWidget):
    
    # 在每次重绘的时候，该函数都将被调用，以此通知显示行号的模块(LineNumberWidget)应该显示哪些行号，显示的位置如何
    visibleLineYOffInfoChangedSignal = QtCore.pyqtSignal( list )
        
    def showLineNumberAsTop(self,lineNumber,update=True):
        suitedLineNumber = FUF.calcMidNumberByRange( 0,lineNumber,self.document().getLineCount()-1 )
        self.settings().setStartDisLineNumber(suitedLineNumber,update)
        
    def showLeftXOffAsLeft(self,xOff,update=True):
        self.settings().setStartDisLetterXOff( 0 if xOff < 0 else xOff,update )
    
    
    def __init__(self,textDocumentObj = None,settingsObj = None,parent=None):
        QWidget.__init__(self,parent)
        self.setCursor( QtCore.Qt.IBeamCursor )
        
        textDocumentObj = TextDocument() if textDocumentObj == None else textDocumentObj 
        settingsObj = EditorSettings() if settingsObj == None else settingsObj
        self.__initData( textDocumentObj,settingsObj )
        
        self.__globalEventFilter = __EventFilter__( self.__onGlobalEvents )
        QtWidgets.qApp.installEventFilter( self.__globalEventFilter )
        
        self.setText = self.__textDocument.setText
        self.getText = self.__textDocument.getText
        self.document = lambda : self.__textDocument
        self.cursor = lambda : self.__textCursor
    
    def __initData(self,textDocumentObj,settingsObj):
        # 为了代码的可读性，将部分属性值（影响文本显示的属性值）放置到EditorSettings类中
        self.__settings = settingsObj
        self.settings = lambda : self.__settings

        # 为了代码的可读性，将部分数据的操作（关于鼠标选中的文本）放置到EditorSettings类中
        self.__selectedTextManager = SelectedTextManager()
        self.selectedTextManager = lambda : self.__selectedTextManager

        self.__textDocument = textDocumentObj
        self.__textDocument.setFont(self.settings().getFont(),self.settings().getFontMetrics())

        self.__textCursor = TextCursor(self)
        self.__textCursor.cursorPosChangedSignal.connect(self.__onCursorPosChanged)
        self.__textCursor.initPos( (0,0) )
        
        self.__forceUpdateFunc = lambda *arg1,**arg2 : self.update()
        
        self.settings().fontChangedSignal.connect(self.__onFontChanged)
        self.settings().startDisLineNumberChangedSignal.connect( self.__forceUpdateFunc )
        self.settings().startDisLetterXOffChangedSignal.connect( self.__forceUpdateFunc )
        self.settings().lineTextMaxPixelChangedSignal.connect( self.__forceUpdateFunc )
        self.settings().editableChangedSignal.connect( self.__forceUpdateFunc )
        
        self.selectedTextManager().updateSignal.connect( self.__forceUpdateFunc )
    
    
    def __onGlobalEvents(self,obj,event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.__textCursor.setFocus(QtCore.Qt.MouseFocusReason)
            return True
        if event.type() == QtCore.QEvent.InputMethod:
            if obj == self.__textCursor or obj == self:
                self.insertStr(event.commitString())
                return True
    
    
    def __onFontChanged(self,newFontObj):
        self.__textDocument.setFont(self.settings().getFont(), self.settings().getFontMetrics())
        self.update()

    # 当光标的位置改变时，需要刷新原来的行以及新行
    def __onCursorPosChanged(self):
        curCursorPos = self.__textCursor.getCursorIndexPos()
        
        curXPixel = self.transGloPixelPosToCurPixelPos( self.transGloIndexPosToGloPixelPos( curCursorPos ) )[0]
        if curXPixel < 0:
            moveDistance = 0 - curXPixel
            moveDistance = (int(moveDistance / 100) + 1) * 100
            self.showLeftXOffAsLeft(self.settings().getStartDisLetterXOff()-moveDistance)
        elif curXPixel+CEGD.CursorWidth > self.width():
            moveDistance = curXPixel-self.width()
            moveDistance = (int(moveDistance / 100) + 1) * 100
            self.showLeftXOffAsLeft(self.settings().getStartDisLetterXOff()+moveDistance)
        
        curYIndex = curCursorPos[1]
        if ( curYIndex < self.settings().getStartDisLineNumber() ):
            self.showLineNumberAsTop(curYIndex)
        elif ( curYIndex >= self.settings().getStartDisLineNumber() + self.calcDisLineNumber() ):
            self.showLineNumberAsTop(curYIndex - (self.calcDisLineNumber()-1))
        else:
            self.__updateLineIndexRect( self.__textCursor.getCursorIndexPos(False)[1],self.settings().getFontMetrics().lineSpacing() )
            self.__updateLineIndexRect( curYIndex,self.settings().getFontMetrics().lineSpacing() )
                    

    # 以当前的设置为准，更新第lineIndex对应的矩形区域
    def __updateLineIndexRect(self,lineIndex,height):
        for item in self.calcAnyVisibleYOff():
            if item['lineIndex'] == lineIndex:
                self.update( 0, item['lineYOff'],self.width(),height )
                break






    # 根据光标的全局位置，计算出当前视口下光标的实际位置，返回tuple
    def transGloPixelPosToCurPixelPos(self,xyGloPixelPosTuple):
        return (xyGloPixelPosTuple[0] - self.settings().getStartDisLetterXOff(), \
                xyGloPixelPosTuple[1] - self.settings().getFontMetrics().lineSpacing() * self.settings().getStartDisLineNumber() )
        
    # 根据光标在当前视口下的位置，计算出光标的全局位置，返回tuple
    def transCurPixelPosToGloPixelPos(self,xyCurPixelPosTuple):
        return (xyCurPixelPosTuple[0] + self.settings().getStartDisLetterXOff(), \
                xyCurPixelPosTuple[1] + self.settings().getFontMetrics().lineSpacing() * self.settings().getStartDisLineNumber() )        
   
    # 根据全局的indexPos，得到全局的pixelPos
    def transGloIndexPosToGloPixelPos(self,xyIndexPosTuple):
        xIndexPos,yIndexPos = xyIndexPosTuple
        charWidthInfoArr = self.__textDocument.getLineCharWidthArrayByIndex(yIndexPos)
               
        yPixelPos = yIndexPos*self.settings().getFontMetrics().lineSpacing() + CEGD.TextYOff
        xPixelPos = 0
        for i in range(xIndexPos):
            xPixelPos += CEGD.CharDistancePixel + charWidthInfoArr[i]
        return (xPixelPos,yPixelPos)
        
    # 根据用户点击的位置，计算出光标应该处于的位置
    def transUserClickedPixelPosToIndexPos(self,xyClickedPixelPosTuple):
        x,y = xyClickedPixelPosTuple
        x = max([x,0])
        lineIndex = self.settings().getStartDisLineNumber() + int((y-CEGD.TextYOff)/self.settings().getFontMetrics().lineSpacing())
        lineIndex = FUF.calcMidNumberByRange(0, lineIndex, self.__textDocument.getLineCount()-1)
        
        charWidthArray = self.__textDocument.getLineCharWidthArrayByIndex(lineIndex)
                
        startX = 0 - self.settings().getStartDisLetterXOff()
        xIndex = 0
        while xIndex < len(charWidthArray):
            charWidth = charWidthArray[xIndex]
            startX += charWidth + CEGD.CharDistancePixel
            xIndex += 1
            if startX >= x:
                break
        if startX > x:
            if ( startX - (charWidth + CEGD.CharDistancePixel)/2 > x ):
                startX -= (charWidth + CEGD.CharDistancePixel)
                xIndex -= 1
        return RetuInfo.info( indexPos = ( xIndex,lineIndex ) , offset = x-startX )



    # 计算一共可以显示多少行
    def calcDisLineNumber(self):
        return int((self.height()-CEGD.TextYOff) / self.settings().getFontMetrics().lineSpacing())
    
    def calcMaxStartDisLineNumber(self):
        return max([ 0,self.__textDocument.getLineCount()-1-(self.calcDisLineNumber()-1) ])


    # 计算每行文本的y偏移（行号和文本的y偏移都一样）
    def calcAnyVisibleYOff(self):
        yOffArray = []
        for i in range( self.settings().getStartDisLineNumber(),self.__textDocument.getLineCount() ):
            curY = CEGD.TextYOff + self.settings().getFontMetrics().lineSpacing() * (i-self.settings().getStartDisLineNumber())
            if curY > self.height():
                break
            yOffArray.append( {'lineIndex':i,'lineYOff':curY} )
        return yOffArray
    
    

      
    def paintEvent(self,event):
        visibleLineYOffInfoArray = self.calcAnyVisibleYOff()
        self.visibleLineYOffInfoChangedSignal.emit( visibleLineYOffInfoArray )
        
        painter = QtGui.QPainter(self)
        painter.setFont(self.settings().getFont())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(CEGD.WhiteOpaqueBrush)
        painter.drawRect(0,0,self.width(),self.height())

        painter.save()
        self.__drawLineText(painter,visibleLineYOffInfoArray,event.rect())
        painter.restore()
        
        painter.save()
        self.__refreshCursor(painter,visibleLineYOffInfoArray)
        painter.restore()
                
        
    # 绘制每行文本
    def __drawLineText(self,painter,visibleLineYOffInfoArray,redrawRect):
        for item in visibleLineYOffInfoArray:
            lineYOff = item['lineYOff']
            lineIndex = item['lineIndex']
            pixmapObj = self.__textDocument.getLinePixmapByIndex(lineIndex)
            if lineYOff >= redrawRect.y() and lineYOff <= redrawRect.y() + redrawRect.height():            
                painter.drawPixmap( - self.settings().getStartDisLetterXOff() , lineYOff , pixmapObj )
        self.settings().setLineTextMaxPixel(self.__textDocument.getMaxLineWidth())


    # 绘制鼠标相关
    def __refreshCursor(self,painter,visibleLineYOffInfoArray):
        drawCursorSign = False
        for item in visibleLineYOffInfoArray:
            if item['lineIndex'] == self.__textCursor.getCursorIndexPos()[1]:     
                drawCursorSign = True
                break
        
        if drawCursorSign == False:
            self.__textCursor.hide()
            return 
        
        # 绘制光标
        cursorPos = self.transGloPixelPosToCurPixelPos( self.transGloIndexPosToGloPixelPos(self.__textCursor.getCursorIndexPos()) )
        self.__textCursor.setGeometry(cursorPos[0],cursorPos[1],CEGD.CursorWidth,self.settings().getFontMetrics().lineSpacing())

        # 绘制光标所在行高亮
        if self.selectedTextManager().getSelectedTextIndexPos() == None:
            lineTextRect = QtCore.QRect( 0,cursorPos[1],self.width(),self.settings().getFontMetrics().lineSpacing() )
            painter.fillRect( lineTextRect ,CEGD.LineSelectedBKBrush)










    