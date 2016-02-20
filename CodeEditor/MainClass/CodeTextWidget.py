
import sys

from PyQt5 import QtGui,QtCore

from CodeEditor.MainClass.TextDocument import TextDocument
from CodeEditor.MainClass.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD,GlobalClipBorard
from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.MainClass.BaseTextWidget import BaseTextWidget

from CodeEditor.ToolClass.SearchDialog import SearchDialog


class CodeTextWidget(BaseTextWidget):

    # 当按下Ctrl+字母键时，onQuickCtrlKey被发射
    # 当按下Alt+字母键时，onQuickAltKey被发射
    onQuickCtrlKeySignal = QtCore.pyqtSignal( QtCore.Qt.Key )
    onQuickAltKeySignal = QtCore.pyqtSignal( QtCore.Qt.Key )


        
    def deleteSelectText(self,update = True):
        selectedTextIndexPosRange = self.selectedTextManager().getSelectedTextIndexPosSorted()
        if selectedTextIndexPosRange != None:
            start,end = selectedTextIndexPosRange
            self.cursor().setGlobalCursorPos( start )
            self.document().deleteText(start,self.document().calcIndexPosDistance(start,end) )
            self.selectedTextManager().clearSelectedText()
            
    def __init__(self,textDocumentObj = None,settingsObj = None,parent=None):
        BaseTextWidget.__init__(self,textDocumentObj,settingsObj,parent)        
        self.onQuickCtrlKeySignal.connect(self.onQuickCtrlKey)

        self.__searchDialog = SearchDialog(self)
        self.searchDialog = lambda : self.__searchDialog


    # 当光标的位置改变时，需要刷新原来的行以及新行
    def onCursorPosChanged(self):
        self.update()
        curCursorPos = self.cursor().getCursorIndexPos()
        
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
            self.updateLineIndexRect( self.cursor().getCursorIndexPos(False)[1],self.settings().getFontMetrics().lineSpacing() )
            self.updateLineIndexRect( curYIndex,self.settings().getFontMetrics().lineSpacing() )

    def onSelectedTextChanged(self):
        selectedTextSearcher = None
        selectedTextIndexPosRangeTuple = self.selectedTextManager().getSelectedTextIndexPosSorted()
        if selectedTextIndexPosRangeTuple != None:
            startIndexPos,endIndexPos = selectedTextIndexPosRangeTuple
            if startIndexPos[1] == endIndexPos[1]:
                lineText = self.document().getLineText(startIndexPos[1])
                if FUF.isTextIsAFullWord(lineText, (startIndexPos[0],endIndexPos[0]) ):
                    word = lineText[ startIndexPos[0]:endIndexPos[0] ]
                    selectedTextSearcher = FUF.generateFullWordSearcher(word)

        self.settings().setUserDataByKey('selectedTextSearcher',selectedTextSearcher)
        self.update()

        
        
        
    def onQuickCtrlKey(self,key):
        off = key - QtCore.Qt.Key_A
        if (off >= 0) and (off <= 25):
            funcName = 'CTRL_%s' % chr( ord('A')+off )
            if hasattr(self, funcName):
                getattr(self, funcName)()
    
    def CTRL_Z(self):
        self.document().redoOneStep()
        cursorIndexPos = self.cursor().getCursorIndexPos()
        if self.document().isIndexPosValid(cursorIndexPos) == False:
            self.cursor().setGlobalCursorPos( self.document().formatIndexPos(cursorIndexPos) )
        self.selectedTextManager().clearSelectedText()
        self.update()
        
    def CTRL_V(self):
        curData = GlobalClipBorard().getData()
        if isinstance(curData,str):
            self.insertStr( curData )
            self.update()
        
    def CTRL_X(self):
        self.CTRL_C()
        self.deleteSelectText(True)
    
    def CTRL_A(self):
        l = self.document().getLineCount()-1
        self.selectedTextManager().setSelectTextIndexPos( (0,0) , (len(self.document().getLineText(l)),l) )
    
    def CTRL_C(self):
        selectedIndexPoss = self.selectedTextManager().getSelectedTextIndexPosSorted()
        if selectedIndexPoss == None:
            return
        start,end = selectedIndexPoss        
        if start[1] == end[1]:
            textData = self.document().getLineText(start[1])[start[0]:end[0]]
        else:        
            textData = self.document().getLineText(start[1])[start[0]:]
            for index in range( start[1]+1,end[1] ):
                textData += self.document().getSplitedChar() + self.document().getLineText(index)
            textData += self.document().getSplitedChar() + self.document().getLineText(end[1])[0:end[0]]
        GlobalClipBorard().setData( textData )
    
    def CTRL_F(self):
        self.searchDialog().show()
    
    
    '''  
    def CTRL_S(self):
        import codecs
        with codecs.open( 'temp.py','w','gb2312' ) as f:
            f.write(self.document().getText())
    '''
    
    
    
    
        
    def insertStr(self,text):
        if len(text) == 0:
            return
        
        self.document().operateCache().startRecord()
        self.deleteSelectText(False)
        indexPos = self.document().insertText(self.cursor().getCursorIndexPos(),text)  
        self.document().operateCache().endRecord()

        self.cursor().setGlobalCursorPos(indexPos)
        self.update()
    

    
    
    

    
    
    
    
    def __onLeftMouseDoubleClicked(self,clickedPixelPos):
        retuDict = self.transUserClickedPixelPosToIndexPos( clickedPixelPos )
        xPos,yPos = retuDict['indexPos']
        offset = retuDict['offset']
        lineText = self.document().getLineText(yPos)
        if len(lineText) == 0:
            self.selectedTextManager().clearSelectedText()
            return 
            
        prevClickedPixelPos = self.settings().getUserDataByKey('leftMouseDoubleClickedPos')
        if prevClickedPixelPos == clickedPixelPos:
            self.settings().setUserDataByKey('leftMouseDoubleClickedPos',None)
            self.selectedTextManager().setSelectTextIndexPos( (0,yPos),(len(lineText),yPos) )
            self.cursor().setGlobalCursorPos( (len(lineText),yPos) )
        else:
            self.settings().setUserDataByKey('leftMouseDoubleClickedPos',clickedPixelPos)
            if xPos == 0:
                length = TextDocument.skipSpaceAndWordByRight(lineText, xPos)['offset']
            elif xPos == len(lineText):
                length = TextDocument.skipSpaceAndWordByLeft(lineText, xPos)['offset']
                xPos -= length
            else:
                toLeftRetuDict = TextDocument.skipSpaceAndWordByLeft(lineText, xPos)
                toRightRetuDict = TextDocument.skipSpaceAndWordByRight(lineText, xPos)
                if toLeftRetuDict['searcher'] == toRightRetuDict['searcher'] and toLeftRetuDict['searcher'] != None:
                    length = toLeftRetuDict['offset'] + toRightRetuDict['offset']
                    xPos -= toLeftRetuDict['offset']
                else:
                    if offset >= 0:
                        length = toRightRetuDict['offset']
                    else:
                        length = toLeftRetuDict['offset']
                        xPos -= length
            self.selectedTextManager().setSelectTextIndexPos( (xPos,yPos),(xPos+length,yPos) )
            self.cursor().setGlobalCursorPos( (xPos+length,yPos) )
        
    
    
    
    def mouseDoubleClickEvent(self, event):
        curClickedPixelPos = (event.x(),event.y())
        if event.button() == QtCore.Qt.LeftButton:
            self.__onLeftMouseDoubleClicked(curClickedPixelPos)
        
        
    
    
    # leftMousePressed 和 leftMousePressed_curCursor只在以下三个函数使用，用来记录一些状态值
    def mousePressEvent(self, event):
        self.selectedTextManager().clearSelectedText()
        if event.button() == QtCore.Qt.LeftButton:
            posInfo = self.transUserClickedPixelPosToIndexPos((event.x(),event.y()))
            self.cursor().setGlobalCursorPos(posInfo['indexPos'])
            self.settings().setUserDataByKey('leftMousePressed',True)
            self.settings().setUserDataByKey('leftMousePressed_curCursor',self.cursor().getCursorIndexPos())
        elif event.button() == QtCore.Qt.RightButton:
            font = QtGui.QFont( "Consolas",self.settings().getFont().pointSize()+1 )
            font.setBold(True)
            self.settings().setFont(font)

    def mouseMoveEvent(self, event):
        if self.settings().getUserDataByKey('leftMousePressed') == True:
            posInfo = self.transUserClickedPixelPosToIndexPos( (event.x(),event.y()) )
            self.cursor().setGlobalCursorPos( posInfo['indexPos'] )
            self.selectedTextManager().setSelectTextIndexPos( self.settings().getUserDataByKey('leftMousePressed_curCursor'),posInfo['indexPos'] )
        
    def mouseReleaseEvent(self, event):
        self.settings().setUserDataByKey('leftMousePressed',None)
        self.settings().setUserDataByKey('leftMousePressed_curCursor',None)



    def __onDirectionKey(self,event):
        key = event.key()
        modifiers = event.modifiers()
        
        oldCursorIndexPos = self.cursor().getCursorIndexPos()
        if ( FUF.hasModifier(modifiers) == False ) or ( FUF.hasCtrlModifier(modifiers) == False ):
            dictMap = { str(QtCore.Qt.Key_Left) :self.document().moveIndexPosLeft   , \
                        str(QtCore.Qt.Key_Right):self.document().moveIndexPosRight  , \
                        str(QtCore.Qt.Key_Up)   :self.document().moveIndexPosUp     , \
                        str(QtCore.Qt.Key_Down) :self.document().moveIndexPosDown  }
            newCursorIndexPos = dictMap[str(key)](oldCursorIndexPos)

        elif FUF.hasCtrlModifier(modifiers):
            if key == QtCore.Qt.Key_Up:
                self.showLineNumberAsTop(self.settings().getStartDisLineNumber()-1)
                return 
            elif key == QtCore.Qt.Key_Down:
                self.showLineNumberAsTop(self.settings().getStartDisLineNumber()+1)
                return 
            
            if key == QtCore.Qt.Key_Left:
                newCursorIndexPos = self.document().moveIndexPosLeftByWord(oldCursorIndexPos)
            elif key == QtCore.Qt.Key_Right:
                newCursorIndexPos = self.document().moveIndexPosRightByWord(oldCursorIndexPos)
        
        
        self.cursor().setGlobalCursorPos(newCursorIndexPos)
        if FUF.hasShiftModifier(event.modifiers()) == True:
            self.selectedTextManager().addSelectTextIndexPos(oldCursorIndexPos, newCursorIndexPos)
        else:
            self.selectedTextManager().clearSelectedText()
        self.update()
        
        
    
    def __onDeleteKey(self,event):
        if self.selectedTextManager().getSelectedTextIndexPos() != None:
            self.deleteSelectText(True)
            return 
        curCursorIndexPos = self.cursor().getCursorIndexPos()
        if FUF.hasModifier(event.modifiers()) == False:
            if event.key() == QtCore.Qt.Key_Delete:
                newCursorIndexPos = self.document().moveIndexPosRight(curCursorIndexPos)
            else:
                newCursorIndexPos = self.document().moveIndexPosLeft(curCursorIndexPos)
        elif FUF.onlyCtrlModifier(event.modifiers()):
            if event.key() == QtCore.Qt.Key_Delete:
                newCursorIndexPos = self.document().moveIndexPosRightByWord(curCursorIndexPos)
            else:
                newCursorIndexPos = self.document().moveIndexPosLeftByWord(curCursorIndexPos)
        else:
            return 

        distance = self.document().calcIndexPosDistance(curCursorIndexPos, newCursorIndexPos, False)
        if distance > 0:
            self.cursor().setGlobalCursorPos(curCursorIndexPos)
            self.document().deleteText(curCursorIndexPos,distance )
        elif distance < 0:
            self.cursor().setGlobalCursorPos(newCursorIndexPos)
            self.document().deleteText(newCursorIndexPos,-distance )
        self.update()
    
    
    def __onDisplayCharKey(self,event):
        self.deleteSelectText(False)
        indexPos = self.document().insertText(self.cursor().getCursorIndexPos(), event.text())
        self.cursor().setGlobalCursorPos(indexPos)
        self.update()
    
    
    def __onDisplayLetterKey(self,event):
        if (FUF.hasModifier(event.modifiers()) == False) or (FUF.onlyShiftModifier(event.modifiers()) == True):
            self.deleteSelectText(False)     
            indexPos = self.document().insertText(self.cursor().getCursorIndexPos(), event.text())
            self.cursor().setGlobalCursorPos(indexPos)
            self.update()
        elif FUF.onlyCtrlModifier(event.modifiers()):
            self.onQuickCtrlKeySignal.emit(event.key())
        elif FUF.onlyAltModifier(event.modifiers()):
            self.onQuickAltKeySignal.emit(event.key())
        
    
    def __onEnterKey(self,event):
        self.deleteSelectText(False)
        
        curCursorPos = self.cursor().getCursorIndexPos()
        cursorLeftText = self.document().getLineText(curCursorPos[1])[0:curCursorPos[0]]
                
        unvisibleSearcher = TextDocument.UnvisibleCharSearcher
        matchObj = unvisibleSearcher.match(cursorLeftText)
        spaceNumber = matchObj.span()[1] - matchObj.span()[0] if matchObj != None else 0
        
        indexPos = self.document().insertText(self.cursor().getCursorIndexPos(), '\n' + ' '*spaceNumber )
        self.cursor().setGlobalCursorPos(indexPos)
        self.update()
    
    def __onTabKey(self,event):
        if self.selectedTextManager().getSelectedTextIndexPos() == None:        
            insertSpaceLen = 4 - (self.cursor().getCursorIndexPos()[0] % 4)
            indexPos = self.document().insertText(self.cursor().getCursorIndexPos(), ' '*insertSpaceLen)
            self.cursor().setGlobalCursorPos(indexPos)
        else:
            curSelectedIndexPos = self.selectedTextManager().getSelectedTextIndexPos()
            retuSortedPoses = FUF.sortedIndexPos( curSelectedIndexPos[0],curSelectedIndexPos[1])
            
            affectedLineIndexList = list(range( retuSortedPoses['first'][1],retuSortedPoses['second'][1]+1 ))
            for lineIndex in affectedLineIndexList:
                self.document().insertText( (0,lineIndex),' '*CEGD.spaceToInsertTOL )
            
            curCursorPos = self.cursor().getCursorIndexPos()
            if affectedLineIndexList.count(curCursorPos[1]) != 0:
                self.cursor().setGlobalCursorPos( (curCursorPos[0]+CEGD.spaceToInsertTOL,curCursorPos[1]) )            
            self.selectedTextManager().setSelectTextIndexPos( (curSelectedIndexPos[0][0]+CEGD.spaceToInsertTOL,curSelectedIndexPos[0][1]) ,\
                                          (curSelectedIndexPos[1][0]+CEGD.spaceToInsertTOL,curSelectedIndexPos[1][1]) )
            
        self.update()
    

    def __onPageKey(self,event):
        if FUF.hasModifier(event.modifiers()) == False:
            if event.key() == QtCore.Qt.Key_PageUp:
                newLineNumber = max([ self.settings().getStartDisLineNumber()-self.calcDisLineNumber(),0 ])
            elif event.key() == QtCore.Qt.Key_PageDown:
                newLineNumber = min([ self.settings().getStartDisLineNumber()+self.calcDisLineNumber(),self.document().getLineCount()-1 ])
        else:
            if FUF.onlyCtrlModifier(event.modifiers()):
                if event.key() == QtCore.Qt.Key_PageUp:
                    newLineNumber = 0
                elif event.key() == QtCore.Qt.Key_PageDown:
                    newLineNumber = self.calcMaxStartDisLineNumber()
            else:
                return 
        
        curIndexPos = self.cursor().getCursorIndexPos()
        newIndexPos = self.document().formatIndexPos(  (curIndexPos[0],curIndexPos[1] - (self.settings().getStartDisLineNumber() - newLineNumber))  )
        self.showLineNumberAsTop( newLineNumber )
        self.cursor().setGlobalCursorPos( newIndexPos )
    
    def __onHomeEndKey(self,event):
        if FUF.hasModifier(event.modifiers()) == False:
            curIndexPos = self.cursor().getCursorIndexPos()
            if event.key() == QtCore.Qt.Key_Home:
                newIndexPos = ( 0,curIndexPos[1] )
            else:
                newIndexPos = ( len(self.document().getLineText(curIndexPos[1])),curIndexPos[1] )
            self.cursor().setGlobalCursorPos( newIndexPos )
        else:
            if FUF.onlyCtrlModifier(event.modifiers()):
                if event.key() == QtCore.Qt.Key_Home:
                    lineIndex = 0
                    newIndexPos = ( 0,0 )
                else:
                    lineIndex = self.calcMaxStartDisLineNumber()
                    lineCount = self.document().getLineCount()-1
                    newIndexPos = ( len(self.document().getLineText(lineCount)),lineCount )
                self.cursor().setGlobalCursorPos( newIndexPos )
                self.showLineNumberAsTop(lineIndex)
                

        
    
    
    
    def keyPressEvent(self, event):
        #print (hex(event.key()).upper(), hex(ord(event.text()))   )
        
        self.document().operateCache().startRecord()
        
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

        self.document().operateCache().endRecord()








    # @FUF.funcExeTime
    def beforePaint(self, painter):
        BaseTextWidget.beforePaint(self, painter)
        self.__highlightSelectedText(painter)
        self.__highlightAutoSelectedText(painter)
        
        
    def __highlightSelectedText(self,painter):
        selectedTextIndexPosRangeTuple = self.selectedTextManager().getSelectedTextIndexPosSorted()
        if selectedTextIndexPosRangeTuple != None:
            startIndexPos,endIndexPos = selectedTextIndexPosRangeTuple
            lineHeight = self.settings().getFontMetrics().lineSpacing()
        
            startCurPixelPos = self.transGloPixelPosToCurPixelPos(self.transGloIndexPosToGloPixelPos(startIndexPos))
            endCurPixelPos = self.transGloPixelPosToCurPixelPos(self.transGloIndexPosToGloPixelPos(endIndexPos))
            
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
    
    # @FUF.funcExeTime
    def __highlightAutoSelectedText(self,painter):
        selectedTextSearcher = self.settings().getUserDataByKey('selectedTextSearcher')
        if selectedTextSearcher == None:
            return 
        
        lineHeight = self.settings().getFontMetrics().lineSpacing()
        
        indexPoss = []
        for item in self.calcAnyVisibleYOff():
            text = self.document().getLineText(item['lineIndex'])
            for metaObj in selectedTextSearcher.finditer( text ):
                indexPoss.append( ( metaObj.span()[0],metaObj.span()[1],item['lineIndex'] )   )
        
        # 移除用户选中的文本的范围，使其不高亮（因为已经高亮过了）
        selectedIndexPos = self.selectedTextManager().getSelectedTextIndexPosSorted()
        selectedItem = ( selectedIndexPos[0][0],selectedIndexPos[1][0],selectedIndexPos[0][1] )
        if indexPoss.count( selectedItem ) != 0:
            indexPoss.remove( selectedItem )

        for spanTuple in indexPoss:
            start,end,lineIndex = spanTuple
            startCurPixelPos = self.transGloPixelPosToCurPixelPos(self.transGloIndexPosToGloPixelPos( (start,lineIndex) ))
            endCurPixelPos = self.transGloPixelPosToCurPixelPos(self.transGloIndexPosToGloPixelPos( (end,lineIndex) ))
            painter.fillRect( startCurPixelPos[0], startCurPixelPos[1], \
                              endCurPixelPos[0] - startCurPixelPos[0],lineHeight, \
                              CEGD.TextAutoSelectedBKBrush )
        
        

        
        
        
        
        
    





        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import codecs

    app = QApplication(sys.argv)

    mce = CodeTextWidget()
    mce.show()
    mce.resize( QtCore.QSize( 600,400 ) )

    #with codecs.open( '../tmp/temp2.txt','r','utf-8' ) as templateFileObj:
    with codecs.open( 'CodeTextWidget.py','r','utf-8' ) as templateFileObj:
    #with codecs.open( '../tmp/strtemp.txt','r','utf-8' ) as templateFileObj:
        fileStr = templateFileObj.read()
        mce.setText( fileStr )
    
    mce.onQuickAltKeySignal.connect(lambda k : print( 'alt',chr(k) ))
        
    
    sys.exit( app.exec_() )



