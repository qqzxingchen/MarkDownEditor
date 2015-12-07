

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
        
        # 注释看文件头
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













    # 插入一个换行符
    def insertLineBreak(self,xyIndexPosTuple):
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]}
        self.__lineTextInfoDictArray.insert( yPos + 1 , {TextDocument.LINE_TEXT_STR:curLineText[xPos:len(curLineText)]})

    # 插入一段没有换行符的文本
    def insertTextWithoutLineBreak(self,xyIndexPosTuple,text):        
        xPos = xyIndexPosTuple[0]
        yPos = xyIndexPosTuple[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos] + text + curLineText[xPos:len(curLineText)]}

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
        
        
        
        
        
        

    
    
    
    def setLineTextInfoDict(self,index,charWidthArray,normalLineTextPixmap,lineWidth):
        if index >= len(self.__lineTextInfoDictArray):
            return False
        self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY] = charWidthArray
        self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP] = normalLineTextPixmap 
        self.__lineMaxWidth = max( [ self.__lineMaxWidth,lineWidth ] )
        return True
    
    # 以下几个方法的参数outOfIndexValue，是指当传入的index越限时，将会返回的值
    # 获取某行的文本
    def getLineTextByIndex(self,index,outOfIndexValue=None):
        if index >= len(self.__lineTextInfoDictArray):
            return outOfIndexValue
        return self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]

    def getCharWidthArrayByIndex(self,index,outOfIndexValue=None):
        if index >= len(self.__lineTextInfoDictArray):
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.CHAR_WIDTH_ARRAY) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY]

    def getNormalLineTextPixmapByIndex(self,index,outOfIndexValue=None):
        if index >= len(self.__lineTextInfoDictArray):
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP]

    def getLineTextInfoDictByIndex(self,index,outOfIndexValue=None):
        if index >= len(self.__lineTextInfoDictArray):
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index]    
    




    # 根据当前最新的文本，来重绘文本信息Dict
    def __refreshLineTextInfoDictByIndex(self,index):
        curLineText = self.getLineTextByIndex(index)
        maxPixelLength = len(curLineText)*( CEGlobalDefines.CharDistancePixel + \
                                            self.__fontMetrics.maxWidth() * 2 )
        
        pixmapObjNormal = QtGui.QPixmap(maxPixelLength,self.__fontMetrics.lineSpacing())
        pixmapObjNormal.fill(QtGui.QColor(0,0,0,0))
        painterNormal = QtGui.QPainter(pixmapObjNormal)
        painterNormal.setPen(CEGlobalDefines.LineStrPen)
        painterNormal.setFont(self.__font)

        curXOff = 0
        charWidthInfoArr = []
        letterRect = QtCore.QRect(0,0,0,0)
        for curChar in curLineText:
            curXOff += CEGlobalDefines.CharDistancePixel
            letterRect = painterNormal.boundingRect(curXOff,0,0,0,0,curChar)
            painterNormal.drawText(letterRect,0,curChar)
            curXOff += letterRect.width()
            charWidthInfoArr.append( letterRect.width() )
        
        # 最大宽度需要减掉最后一个字符导致的字符长度增长，这样可以保证即使用户把滚动条拉倒最右边，也有字符显示出来        
        self.setLineTextInfoDict(index, charWidthInfoArr, pixmapObjNormal,curXOff - letterRect.width())

    def __afterTextChanged(self):
        splitN = self.__text.split('\n')
        splitRN = self.__text.split('\r\n')
        if len(splitN) == len(splitRN):
            splitedTexts = splitRN
            self.__splitedChar = '\r\n'
        else:
            splitedTexts = splitN
            self.__splitedChar = '\n'
            
        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0
        for text in splitedTexts:
            self.__lineTextInfoDictArray.append({TextDocument.LINE_TEXT_STR:text})
    

