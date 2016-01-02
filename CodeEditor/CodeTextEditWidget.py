
import sys

from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QWidget

from CodeEditor.TextDocument import TextDocument
from CodeEditor.TextCursor import TextCursor
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.EditorSettings import EditorSettings



class __LineNumberWidget__(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)
    


class __LineTextWidget(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)





class CodeTextEditWidget(QWidget):
    # 当文本内容发生改变时，该信号将会被发射
    textChangedSignal = QtCore.pyqtSignal( TextDocument)
    
    # 当按下Ctrl+字母键时，onQuickCtrlKey被发射
    # 当按下Alt+字母键时，onQuickAltKey被发射
    onQuickCtrlKey = QtCore.pyqtSignal( QtCore.Qt.Key )
    onQuickAltKey = QtCore.pyqtSignal( QtCore.Qt.Key )



    def setText(self,text):
        self.__textDocument.setText(text)
        self.textChangedSignal.emit(self.__textDocument)
    def getText(self):
        return self.__textDocument.getText()



    def showLineNumberAsTop(self,lineNumber,update=True):
        suitedLineNumber = FUF.calcMidNumberByRange( 0,lineNumber,self.__textDocument.getLineCount()-1 )
        self.setStartDisLineNumber(suitedLineNumber,update)
        
    def showLeftXOffAsLeft(self,xOff,update=True):
        self.setStartDisLetterXOff( 0 if xOff < 0 else xOff,update )
        
    
    # 将本次选中的文本与上次选中的文本进行合并
    def setSelectTextByIndexPos(self,startIndexPosTuple,endIndexPosTuple,update = True):
        if self.selectedTextIndexPos != None:
            if FUF.isIndexPosEqual( startIndexPosTuple,self.selectedTextIndexPos[0] ) and \
                FUF.isIndexPosEqual( endIndexPosTuple,self.selectedTextIndexPos[1] ):
                return
        if FUF.isIndexPosEqual( startIndexPosTuple,endIndexPosTuple ) == True:
            self.selectedTextIndexPos = None
        else:
            self.selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)
        if update == True:
            self.update()
        
    def addSelectTextByIndexPos(self,startIndexPosTuple,endIndexPosTuple,update = True):
        if self.selectedTextIndexPos == None:
            self.selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)
        else:
            if FUF.isIndexPosEqual(self.selectedTextIndexPos[1],startIndexPosTuple ):
                self.selectedTextIndexPos = ( self.selectedTextIndexPos[0],endIndexPosTuple )
            else:
                self.selectedTextIndexPos = ( endIndexPosTuple,self.selectedTextIndexPos[1] )
        if FUF.isIndexPosEqual(self.selectedTextIndexPos[0],self.selectedTextIndexPos[1]):
            self.selectedTextIndexPos = None
        if update == True:
            self.update()
    def getSelectTextByIndexPos(self):
        return self.selectedTextIndexPos
    def clearSelectText(self,update = True):
        if self.selectedTextIndexPos != None:
            self.selectedTextIndexPos = None
            if update == True:
                self.update()
    def deleteSelectText(self,update = True):
        if self.selectedTextIndexPos != None:
            selectedStart = self.getSelectTextByIndexPos()[0]
            selectedEnd = self.getSelectTextByIndexPos()[1]
            sortedInfoDict = FUF.sortedIndexPos( selectedStart , selectedEnd )
            self.__textCursor.setGlobalCursorPos( sortedInfoDict['first'])
            value = self.__textDocument.calcIndexPosDistance(selectedStart,selectedEnd)            
            self.__textDocument.deleteText(self.__textCursor.getCursorIndexPos(), value)
            self.clearSelectText(update)
    

    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.__initData()
        self.setCursorFocusOn = lambda event: self.__textCursor.setFocus(QtCore.Qt.MouseFocusReason)
        
        self.setCursor( QtCore.Qt.IBeamCursor )
        
        
        self.onQuickCtrlKey.connect(self.temp)
    def temp(self,key):
        if key == QtCore.Qt.Key_Z:
            self.__textDocument.redoOneStep()
            cursorIndexPos = self.__textCursor.getCursorIndexPos()
            if self.__textDocument.isIndexPosValid(cursorIndexPos) == False:
                self.__textCursor.setGlobalCursorPos( self.__textDocument.formatIndexPos(cursorIndexPos) )
            self.clearSelectText(False)
            self.update()
        
        
    
    
    
    

    def __initData(self):
        # 为了代码的可读性，将部分属性值（影响文本显示的属性值）放置到EditorSettings类中。然后将类的方法定向到本类中
        self.__settings = EditorSettings()
        for funcName in EditorSettings.getFuncNames + EditorSettings.setFuncNames + EditorSettings.signalNames:
            setattr(self, funcName, getattr(self.__settings, funcName) )
    
        self.__textDocument = TextDocument()
        self.__textDocument.setFont(self.getFont(),self.getFontMetrics())
        
        self.__textCursor = TextCursor(self)
        self.__textCursor.cursorPosChangedSignal.connect(self.__onCursorPosChanged)
        self.__textCursor.initPos( (0,0) )
        
        self.selectedTextIndexPos = None
        
        self.fontChangedSignal.connect(self.__onFontChanged)
        self.lineNumberRightXOffChangedSignal.connect(lambda v: self.update())
        self.lineTextLeftXOffChangedSignal.connect(lambda v: self.update())
        self.startDisLineNumberChangedSignal.connect(lambda v: self.update())
        self.startDisLetterXOffChangedSignal.connect(lambda v: self.update())
        self.lineTextMaxPixelChangedSignal.connect(lambda v: self.update())
        self.editableChangedSignal.connect(lambda v: self.update())
        
    
    def __onFontChanged(self,newFontObj):
        self.__textDocument.setFont(self.getFont(), self.getFontMetrics())
        cursorIndexPos = self.__textCursor.getCursorIndexPos()
        self.__textCursor.setGlobalCursorPos(cursorIndexPos )
        self.update()
    
    
    
    # 当光标的位置改变时，需要刷新原来的行以及新行
    def __onCursorPosChanged(self):
        curCursorPos = self.__textCursor.getCursorIndexPos()
        
        curXPixel = self.__transGloPixelPosToCurPixelPos( self.__transGloIndexPosToGloPixelPos( curCursorPos ) )[0]
        if curXPixel < self.getLineTextLeftXOff():
            moveDistance = self.getLineTextLeftXOff() - curXPixel
            moveDistance = (int(moveDistance / 100) + 1) * 100
            self.showLeftXOffAsLeft(self.getStartDisLetterXOff()-moveDistance,False)
        elif curXPixel+CEGD.CursorWidth+20 > self.width():
            moveDistance = curXPixel-self.width()
            moveDistance = (int(moveDistance / 100) + 1) * 100
            self.showLeftXOffAsLeft(self.getStartDisLetterXOff()+moveDistance, False)
        
        
        curYIndex = curCursorPos[1]
        if ( curYIndex < self.getStartDisLineNumber() ):
            self.showLineNumberAsTop(curYIndex)
        elif ( curYIndex >= self.getStartDisLineNumber() + self.__calcDisLineNumber() ):
            self.showLineNumberAsTop(curYIndex - (self.__calcDisLineNumber()-1))
        else:
            self.__updateLineIndexRect( self.__textCursor.getCursorIndexPos(False)[1],self.getFontMetrics().lineSpacing() )
            self.__updateLineIndexRect( curYIndex,self.getFontMetrics().lineSpacing() )
                    

    # 以当前的设置为准，更新第lineIndex对应的矩形区域
    def __updateLineIndexRect(self,lineIndex,height):
        for item in self.__calcAnyVisibleYOff():
            if item['lineIndex'] == lineIndex:
                self.update( 0, item['lineYOff'],self.width(),height )
                break
    
    
    
    
    
    # leftMousePressed 和 leftMousePressed_curCursor只在以下三个函数使用，用来记录一些状态值
    def mousePressEvent(self, event):
        self.clearSelectText()
        if event.button() == QtCore.Qt.LeftButton:
            self.__textCursor.setGlobalCursorPos(self.__transUserClickedPixelPosToIndexPos((event.x(),event.y())))
            self.setUserDataByKey('leftMousePressed',True)
            self.setUserDataByKey('leftMousePressed_curCursor',self.__textCursor.getCursorIndexPos())
        elif event.button() == QtCore.Qt.RightButton:
            font = QtGui.QFont( "Consolas",self.getFont().pointSize()+1 )
            font.setBold(True)
            self.setFont(font)

    def mouseMoveEvent(self, event):
        if self.getUserDataByKey('leftMousePressed') == True:
            indexPos = self.__transUserClickedPixelPosToIndexPos( (event.x(),event.y()) )
            self.__textCursor.setGlobalCursorPos( indexPos )
            self.setSelectTextByIndexPos( self.getUserDataByKey('leftMousePressed_curCursor'),indexPos )
        
    def mouseReleaseEvent(self, event):
        self.setUserDataByKey('leftMousePressed',None)
        self.setUserDataByKey('leftMousePressed_curCursor',None)

    








    def __onDirectionKey(self,event):
        key = event.key()
        modifiers = event.modifiers()
        
        oldCursorIndexPos = self.__textCursor.getCursorIndexPos()
        if ( FUF.hasModifier(modifiers) == False ) or ( FUF.hasCtrlModifier(modifiers) == False ):
            dictMap = { str(QtCore.Qt.Key_Left) :self.__textDocument.moveIndexPosLeft   , \
                        str(QtCore.Qt.Key_Right):self.__textDocument.moveIndexPosRight  , \
                        str(QtCore.Qt.Key_Up)   :self.__textDocument.moveIndexPosUp     , \
                        str(QtCore.Qt.Key_Down) :self.__textDocument.moveIndexPosDown  }
            newCursorIndexPos = dictMap[str(key)](oldCursorIndexPos)

        elif FUF.hasCtrlModifier(modifiers):
            if key == QtCore.Qt.Key_Up:
                self.showLineNumberAsTop(self.getStartDisLineNumber()-1)
                return 
            elif key == QtCore.Qt.Key_Down:
                self.showLineNumberAsTop(self.getStartDisLineNumber()+1)
                return 
            
            if key == QtCore.Qt.Key_Left:
                newCursorIndexPos = self.__textDocument.moveIndexPosLeftByWord(oldCursorIndexPos)
            elif key == QtCore.Qt.Key_Right:
                newCursorIndexPos = self.__textDocument.moveIndexPosRightByWord(oldCursorIndexPos)
        
        
        self.__textCursor.setGlobalCursorPos(newCursorIndexPos)
        if FUF.hasShiftModifier(event.modifiers()) == True:
            self.addSelectTextByIndexPos(oldCursorIndexPos, newCursorIndexPos)
        else:
            self.clearSelectText()
        self.update()
        
        
    
    def __onDeleteKey(self,event):
        if self.getSelectTextByIndexPos() != None:
            self.deleteSelectText(True)
            return 
        curCursorIndexPos = self.__textCursor.getCursorIndexPos()
        if FUF.hasModifier(event.modifiers()) == False:
            if event.key() == QtCore.Qt.Key_Delete:
                newCursorIndexPos = self.__textDocument.moveIndexPosRight(curCursorIndexPos)
            else:
                newCursorIndexPos = self.__textDocument.moveIndexPosLeft(curCursorIndexPos)
        elif FUF.onlyCtrlModifier(event.modifiers()):
            if event.key() == QtCore.Qt.Key_Delete:
                newCursorIndexPos = self.__textDocument.moveIndexPosRightByWord(curCursorIndexPos)
            else:
                newCursorIndexPos = self.__textDocument.moveIndexPosLeftByWord(curCursorIndexPos)
        else:
            return 

        distance = self.__textDocument.calcIndexPosDistance(curCursorIndexPos, newCursorIndexPos, False)
        if distance > 0:
            self.__textCursor.setGlobalCursorPos(curCursorIndexPos)
            self.__textDocument.deleteText(curCursorIndexPos,distance )
        elif distance < 0:
            self.__textCursor.setGlobalCursorPos(newCursorIndexPos)
            self.__textDocument.deleteText(newCursorIndexPos,-distance )
        self.update()
    
    def __onDisplayCharKey(self,event):
        indexPos = self.__textDocument.insertText(self.__textCursor.getCursorIndexPos(), event.text())
        self.__textCursor.setGlobalCursorPos(indexPos)
        self.update()
    
    def __onDisplayLetterKey(self,event):
        if (FUF.hasModifier(event.modifiers()) == False) or (FUF.onlyShiftModifier(event.modifiers()) == True):        
            indexPos = self.__textDocument.insertText(self.__textCursor.getCursorIndexPos(), event.text())
            self.__textCursor.setGlobalCursorPos(indexPos)
            self.update()
        elif FUF.onlyCtrlModifier(event.modifiers()):
            self.onQuickCtrlKey.emit(event.key())
        elif FUF.onlyAltModifier(event.modifiers()):
            self.onQuickAltKey.emit(event.key())
        
    
    def __onEnterKey(self,event):
        self.deleteSelectText(False)
        
        curCursorPos = self.__textCursor.getCursorIndexPos()
        cursorLeftText = self.__textDocument.getLineTextByIndex(curCursorPos[1])[0:curCursorPos[0]]
                
        unvisibleSearcher = TextDocument.UnvisibleCharSearcher
        matchObj = unvisibleSearcher.match(cursorLeftText)
        spaceNumber = matchObj.span()[1] - matchObj.span()[0] if matchObj != None else 0
        
        indexPos = self.__textDocument.insertText(self.__textCursor.getCursorIndexPos(), '\n' + ' '*spaceNumber )
        self.__textCursor.setGlobalCursorPos(indexPos)
        self.update()
    
    def __onTabKey(self,event):
        if self.getSelectTextByIndexPos() == None:        
            insertSpaceLen = 4 - (self.__textCursor.getCursorIndexPos()[0] % 4)
            indexPos = self.__textDocument.insertText(self.__textCursor.getCursorIndexPos(), ' '*insertSpaceLen)
            self.__textCursor.setGlobalCursorPos(indexPos)
        else:
            curSelectedIndexPos = self.getSelectTextByIndexPos()
            retuSortedPoses = FUF.sortedIndexPos( curSelectedIndexPos[0],curSelectedIndexPos[1])
            
            affectedLineIndexList = list(range( retuSortedPoses['first'][1],retuSortedPoses['second'][1]+1 ))
            for lineIndex in affectedLineIndexList:
                self.__textDocument.insertText( (0,lineIndex),' '*CEGD.spaceToInsertTOL )
            
            curCursorPos = self.__textCursor.getCursorIndexPos()
            if affectedLineIndexList.count(curCursorPos[1]) != 0:
                self.__textCursor.setGlobalCursorPos( (curCursorPos[0]+CEGD.spaceToInsertTOL,curCursorPos[1]) )            
            self.setSelectTextByIndexPos( (curSelectedIndexPos[0][0]+CEGD.spaceToInsertTOL,curSelectedIndexPos[0][1]) ,\
                                          (curSelectedIndexPos[1][0]+CEGD.spaceToInsertTOL,curSelectedIndexPos[1][1]) , False)
            
        self.update()
    
    
    def __onPageKey(self,event):
        if FUF.hasModifier(event.modifiers()) == False:
            if event.key() == QtCore.Qt.Key_PageUp:
                newLineNumber = max([ self.getStartDisLineNumber()-self.__calcDisLineNumber(),0 ])
            elif event.key() == QtCore.Qt.Key_PageDown:
                newLineNumber = min([ self.getStartDisLineNumber()+self.__calcDisLineNumber(),self.__textDocument.getLineCount()-1 ])
        else:
            if FUF.onlyCtrlModifier(event.modifiers()):
                if event.key() == QtCore.Qt.Key_PageUp:
                    newLineNumber = 0
                elif event.key() == QtCore.Qt.Key_PageDown:
                    newLineNumber = self.__calcMaxStartDisLineNumber()
            else:
                return 
        
        curIndexPos = self.__textCursor.getCursorIndexPos()
        newIndexPos = self.__textDocument.formatIndexPos(  (curIndexPos[0],curIndexPos[1] - (self.getStartDisLineNumber() - newLineNumber))  )
        self.showLineNumberAsTop( newLineNumber )
        self.__textCursor.setGlobalCursorPos( newIndexPos )
    
    def __onHomeEndKey(self,event):
        if FUF.hasModifier(event.modifiers()) == False:
            curIndexPos = self.__textCursor.getCursorIndexPos()
            if event.key() == QtCore.Qt.Key_Home:
                newIndexPos = ( 0,curIndexPos[1] )
            else:
                newIndexPos = ( len(self.__textDocument.getLineTextByIndex(curIndexPos[1])),curIndexPos[1] )
            self.__textCursor.setGlobalCursorPos( newIndexPos )
        else:
            if FUF.onlyCtrlModifier(event.modifiers()):
                if event.key() == QtCore.Qt.Key_Home:
                    lineIndex = 0
                    newIndexPos = ( 0,0 )
                else:
                    lineIndex = self.__calcMaxStartDisLineNumber()
                    lineCount = self.__textDocument.getLineCount()-1
                    newIndexPos = ( len(self.__textDocument.getLineTextByIndex(lineCount)),lineCount )
                self.__textCursor.setGlobalCursorPos( newIndexPos )
                self.showLineNumberAsTop(lineIndex)
                

        
    
    
    
    def keyPressEvent(self, event):
        #print (hex(event.key()).upper(), hex(ord(event.text()))   )
        
        self.__textDocument.startRecord()
        
        if FUF.isEventKeyIsDirectionKey(event.key()):
            self.__onDirectionKey(event)
        
        # BackSpace和Delete键            
        elif FUF.isEventKeyIsDeleteKey(event.key()):
            self.__onDeleteKey(event)
        
        # enter键
        elif FUF.isEventKeyIsEnterKey(event.key()):
            self.__onEnterKey(event)
            
        # tab键
        elif FUF.isEventKeyIsTabKey(event.key()):
            self.__onTabKey(event)
                
        # 数字键、其它可见字符
        elif FUF.isEventKeyIsNumber(event.key()) or FUF.isSingleCharKey(event.key()):
            self.__onDisplayCharKey(event)
        # 字母
        elif FUF.isEventKeyIsChar(event.key()):
            self.__onDisplayLetterKey(event)
        
        # PageUp、PageDown、Home、End
        elif FUF.isEventKeyIsPageUpDownKey(event.key()):
            self.__onPageKey(event)
            
        elif FUF.isEventKeyIsHomeEndKey(event.key()):
            self.__onHomeEndKey(event)


        self.__textDocument.endRecord()










    
    def insertStr(self,text):
        if len(text) == 0:
            return
        self.__textDocument.startRecord()
        indexPos = self.__textDocument.insertText(self.__textCursor.getCursorIndexPos(),text)  
        self.__textDocument.endRecord()
        self.__textCursor.setGlobalCursorPos(indexPos)
        self.update()
    
        
        
    # 根据光标的全局位置，计算出当前视口下光标的实际位置
    # 返回tuple
    def __transGloPixelPosToCurPixelPos(self,xyGloPixelPosTuple):
        return (xyGloPixelPosTuple[0] + self.getLineTextLeftXOff() - self.getStartDisLetterXOff(), \
                xyGloPixelPosTuple[1] - self.getFontMetrics().lineSpacing() * self.getStartDisLineNumber() )
        
    # 根据光标在当前视口下的位置，计算出光标的全局位置
    # 返回tuple
    def __transCurPixelPosToGloPixelPos(self,xyCurPixelPosTuple):
        return (xyCurPixelPosTuple[0] - (self.getLineTextLeftXOff() - self.getStartDisLetterXOff()), \
                xyCurPixelPosTuple[1] + self.getFontMetrics().lineSpacing() * self.getStartDisLineNumber() )        
   
    # 根据全局的indexPos，得到全局的pixelPos
    def __transGloIndexPosToGloPixelPos(self,xyIndexPosTuple):
        xIndexPos = xyIndexPosTuple[0]
        yIndexPos = xyIndexPosTuple[1]
        charWidthInfoArr = self.__textDocument.getCharWidthArrayByIndex(yIndexPos)
               
        yPixelPos = yIndexPos*self.getFontMetrics().lineSpacing() + CEGD.TextYOff
        xPixelPos = 0
        for i in range(xIndexPos):
            xPixelPos += CEGD.CharDistancePixel + charWidthInfoArr[i]
        return (xPixelPos,yPixelPos)
        
    # 根据用户点击的位置，计算出光标应该处于的位置
    def __transUserClickedPixelPosToIndexPos(self,xyClickedPixelPosTuple):
        x = max([xyClickedPixelPosTuple[0],self.getLineTextLeftXOff()])
        y = max([xyClickedPixelPosTuple[1],CEGD.TextYOff])
        
        lineIndex = self.getStartDisLineNumber() + int((y-CEGD.TextYOff)/self.getFontMetrics().lineSpacing())
        if lineIndex > self.__textDocument.getLineCount()-1:
            lineIndex = self.__textDocument.getLineCount()-1
        
        charWidthArray = self.__textDocument.getCharWidthArrayByIndex(lineIndex)
                
        startX = self.getLineTextLeftXOff() - self.getStartDisLetterXOff()
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
        return ( xIndex,lineIndex )
        #return RetuInfo.info( indexPos = ( xIndex,lineIndex ) , isOnTheLeftOfIndexPos =  )



    # 计算一共可以显示多少行
    def __calcDisLineNumber(self):
        return int((self.height()-CEGD.TextYOff) / self.getFontMetrics().lineSpacing())
    
    def __calcMaxStartDisLineNumber(self):
        return max([ 0,self.__textDocument.getLineCount()-1-(self.__calcDisLineNumber()-1) ])


    # 计算每行文本的y偏移（行号和文本的y偏移都一样）
    def __calcAnyVisibleYOff(self):
        yOffArray = []
        for i in range( self.getStartDisLineNumber(),self.__textDocument.getLineCount() ):
            curY = CEGD.TextYOff + self.getFontMetrics().lineSpacing() * (i-self.getStartDisLineNumber())
            if curY > self.height():
                break
            yOffArray.append( {'lineIndex':i,'lineYOff':curY} )
        return yOffArray
    
    

      

    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        painter.setFont(self.getFont())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(CEGD.WhiteOpaqueBrush)
        painter.drawRect(self.getLineTextLeftXOff(),0,self.width(),self.height())
        
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
                
        


        
    # 绘制行号
    def __drawLineNumber(self,painter,visibleLineYOffInfoArray):
        painter.setPen(CEGD.LineNumberPen)   
        for item in visibleLineYOffInfoArray:
            curY = item['lineYOff']
            index = item['lineIndex']
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(index+1) )
            lineNumberRect.moveRight( self.getLineNumberRightXOff() - lineNumberRect.x() )
            painter.drawText( lineNumberRect,0,str(index+1) )


    # 绘制每行文本
    def __drawLineText(self,painter,visibleLineYOffInfoArray,redrawRect):
        
        # 绘制文本时，需要设置裁剪区域
        painter.setClipRect( self.getLineTextLeftXOff(),CEGD.TextYOff, \
                             self.width()-self.getLineTextLeftXOff(),self.height(), \
                             QtCore.Qt.IntersectClip )
        for item in visibleLineYOffInfoArray:
            lineYOff = item['lineYOff']
            lineIndex = item['lineIndex']
            pixmapObj = self.__textDocument.getNormalLineTextPixmapByIndex(lineIndex)
            if lineYOff >= redrawRect.y() and lineYOff <= redrawRect.y() + redrawRect.height():            
                painter.drawPixmap( self.getLineTextLeftXOff() - self.getStartDisLetterXOff() , lineYOff,pixmapObj )

        self.setLineTextMaxPixel(self.__textDocument.getMaxLineWidth())
        self.__highlightSelectedText(painter)
        
        
    def __highlightSelectedText(self,painter):
        painter.setClipRect( self.getLineTextLeftXOff(),CEGD.TextYOff, \
                            self.width()-self.getLineTextLeftXOff(),self.height(), \
                            QtCore.Qt.IntersectClip )
        lineHeight = self.getFontMetrics().lineSpacing()
        selectedTextIndexPosRangeTuple = self.getSelectTextByIndexPos()
        if selectedTextIndexPosRangeTuple != None:
            sortedIndexPosDict = FUF.sortedIndexPos( selectedTextIndexPosRangeTuple[0],selectedTextIndexPosRangeTuple[1] )
            startIndexPos = sortedIndexPosDict['first']
            endIndexPos = sortedIndexPosDict['second']

            startCurPixelPos = self.__transGloPixelPosToCurPixelPos(self.__transGloIndexPosToGloPixelPos(startIndexPos))
            endCurPixelPos = self.__transGloPixelPosToCurPixelPos(self.__transGloIndexPosToGloPixelPos(endIndexPos))
            
            # 如果被选中文本是行内文本
            if startIndexPos[1] == endIndexPos[1]:            
                painter.fillRect( startCurPixelPos[0], startCurPixelPos[1], \
                                  endCurPixelPos[0] - startCurPixelPos[0],lineHeight, \
                                  CEGD.TextSelectedBKBrush )

            # 如果被选中文本是多行文本
            else:
                painter.fillRect( startCurPixelPos[0], startCurPixelPos[1], \
                                  self.width()-startCurPixelPos[0], lineHeight ,  \
                                  CEGD.TextSelectedBKBrush )
                painter.fillRect( 0,startCurPixelPos[1]+lineHeight, \
                                  self.width(), endCurPixelPos[1]-startCurPixelPos[1]-lineHeight, \
                                  CEGD.TextSelectedBKBrush )
                painter.fillRect( endCurPixelPos[0]-self.width(),endCurPixelPos[1], \
                                  self.width(),lineHeight ,\
                                  CEGD.TextSelectedBKBrush )                


            
            
            
                        
                        
        
        
        
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
        
        # 设置剪裁区域
        painter.setClipRect( self.getLineTextLeftXOff(),CEGD.TextYOff, \
                             self.width()-self.getLineTextLeftXOff(),self.height() , \
                             QtCore.Qt.IntersectClip )
        
        # 绘制光标
        cursorPos = self.__transGloPixelPosToCurPixelPos( self.__transGloIndexPosToGloPixelPos(self.__textCursor.getCursorIndexPos()) )
        self.__textCursor.setGeometry(cursorPos[0],cursorPos[1],CEGD.CursorWidth,self.getFontMetrics().lineSpacing())
        self.__textCursor.setForceHide( cursorPos[0] < self.getLineTextLeftXOff() )

        
        # 绘制光标所在行高亮
        if self.getSelectTextByIndexPos() == None:
            lineTextRect = QtCore.QRect( self.getLineTextLeftXOff(),cursorPos[1], \
                                         self.width()-self.getLineTextLeftXOff(),self.getFontMetrics().lineSpacing() )
            painter.fillRect( lineTextRect ,CEGD.LineSelectedBKBrush)
    






        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs

    app = QApplication(sys.argv)

    mce = CodeTextEditWidget()
    #with codecs.open( '../tmp/temp2.txt','r','utf-8' ) as templateFileObj:
    with codecs.open( 'CodeTextEditWidget.py','r','utf-8' ) as templateFileObj:
    
        fileStr = templateFileObj.read()
        mce.setText( fileStr )
    mce.show()
    mce.resize( QtCore.QSize( 600,400 ) )
    
    mce.onQuickAltKey.connect(lambda k : print( 'alt',chr(k) ))
    mce.onQuickCtrlKey.connect(lambda k : print( 'ctrl',chr(k) ))
    
    
    
    sys.exit( app.exec_() )



