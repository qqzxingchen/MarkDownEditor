
import re
from PyQt5 import QtCore,QtGui
from CodeEditor.CodeEditorGlobalDefines import CEGlobalDefines
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc

'''
TextDocument.__lineTextInfoDictArray的注释信息
一个Array，其中的每项都是一个dict，称为lineTextInfoDict，它的格式是：
lineTextInfoDict['lineText']                     一个字符串，该行文本的字符串
lineTextInfoDict['normalLineTextPixmap']         一个QPixmap对象，绘制对应行文本时，就把这个pixmap绘制到界面上（原始图片）
lineTextInfoDict['charWidthArray']               绘制到QPixmap对象上时，每个字符的字符宽度（像素数）
'''


class TextDocument(QtCore.QObject):

    LINE_TEXT_STR = 'lineText'
    CHAR_WIDTH_ARRAY = 'charWidthArray'
    NORMAL_LINE_PIXMAP = 'normalLineTextPixmap'

    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        QtCore.QObject.__init__(self,parent)
        
        # 注释看文件头的注释
        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0             # 实时保存最大像素宽度
        self.setFont( font )



    def getMaxLineWidth(self):
        return self.__lineMaxWidth
    def getLineCount(self):
        return len(self.__lineTextInfoDictArray)

    def setText(self,text = ''):
        self.__text = text
        self.__afterTextChanged()
    def getText(self):
        return self.text
    def getSplitedChar(self):
        return self.__splitedChar
    
    
    def setFont(self,fontObj,fontMetrics = None):
        self.__font = fontObj
        if fontMetrics == None:
            fontMetrics = QtGui.QFontMetrics(self.__font)
        self.__fontMetrics = fontMetrics
        
        self.__lineMaxWidth = 0
        for index in range(len(self.__lineTextInfoDictArray)):
            self.__lineTextInfoDictArray[index] = {TextDocument.LINE_TEXT_STR:self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]}
        
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics










    def insertText(self,xyIndexPosTuple,text):
        retuDict = FrequentlyUsedFunc.splitTextToLines(text)
        splitedTexts = retuDict['splitedTexts']
        if len(splitedTexts) == 0:
            return
        indexPos = xyIndexPosTuple
        for index in range(len( splitedTexts )-1):
            indexPos = self.__insertTextWithoutLineBreak( indexPos , splitedTexts[index])
            indexPos = self.__insertLineBreak( indexPos )
        return self.__insertTextWithoutLineBreak( indexPos , splitedTexts[-1])

    # 插入一个换行符
    def __insertLineBreak(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]}
        self.__lineTextInfoDictArray.insert( yPos + 1 , {TextDocument.LINE_TEXT_STR:curLineText[xPos:len(curLineText)]})
        return (0,yPos+1)
        
    # 插入一段没有换行符的文本
    def __insertTextWithoutLineBreak(self,xyIndexPosTuple,text):        
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos] + text + curLineText[xPos:len(curLineText)]}
        return ( len(curLineText[0:xPos] + text) ,yPos)
        
    # 从xyPos的位置起向右删掉length长度的字符
    def deleteText(self,xyIndexPosTuple,length):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        
        while len(self.getLineTextByIndex(yPos))-xPos < length:
            self.__deleteLineBreak(yPos)
            length -= 1
            
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]+curLineText[xPos+length:len(curLineText)]}
        
    def deleteOneLine(self,yIndexPos):
        self.__lineTextInfoDictArray.remove( self.__lineTextInfoDictArray[yIndexPos] )


    # 删掉第lineIndex行的行尾换行符，其实质是将第lineIndex和第lineIndex+1行的文本合并为一行
    # 如果不存在第lineIndex+1行，则什么都不做
    def __deleteLineBreak(self,lineIndex):
        if lineIndex+1 >= len(self.__lineTextInfoDictArray):
            return 
        text1 = self.getLineTextByIndex(lineIndex)
        text2 = self.getLineTextByIndex(lineIndex+1)
        self.__lineTextInfoDictArray[lineIndex] = {TextDocument.LINE_TEXT_STR:text1+text2}
        self.__lineTextInfoDictArray.remove( self.__lineTextInfoDictArray[lineIndex+1] )
    
    
    
    
    
    
    
    
    
        

    # 计算从indexPos1到indexPos2的距离（认为indexPos1是起点，indexPos2是终点）
    # 如果absValue为True，则返回距离的绝对值，否则，
    def calcIndexPosDistance(self,indexPos1,indexPos2,absValue = True):        
        
        sortedIndexPosDict = FrequentlyUsedFunc.sortedIndexPos(indexPos1, indexPos2)
        if (sortedIndexPosDict['changed'] == True) and (absValue == False):
            positiveSign = -1
        else:
            positiveSign = 1
        
        indexPosA = sortedIndexPosDict['first']
        indexPosB = sortedIndexPosDict['second']
        if indexPosA[1] == indexPosB[1]:
            absV = indexPosB[0] - indexPosA[0]
        else:
            absV = len(self.getLineTextByIndex(indexPosA[1])) - indexPosA[0] + 1
            absV += indexPosB[0]
            for index in range( indexPosA[1]+1,indexPosB[1] ):
                absV += len(self.getLineTextByIndex(index)) + 1
        return positiveSign * absV
    
    # 判断xyIndexPosTuple所标示的光标位置是否存在
    def isIndexPosValid(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        lineText = self.getLineTextByIndex(yPos)
        if lineText == None:
            return False
        if (xPos < 0) or (xPos > len(lineText)):
            return False
        return True
    def formatIndexPos(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        lineText = self.getLineTextByIndex(yPos)
        if lineText == None:
            if yPos < 0:
                return (0,0)
            else:
                l = self.getLineCount()-1
                return ( len(self.getLineTextByIndex(l)),l )
        else:
            if xPos < 0:
                return ( 0,yPos )
            elif xPos > len(lineText):
                return ( len(lineText),yPos )
            else:
                return ( xPos,yPos )
    
    
    
    
    
    
    
    
    
    
    def moveLeftIndexPos(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]

        xPos -= 1
        if xPos < 0:
            if yPos <= 0:
                xPos = 0
                yPos = 0
            else:            
                yPos -= 1
                xPos = len(self.getLineTextByIndex(yPos))
        return (xPos,yPos)

    def moveRightIndexPos(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]

        xPos += 1
        if xPos > len(self.getLineTextByIndex(yPos)):
            xPos = 0
            yPos += 1
            if yPos >= self.getLineCount()-1:
                yPos = self.getLineCount()-1
        return (xPos,yPos)

    def moveUpIndexPos(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        
        if yPos > 0:
            yPos -= 1
            xPos = min([ len(self.getLineTextByIndex(yPos)),xPos ])
        return (xPos,yPos)
        
    def moveDownIndexPos(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        
        if yPos < self.getLineCount()-1:
            yPos += 1
            xPos = min([ len(self.getLineTextByIndex(yPos)),xPos ])    
        return (xPos,yPos)
        
        
        
        
        
        

    def __indexIsValid(self,index):
        if (index < 0) or (index >= len(self.__lineTextInfoDictArray)):
            return False
        else:
            return True
    
    def setLineTextInfoDict(self,index,charWidthArray,normalLineTextPixmap,lineWidth = None):
        if self.__indexIsValid(index) == False:
            return False
        self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY] = charWidthArray
        self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP] = normalLineTextPixmap 
        if lineWidth != None:
            self.__lineMaxWidth = max( [ self.__lineMaxWidth,lineWidth ] )
        return True
    
    # 以下几个方法的参数outOfIndexValue，是指当传入的index越限时，将会返回的值
    # 获取某行的文本
    def getLineTextByIndex(self,index,outOfIndexValue=None):
        if self.__indexIsValid(index) == False:
            return outOfIndexValue 
        return self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]

    def getCharWidthArrayByIndex(self,index,outOfIndexValue=None):
        if self.__indexIsValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.CHAR_WIDTH_ARRAY) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY]

    def getNormalLineTextPixmapByIndex(self,index,outOfIndexValue=None):
        if self.__indexIsValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP]

    def getLineTextInfoDictByIndex(self,index,outOfIndexValue=None):
        if self.__indexIsValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index]    
    




    # 根据当前最新的文本，来重绘文本信息Dict
    def __refreshLineTextInfoDictByIndex(self,index):
        curLineText = self.getLineTextByIndex(index)
        charCorrespondedQPenArr = self.__findCharCorrespondedQPen(curLineText)
        
        maxPixelLength = len(curLineText)*( CEGlobalDefines.CharDistancePixel + self.__fontMetrics.maxWidth() * 2 )
        pixmapObj = QtGui.QPixmap(maxPixelLength,self.__fontMetrics.lineSpacing())
        pixmapObj.fill(QtGui.QColor(255,255,255,0))
        painter = QtGui.QPainter(pixmapObj)
        painter.setFont(self.__font)
            
        curXOff = 0
        charWidthInfoArr = []
        letterRect = QtCore.QRect(0,0,0,0)
        for i in range(len(curLineText)):
            if charCorrespondedQPenArr[i] != painter.pen():
                painter.setPen(charCorrespondedQPenArr[i])            
            curChar = curLineText[i]
            curXOff += CEGlobalDefines.CharDistancePixel
            letterRect = painter.boundingRect(curXOff,0,0,0,0,curChar)
            painter.drawText(letterRect,0,curChar)
            curXOff += letterRect.width()
            charWidthInfoArr.append( letterRect.width() )
        del painter   # 删除当前的painter，才能继续为pixmap创建新的画笔并绘制
        
        # 最大宽度需要减掉最后一个字符导致的字符长度增长，这样可以保证即使用户把滚动条拉倒最右边，也有字符显示出来
        self.setLineTextInfoDict(index, charWidthInfoArr, pixmapObj,curXOff - letterRect.width())



    def __findCharCorrespondedQPen(self,lineStr):
        '''
        arr = []
        for c in lineStr:
            if c == '1':
                arr.append(CEGlobalDefines.LineStrPen)
            else:
                arr.append(CEGlobalDefines.TextTokenPen)
        '''
        
        arr = [CEGlobalDefines.LineStrPen] * len(lineStr)
        tokens = ['def','class','del']
        
        for t in tokens:
            pBegin = r'^%s[\W]{1}'
            pMid = r'[\W]{1}%s[\W]{1}'
            pEnd = '[\W]{1}%s$'
            
            
            
            pattern = '^%s[\W]{1}|[\W]{1}%s[\W]{1}|[\W]{1}%s$' % (t,t,t)
            for mObj in re.finditer(pattern, lineStr):
                for index in range(mObj.span()[0],mObj.span()[1]):
                    
                    arr[index] = CEGlobalDefines.TextTokenPen
                    
        return arr



    def __afterTextChanged(self):
        retuDict = FrequentlyUsedFunc.splitTextToLines(self.__text)
        self.__splitedChar = retuDict['splitedChar']

        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0
        for text in retuDict['splitedTexts']:
            self.__lineTextInfoDictArray.append({TextDocument.LINE_TEXT_STR:text})
    

