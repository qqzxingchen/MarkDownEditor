

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
    
    
    
    
    def onSelectedTextChanged(self):
        self.update()
    
    def onFontChanged(self,newFontObj):
        self.__textDocument.setFont(self.settings().getFont(), self.settings().getFontMetrics())
        self.update()
    
    # 当光标的位置改变时，需要刷新原来的行以及新行
    def onCursorPosChanged(self):
        self.update()
    
    def onStartDisLineNumberChanged(self,curV):
        self.update()

    def onStartDisLetterXOffChanged(self,curV):
        self.update()

    def onLineTextMaxPixelChanged(self,curV):
        self.update()

    def onEditableChanged(self,curState):
        self.update()
    
    
    
    
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
        self.__textCursor.cursorPosChangedSignal.connect(self.onCursorPosChanged)
        self.__textCursor.initPos( (0,0) )
        
        self.settings().fontChangedSignal.connect(self.onFontChanged)
        self.settings().startDisLineNumberChangedSignal.connect( self.onStartDisLineNumberChanged )
        self.settings().startDisLetterXOffChangedSignal.connect( self.onStartDisLetterXOffChanged )
        self.settings().lineTextMaxPixelChangedSignal.connect( self.onLineTextMaxPixelChanged )
        self.settings().editableChangedSignal.connect( self.onEditableChanged )
        
        self.selectedTextManager().selectedTextChangedSignal.connect( self.onSelectedTextChanged )
    
    def __onGlobalEvents(self,obj,event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.__textCursor.setFocus(QtCore.Qt.MouseFocusReason)
            return True
        if event.type() == QtCore.QEvent.InputMethod:
            if obj == self.__textCursor or obj == self:
                self.insertStr(event.commitString())
                return True
    
    



                    

    # 以当前的设置为准，更新第lineIndex对应的矩形区域
    def updateLineIndexRect(self,lineIndex,height):
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
    
    
    # 子类通过重写beforeDraw、afterDraw来实现对界面的修改，而不要直接重写paintEvent
    # 之所以子类尽量不要重写paintEvent，是因为子类中大部分情况是为了高亮某段文本
    #     如果先绘制文本，再用半透明的高亮画刷绘制高亮区域，会导致之前绘制的文本的颜色大幅度变浅，影响用户查看
    #     而如果先用高亮画刷绘制高亮区域，再绘制文本即可解决上述问题
    # 如果子类的绘制可以晚于文本的绘制，并不会造成不利影响，那么子类重写paintEvent也是可以的
    def beforePaint(self,painter):
        pass
    
    def afterPaint(self,painter):
        pass

    def paintEvent(self,event):
        visibleLineYOffInfoArray = self.calcAnyVisibleYOff()
        self.visibleLineYOffInfoChangedSignal.emit( visibleLineYOffInfoArray )
        
        painter = QtGui.QPainter(self)
        painter.setFont(self.settings().getFont())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(CEGD.WhiteOpaqueBrush)
        painter.drawRect(0,0,self.width(),self.height())
        
        painter.save()
        self.beforePaint(painter)
        painter.restore()
        
        painter.save()
        self.__drawLineText(painter,visibleLineYOffInfoArray,event.rect())
        painter.restore()
        
        painter.save()
        self.__refreshCursor(painter,visibleLineYOffInfoArray)
        painter.restore()

        painter.save()
        self.afterPaint(painter)
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










    