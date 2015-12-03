

from PyQt5 import QtCore,QtGui
from CodeEditor.CodeEditorGlobalDefines import CEGlobalDefines

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


    def getLineCount(self):
        return len(self.__lineTextInfoDictArray)

    def setText(self,text = ''):
        self.__text = text
        self.__afterTextChanged()
    def getText(self):
        return self.text
    def getSplitedChar(self):
        return self.__splitedChar
    
    def setFont(self,fontObj):
        self.__font = fontObj
        self.__fontMetrics = QtGui.QFontMetrics(self.__font)
        self.__lineMaxWidth = 0
        for index in range(len(self.__lineTextInfoDictArray)):
            self.__lineTextInfoDictArray[index] = {TextDocument.LINE_TEXT_STR:self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]}
        
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics


    # 插入一个换行符
    def insertLineBreak(self,xyPos):
        xPos = xyPos[0]
        yPos = xyPos[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]}
        self.__lineTextInfoDictArray.insert( yPos + 1 , {TextDocument.LINE_TEXT_STR:curLineText[xPos:len(curLineText)]})

    # 插入一段没有换行符的文本
    def insertTextWithoutLineBreak(self,xyPos,text):        
        xPos = xyPos[0]
        yPos = xyPos[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos] + text + curLineText[xPos:len(curLineText)]}


    # 从xyPos的位置删掉length长度的字符
    def deleteText(self,xyPos,length):
        xPos = xyPos[0]
        yPos = xyPos[1]
        curLineText = self.__lineTextInfoDictArray[yPos][TextDocument.LINE_TEXT_STR]
        rightText = curLineText[xPos:len(curLineText)]
        if len(rightText) >= length:
            self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]+curLineText[xPos+length:len(curLineText)]}
        else:
            self.__lineTextInfoDictArray[yPos] = {TextDocument.LINE_TEXT_STR:curLineText[0:xPos]}
            length -= len(rightText)
            
            index = yPos + 1
            while True:
                if index >= len(self.__lineTextInfoDictArray):
                    break
                s = self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]
                if length > len(s):
                    self.__lineTextInfoDictArray.remove( self.__lineTextInfoDictArray[index] )
                    length -= len(s)
                else:
                    self.__lineTextInfoDictArray[index] = {TextDocument.LINE_TEXT_STR:s[len(s)-length:len(s)]}
                    break
                
    
    
    
    
    
    def setLineTextInfoDict(self,index,charWidthArray,normalLineTextPixmap,lineWidth):
        if index >= len(self.__lineTextInfoDictArray):
            return False
        self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY] = charWidthArray
        self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP] = normalLineTextPixmap 
        self.__lineMaxWidth = max( [ self.__lineMaxWidth,lineWidth ] )
        return True
    
    # 获取某行的文本
    def getLineTextByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        return self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]
    def getCharWidthArrayByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        if self.__lineTextInfoDictArray[index].get(TextDocument.CHAR_WIDTH_ARRAY) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY]
    def getNormalLineTextPixmapByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP]
    def getLineTextInfoDictByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index]    
    def getMaxLineWidth(self):
        return self.__lineMaxWidth



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
    

