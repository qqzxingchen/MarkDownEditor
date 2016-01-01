
import re
from PyQt5 import QtCore,QtGui
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.OperateCache import OperateCache, OperateRecord


'''
TextDocument.__lineTextInfoDictArray的注释信息
一个Array，其中的每项都是一个dict，称为lineTextInfoDict，它的格式是：
lineTextInfoDict['lineText']                     一个字符串，该行文本的字符串
lineTextInfoDict['normalLineTextPixmap']         一个QPixmap对象，绘制对应行文本时，就把这个pixmap绘制到界面上（原始图片）
lineTextInfoDict['charWidthArray']               绘制到QPixmap对象上时，每个字符的字符宽度（像素数）
'''

# 主要负责进行文本的绘制工作相关
class __BaseDocument__(QtCore.QObject):

    def setFont(self,fontObj,fontMetrics = None):
        self.__font = fontObj
        if fontMetrics == None:
            fontMetrics = QtGui.QFontMetrics(self.__font)
        self.__fontMetrics = fontMetrics
        self.__chineseCharFont = QtGui.QFont(self.__font)
        self.__chineseCharFont.setPointSize( self.__chineseCharFont.pointSize()-2 )
        
        self.__lineMaxWidth = 0
        for index in range(self.getLineCount()):
            self.clearLineTextInfoDict(index)
        
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics
    
    
    def getMaxLineWidth(self):
        return self.__lineMaxWidth
    def getLineCount(self):
        return len(self.__lineTextInfoDictArray)
    
    
    def setText(self,text = ''):
        self.__text = text
        retuDict = FUF.splitTextToLines(self.__text)
        self.__splitedChar = retuDict['splitedChar']

        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0
        for text in retuDict['splitedTexts']:
            self.__lineTextInfoDictArray.append({TextDocument.LINE_TEXT_STR:text})
            
    def getText(self):
        return self.__text
    def getSplitedChar(self):
        return self.__splitedChar
    
    
    
    
    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        QtCore.QObject.__init__(self,parent)
        
        # 注释看文件头的注释
        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0             # 实时保存最大像素宽度
        self.setFont( font )

    
    
    
    
    def isLineIndexValid(self,index):
        if (index < 0) or (index >= len(self.__lineTextInfoDictArray)):
            return False
        else:
            return True
    
    def changeLineText(self,lineIndex,newText):
        if self.isLineIndexValid(lineIndex) == False:
            return False
        self.__lineTextInfoDictArray[lineIndex] = {TextDocument.LINE_TEXT_STR:newText}
        return True
        
    def delLine(self,lineIndex):
        if self.isLineIndexValid(lineIndex) == False:
            return False
        self.__lineTextInfoDictArray.remove( self.__lineTextInfoDictArray[lineIndex] )
        if len(self.__lineTextInfoDictArray) == 0:
            self.__lineTextInfoDictArray.append( {TextDocument.LINE_TEXT_STR:''} )            
        return True
    
    # 文本将会把newText插入到lineIndex之前，使newText称为新的第lineIndex号元素
    def addLine(self,lineIndex,newText):
        if lineIndex < 0:
            return False
        self.__lineTextInfoDictArray.insert(lineIndex, {TextDocument.LINE_TEXT_STR:newText})
        return True
    
    def clearLineTextInfoDict(self,index):
        if self.isLineIndexValid(index) == False:
            return False
        self.__lineTextInfoDictArray[index] = {TextDocument.LINE_TEXT_STR:self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]}
        return True
    
    def setLineTextInfoDict(self,index,charWidthArray,normalLineTextPixmap,lineWidth = None):
        if self.isLineIndexValid(index) == False:
            return False
        self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY] = charWidthArray
        self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP] = normalLineTextPixmap 
        if lineWidth != None:
            self.__lineMaxWidth = max( [ self.__lineMaxWidth,lineWidth ] )
        return True
    
    # 以下几个方法的参数outOfIndexValue，是指当传入的index越限时，将会返回的值
    # 获取某行的文本
    def getLineTextByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue 
        return self.__lineTextInfoDictArray[index][TextDocument.LINE_TEXT_STR]

    def getCharWidthArrayByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.CHAR_WIDTH_ARRAY) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.CHAR_WIDTH_ARRAY]

    def getNormalLineTextPixmapByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index][TextDocument.NORMAL_LINE_PIXMAP]

    def getLineTextInfoDictByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP) == None:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.__lineTextInfoDictArray[index]    


    # 根据当前最新的文本，来重绘文本信息Dict
    # @FUF.funcExeTime
    def __refreshLineTextInfoDictByIndex(self,index):
        lineHeight = self.__fontMetrics.lineSpacing()        
        curLineText = self.getLineTextByIndex(index)
        charMatchedSettings = self.findCharMatchedSettings(curLineText,index)

        pixmapObj = QtGui.QPixmap(len(curLineText)*( CEGD.CharDistancePixel + self.__fontMetrics.maxWidth() * 2 ),lineHeight)
        pixmapObj.fill(QtGui.QColor(255,255,255,0))
        painter = QtGui.QPainter(pixmapObj)
        
        curXOff = 0
        charWidthInfoArr = []
        letterRect = QtCore.QRect(0,0,0,0)
        for i in range(len(curLineText)):
            painter = self.__changePainter(painter, charMatchedSettings[i])
            curXOff += CEGD.CharDistancePixel
            letterRect = painter.boundingRect(curXOff,0,0,0,0,curLineText[i])
            yOff = (lineHeight-letterRect.height())/2
            letterRect = QtCore.QRect( letterRect.x(),yOff,letterRect.width(),lineHeight-yOff )
            painter.drawText(letterRect,0,curLineText[i])
            
            curXOff += letterRect.width()
            charWidthInfoArr.append( letterRect.width() )
        del painter   # 删除当前的painter，才能继续为pixmap创建新的画笔并绘制
        
        # 最大宽度需要减掉最后一个字符导致的字符长度增长，这样可以保证即使用户把滚动条拉倒最右边，也有字符显示出来
        self.setLineTextInfoDict(index, charWidthInfoArr, pixmapObj,curXOff - letterRect.width())


    # 根据matchedPenAndInfo中的信息，更新painter的QFont和QPen
    # matchedPenAndInfo的格式与
    def __changePainter(self,painter,matchedPenAndInfo):
        if matchedPenAndInfo[0] != painter.pen():
            painter.setPen(matchedPenAndInfo[0])
        if matchedPenAndInfo[1] != painter.font():
            painter.setFont(matchedPenAndInfo[1])
        return painter

    # 该函数可以被重载以实现字符高亮
    # 输入：
    #     lineStr：行字符串
    #     lineIndex：行号
    # 输出：
    #     retuList(list)，它要满足以下要求
    #         长度与lineStr的长度相同
    #         list的每项都为一个Tuple，格式为： ( QPenObj,QFontObj )
    def findCharMatchedSettings(self,lineStr,lineIndex):
        arr = []
        for c in lineStr:
            if FUF.isChineseChar(c):
                arr.append( (CEGD.LineTextPen,self.__chineseCharFont) )
            else:
                arr.append( (CEGD.LineTextPen,self.__font) )
        return arr














class TextDocument(__BaseDocument__):

    lineTextChangedSignal = QtCore.pyqtSignal()

    LINE_TEXT_STR = 'lineText'
    CHAR_WIDTH_ARRAY = 'charWidthArray'
    NORMAL_LINE_PIXMAP = 'normalLineTextPixmap'

    
    UnvisibleCharSearcher = re.compile('[\s]{1,}')
    WordSearcher = re.compile('[0-9a-zA-Z]{1,}')
    ChineseSearcher = re.compile(u'[\u4e00-\u9fa5]+')
    Searchers = [UnvisibleCharSearcher,WordSearcher,ChineseSearcher]

    # 设当前行内容为lineText，当前光标的xIndexPos为curIndex（表示光标位置向左查，有curIndex个字符）
    # 该函数将会返回一个int值，该值为光标新位置距离旧位置的偏移。该位置恒为正
    # 光标的新位置为 光标向右移动一个“单词”之后的光标位置（skipSpaceAndWordByLeft表示向左移动一个单词之后的光标位置）
    #     单词的定义：连续的不可见字符（正则匹配中的\s）、连续的中文字符、连续的字母数字组合（[0-9a-zA-Z]）
    @staticmethod
    def skipSpaceAndWordByRight(lineText,curIndex):
        rightText = lineText[curIndex:]
        for searcher in TextDocument.Searchers:
            matchObj = searcher.match(rightText)
            if matchObj != None:
                return matchObj.span()[1] - matchObj.span()[0]
        return 1

    @staticmethod
    def skipSpaceAndWordByLeft(lineText,curIndex):
        l = list(lineText)
        l.reverse()
        return TextDocument.skipSpaceAndWordByRight( ''.join(l) , len(lineText)-curIndex)

    # 文本改变装饰器（如果某函数的执行将会修改某行的文本，则需要使用该装饰器进行装饰）
    @staticmethod
    def __TextChangedDecorator(funcObj):
        def _deco(*arg1,**arg2):
            retuValue = funcObj(*arg1,**arg2)
            getattr(funcObj, '__self__').lineTextChangedSignal.emit()     # 已与对象绑定的函数会有一个属性__self__，它将标示已绑定的对象
            return retuValue
        return _deco


    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        __BaseDocument__.__init__(self, font, parent)
        
        # 用户操作记录
        self.__operateCache = OperateCache()
        for funcName in OperateCache.funcNames:
            setattr(self, funcName, getattr(self.__operateCache, funcName))
        
        # 当它们执行时，将会修改文本的内容。因此使用TextDocument.__TextChangedDecorator进行装饰，来响应文本的改动，并简化了代码
        # 注意，不能直接在insertText函数上直接@TextDocument.__TextChangedDecorator
        # 因为python解释器在生成TextDocument类的过程中，遇到insertText函数时将无法解析@TextDocument.__TextChangedDecorator（因为此时TextDocument还未产生）
        self.insertText = TextDocument.__TextChangedDecorator(self.insertText)
        self.deleteText = TextDocument.__TextChangedDecorator(self.deleteText)
        
        self.lineTextChangedSignal.connect(self.afterLineTextChanged)




    def findCharMatchedSettings(self,lineStr,lineIndex):
        if lineIndex % 2 == 0:
            return len(lineStr) * [ (CEGD.LineTextPen,self.getFont()) ]
        else:
            return len(lineStr) * [ (CEGD.StrTextPen,self.getFont()) ]

    # @FUF.funcExeTime
    def afterLineTextChanged(self):
        text = ''
        for index in range(self.getLineCount()):
            text += self.getLineTextByIndex(index) + self.getSplitedChar()
        self.__text = text
        #print (re.findall( '\'\'\'' , text, re.MULTILINE))



    def redoOneStep(self):
        lastOperate = self.popOperates()
        if lastOperate == None:
            return
        for index in range(len(lastOperate)):
            record = lastOperate[len(lastOperate)-index-1]
            if record.recordType == OperateRecord.OPERATETYPE_INSERTTEXT:
                self.insertText( record.indexPos, record.text , False)
            elif record.recordType == OperateRecord.OPERATETYPE_DELETETEXT:
                self.deleteText( record.indexPos, record.length, False)
        return lastOperate
    
    







        

    def insertText(self,xyIndexPosTuple,text,record = True):
        splitedTexts = FUF.splitTextToLines(text)['splitedTexts']
        indexPos = xyIndexPosTuple
        for index in range(len( splitedTexts )-1):
            indexPos = self.__insertTextWithoutLineBreak( indexPos , splitedTexts[index], record)
            indexPos = self.__insertLineBreak( indexPos , record)
        return self.__insertTextWithoutLineBreak( indexPos , splitedTexts[-1], record)


    # 插入一个换行符
    def __insertLineBreak(self,xyIndexPosTuple,record = True):
        xPos,yPos = xyIndexPosTuple
        curLineText = self.getLineTextByIndex(yPos)
        self.changeLineText(yPos,curLineText[0:xPos] )
        self.addLine( yPos + 1,curLineText[xPos:len(curLineText)] )
        
        # 记录操作
        if record == True:
            self.addRecord( OperateRecord.deleteText( (len(curLineText),yPos),1 ) )
        
        return (0,yPos+1)
        
    # 插入一段没有换行符的文本
    def __insertTextWithoutLineBreak(self,xyIndexPosTuple,text,record = True):        
        xPos,yPos = xyIndexPosTuple
        curLineText = self.getLineTextByIndex(yPos)
        self.changeLineText(yPos, curLineText[0:xPos] + text + curLineText[xPos:len(curLineText)])
        
        # 记录操作
        if record == True:
            self.addRecord( OperateRecord.deleteText( (xPos,yPos),len(text) ) )
         
        return ( len(curLineText[0:xPos] + text) ,yPos)
        
    # 从xyPos的位置起向右删掉length长度的字符
    def deleteText(self,xyIndexPosTuple,length,record = True):
        xPos,yPos = xyIndexPosTuple
        
        while len(self.getLineTextByIndex(yPos))-xPos < length:
            self.__deleteLineBreak(yPos,record)
            length -= 1            
        curLineText = self.getLineTextByIndex(yPos)
        self.changeLineText( yPos,curLineText[0:xPos]+curLineText[xPos+length:len(curLineText)] )

        if record == True:
            self.addRecord( OperateRecord.insertText( (xPos,yPos),curLineText[xPos:xPos+length] ) )

        return xyIndexPosTuple

    # 删掉第lineIndex行的行尾换行符，其实质是将第lineIndex和第lineIndex+1行的文本合并为一行
    # 如果不存在第lineIndex+1行，则什么都不做
    def __deleteLineBreak(self,lineIndex,record = True):
        text1 = self.getLineTextByIndex(lineIndex)
        text2 = self.getLineTextByIndex(lineIndex+1,'')
        self.changeLineText(lineIndex, text1+text2)
        self.delLine(lineIndex+1)
    
        # 记录操作
        if record == True:
            self.addRecord( OperateRecord.insertText( (len(text1),lineIndex),self.getSplitedChar() ) )
    
    
    
    
    
    

    # 计算从indexPos1到indexPos2的距离（认为indexPos1是起点，indexPos2是终点）
    # 如果absValue为True，则返回距离的绝对值，否则，
    def calcIndexPosDistance(self,indexPos1,indexPos2,absValue = True):        
        
        sortedIndexPosDict = FUF.sortedIndexPos(indexPos1, indexPos2)
        positiveSign = -1 if (sortedIndexPosDict['changed'] == True) and (absValue == False) else 1
        
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
        xPos,yPos = xyIndexPosTuple

        lineText = self.getLineTextByIndex(yPos)
        if lineText == None:
            return False
        if (xPos < 0) or (xPos > len(lineText)):
            return False
        return True
    def formatIndexPos(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple

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
    
    
    
    


           
    moveIndexPosLeft    = lambda self,xyIndexPosTuple,distance = 1: self.__moveIndexPosByX(xyIndexPosTuple,-int(distance))
    moveIndexPosRight   = lambda self,xyIndexPosTuple,distance = 1: self.__moveIndexPosByX(xyIndexPosTuple,int(distance))
    moveIndexPosUp      = lambda self,xyIndexPosTuple,distance = 1: self.__moveIndexPosByY(xyIndexPosTuple,-distance)
    moveIndexPosDown    = lambda self,xyIndexPosTuple,distance = 1: self.__moveIndexPosByY(xyIndexPosTuple, distance)
        
    # 左移一个单词
    def moveIndexPosLeftByWord(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple
        off = TextDocument.skipSpaceAndWordByLeft( self.getLineTextByIndex(yPos),xPos )
        return self.__moveIndexPosByX(xyIndexPosTuple, -off)
    
    # 右移一个单词
    def moveIndexPosRightByWord(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple
        off = TextDocument.skipSpaceAndWordByRight( self.getLineTextByIndex(yPos),xPos )
        return self.__moveIndexPosByX(xyIndexPosTuple, off)
    
    def __moveIndexPosByY(self,xyIndexPosTuple,distance):
        if distance == 0:
            return xyIndexPosTuple
        xPos,yPos = xyIndexPosTuple
        yPos += distance
        
        if yPos < 0:
            yPos = 0
        elif yPos >= self.getLineCount():
            yPos = self.getLineCount()-1
        
        curLineText = self.getLineTextByIndex(yPos)
        if xPos > len(curLineText):
            xPos = len(curLineText)
        return (xPos,yPos)
    
    # 大于0则右移，小于0则左移
    def __moveIndexPosByX(self,xyIndexPosTuple,distance):
        if distance == 0:
            return xyIndexPosTuple
        
        xPos,yPos = xyIndexPosTuple
        xPos += distance
        if xPos < 0:
            while True:
                yPos -= 1
                if yPos < 0:
                    return (0,0)
                xPos += len(self.getLineTextByIndex(yPos)) + 1
                if xPos >= 0:
                    return (xPos,yPos)                
            
        elif xPos >= len(self.getLineTextByIndex(yPos))+1:
            while True:
                xPos -= ( len(self.getLineTextByIndex(yPos))+1 )                
                yPos += 1
                if yPos >= self.getLineCount():
                    l = self.getLineCount() - 1
                    return ( len(self.getLineTextByIndex(l)),l )                
                if xPos <= len(self.getLineTextByIndex(yPos)):
                    return (xPos,yPos)
        else:
            return (xPos,yPos)
        