
import re
from PyQt5 import QtCore,QtGui
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.ToolClass.OperateCache import OperateCache, OperateRecord
from CodeEditor.ToolClass.RetuInfo import RetuInfo


'''
TextDocument.__lineTextInfoDictArray的注释信息
一个Array，其中的每项都是一个dict，称为lineTextInfoDict，它的格式是：
lineTextInfoDict['lineText']                   一个字符串，该行文本的字符串
lineTextInfoDict['lineTextPixmap']             一个QPixmap对象，绘制对应行文本时，就把这个pixmap绘制到界面上（原始图片）
lineTextInfoDict['lineTextCharWidthArray']     绘制到QPixmap对象上时，每个字符的字符宽度（像素数）
'''

# 主要负责进行文本的绘制工作相关
class BaseDocument(QtCore.QObject):

    LINEADD = 0
    LINECHANGED = 1
    LINEDELETE = 2
    LINELEVELCHANGEDSTATE = [LINEADD,LINECHANGED,LINEDELETE]
    
    # 该信号在某行文本被改变时触发：
    # 参数的含义：
    #     如果为None，则说明是因为setText导致的改变
    #     如果为有效的tuple，则将会是一个三元组
    #         data[0] BaseDocument.LINELEVELCHANGEDSTATE 中的一种
    #         data[1]、data[2] 与data[0]对应函数（addLine、delLine、setLineText）的参数列表一致
    lineLevelTextChangedSignal = QtCore.pyqtSignal( object )


    # 当某行的pixmap、charWidthArr信息被重新生成时，该信号被发射
    # 注意，当该行文本改变、或者设置该行的这些数据失效时，都会引发该信号
    afterGeneratePixmapAndCharWidthArrSignal = QtCore.pyqtSignal(object)


    LINETEXT_STR = 'lineText'
    LINETEXT_PIXMAP = 'lineTextPixmap'
    LINETEXT_CHARWIDTHARRAY = 'lineTextCharWidthArray'
    
    UnvisibleCharSearcher = re.compile('[\s]{1,}')
    WordSearcher = re.compile('[0-9a-zA-Z]{1,}')
    ChineseSearcher = re.compile(u'[\u4e00-\u9fa5]+')
    Searchers = [UnvisibleCharSearcher,WordSearcher,ChineseSearcher]

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
    def getChineseCharFont(self):
        return self.__chineseCharFont

    
    def refreshLineMaxWidth(self,lineWidth):
        self.__lineMaxWidth = max( [ self.__lineMaxWidth,lineWidth ] )
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
            self.__lineTextInfoDictArray.append({BaseDocument.LINETEXT_STR:text})
            
        self.lineLevelTextChangedSignal.emit(None)
        
    def getText(self):
        if self.__isDataDirty == True:
            self.__text = ''
            for index in range (self.getLineCount()):
                self.__text += self.getLineText(index) + self.getSplitedChar()

        self.__isDataDirty = False
        return self.__text
    
    def getSplitedChar(self):
        return self.__splitedChar
    
    
    
    
    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        QtCore.QObject.__init__(self,parent)
        
        # 注释看文件头的注释
        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0             # 实时保存最大像素宽度
        self.setFont( font )

        self.__isDataDirty = False
        self.lineLevelTextChangedSignal.connect( self.__onUserOperate )
                
    def __onUserOperate(self,info):
        self.__isDataDirty = ( info != None )



    
    def isLineIndexValid(self,index):
        if (index < 0) or (index >= self.getLineCount()):
            return False
        else:
            return True
        
    # 增加行：文本将会把newText插入到lineIndex之前，使newText成为新的第lineIndex号元素
    def addLine(self,lineIndex,newText):
        if lineIndex < 0:
            return False
        self.__lineTextInfoDictArray.insert(lineIndex, {BaseDocument.LINETEXT_STR:newText})
        self.lineLevelTextChangedSignal.emit( (BaseDocument.LINEADD,lineIndex,newText) )
        return True
    
    # 删除行
    def delLine(self,lineIndex):
        if self.isLineIndexValid(lineIndex) == False:
            return False
        
        if self.getLineCount() == 1:
            self.setLineText(0, '')
        else:
            self.__lineTextInfoDictArray.remove( self.__lineTextInfoDictArray[lineIndex] )
            self.lineLevelTextChangedSignal.emit( (BaseDocument.LINEDELETE,lineIndex,None) )
        return True
    
    # 修改行文本，并删除其它所有的行数据        
    def setLineText(self,lineIndex,newText):
        if self.isLineIndexValid(lineIndex) == False:
            return False
        self.__lineTextInfoDictArray[lineIndex] = {BaseDocument.LINETEXT_STR:newText}
        self.lineLevelTextChangedSignal.emit( (BaseDocument.LINECHANGED,lineIndex,newText) )
        return True
    
    # 获取行文本    
    def getLineText(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue 
        return self.__lineTextInfoDictArray[index][BaseDocument.LINETEXT_STR]
    
    # 设置行其它数据
    def setLineTextInfoByKey(self,index,key,value):
        if self.isLineIndexValid(index) == False:
            return False
        if key == BaseDocument.LINETEXT_STR:
            return False
        self.__lineTextInfoDictArray[index][key] = value
        return True
    
    # 获取行其它数据
    def getLineTextInfoByKey(self,index,key):
        if self.isLineIndexValid(index) == False:
            return None
        return self.__lineTextInfoDictArray[index].get(key)

    # 清除行其它数据
    def clearLineTextInfoDict(self,index):
        if self.isLineIndexValid(index) == False:
            return False
        return self.setLineText(index, self.getLineText(index))
    

    
    # 作为判断某行的pixmap数据和charWidthArr数据是否有效，可以被继承并重写
    # 返回值：
    #    None  传入的行号越界
    #    True  传入的行号对应行的Pixmap数据和charWidthArr数据有效
    #    False 传入的行号对应行的Pixmap数据和charWidthArr数据无效，需要更新
    def isLinePixmapAndCharWidthArrValid(self,index):
        if self.isLineIndexValid(index) == False:
            return None
        if self.getLineTextInfoByKey(index, BaseDocument.LINETEXT_PIXMAP) == None or \
            self.getLineTextInfoByKey(index, BaseDocument.LINETEXT_CHARWIDTHARRAY) == None:
            return False
        else:
            return True
    
    

    # 以下几个方法的参数outOfIndexValue，是指当传入的index越限时，将会返回的值
    def getLineCharWidthArrayByIndex(self,index,outOfIndexValue=None):
        retV = self.isLinePixmapAndCharWidthArrValid(index)
        if retV == None:
            return outOfIndexValue
        if retV == False:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.getLineTextInfoByKey(index, BaseDocument.LINETEXT_CHARWIDTHARRAY)  
            
    def getLinePixmapByIndex(self,index,outOfIndexValue=None):
        retV = self.isLinePixmapAndCharWidthArrValid(index)
        if retV == None:
            return outOfIndexValue
        if retV == False:
            self.__refreshLineTextInfoDictByIndex(index)
        return self.getLineTextInfoByKey(index, BaseDocument.LINETEXT_PIXMAP)  
        
  



    # 根据当前最新的文本，来重绘文本信息，并将重绘之后的数据进行存储
    def __refreshLineTextInfoDictByIndex(self,index):
        lineHeight = self.getFontMetrics().lineSpacing()        
        curLineText = self.getLineText(index)
        charMatchedSettings = self.generateCharMatchedSettings(index)

        pixmapObj = QtGui.QPixmap(len(curLineText)*( CEGD.CharDistancePixel + self.getFontMetrics().maxWidth() * 2 ),lineHeight)
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
        self.refreshLineMaxWidth( curXOff - letterRect.width() )
        self.setLineTextInfoByKey(index, BaseDocument.LINETEXT_PIXMAP, pixmapObj)
        self.setLineTextInfoByKey(index, BaseDocument.LINETEXT_CHARWIDTHARRAY, charWidthInfoArr)
        self.afterGeneratePixmapAndCharWidthArrSignal.emit(index)
        
        


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
    def generateCharMatchedSettings(self,lineIndex):
        arr = []
        for c in self.getLineText(lineIndex):
            arr.append( (CEGD.LineTextPen,self.getChineseCharFont() if FUF.isChineseChar(c) else self.getFont() ) )
        return arr        


















class TextDocument(BaseDocument):
    
    
    # 该信号在用户完成某项操作（修改了文本内容）后触发
    # 参数的含义：
    #     如果它等于None，则表明是在setText中传入的
    #     否则，它将为一个list，其中保存着用户操作的操作记录（参见TextDocument.insertText和TextDocument.deleteText）
    totalLevelTextChangedSignal = QtCore.pyqtSignal(object)
    
    
    
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
                return RetuInfo.info( searcher = searcher, offset = matchObj.span()[1] - matchObj.span()[0] )
        return RetuInfo.info( searcher = None,offset = 1)
        
    @staticmethod
    def skipSpaceAndWordByLeft(lineText,curIndex):
        l = list(lineText)
        l.reverse()
        return TextDocument.skipSpaceAndWordByRight( ''.join(l) , len(lineText)-curIndex)
    
    
    def setText(self, text=''):
        BaseDocument.setText(self, text=text)
        self.totalLevelTextChangedSignal.emit(None)
        

    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        BaseDocument.__init__(self, font, parent)
        
        # 用户操作记录
        self.__operateCache = OperateCache()
        for funcName in OperateCache.funcNames:
            setattr(self, funcName, getattr(self.__operateCache, funcName))
                

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
    
    


    # 插删字符串操作对外的接口
    def insertText(self,xyIndexPosTuple,text,record = True):
        retuDict = self.__insertText(xyIndexPosTuple, text)
        
        if record == True:
            for r in retuDict['operateRecords']:
                self.addRecord( r )
        
        self.totalLevelTextChangedSignal.emit(retuDict['operateRecords'])
        
        return retuDict['indexPos']

    def deleteText(self,xyIndexPosTuple,length,record = True):
        retuDict = self.__deleteText(xyIndexPosTuple, length)
        
        if record == True:
            for r in retuDict['operateRecords']:
                self.addRecord( r )

        self.totalLevelTextChangedSignal.emit(retuDict['operateRecords'])

        return retuDict['indexPos']

        

    def __insertText(self,xyIndexPosTuple,text):
        splitedTexts = FUF.splitTextToLines(text)['splitedTexts']
        indexPos = xyIndexPosTuple
        operateRecords = []
        
        for index in range(len( splitedTexts )-1):
            retuDict = self.__insertTextWithoutLineBreak( indexPos , splitedTexts[index])
            indexPos = retuDict['newXYIndexPos']
            operateRecords.append( retuDict['operateRecord'] )
            
            retuDict = self.__insertLineBreak( indexPos)
            indexPos = retuDict['newXYIndexPos']
            operateRecords.append( retuDict['operateRecord'] )
        
        retuDict = self.__insertTextWithoutLineBreak( indexPos , splitedTexts[-1])
        indexPos = retuDict['newXYIndexPos']
        operateRecords.append( retuDict['operateRecord'] )
        
        return RetuInfo.info( indexPos = indexPos,operateRecords = operateRecords )

    # 插入一个换行符
    def __insertLineBreak(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple
        curLineText = self.getLineText(yPos)
        self.setLineText(yPos,curLineText[0:xPos] )
        self.addLine( yPos + 1,curLineText[xPos:len(curLineText)] )
        
        newXYIndexPos = (0,yPos+1)
        operateRecord = OperateRecord.deleteText( (len(curLineText),yPos),1 )
        return RetuInfo.info( newXYIndexPos=newXYIndexPos,operateRecord=operateRecord )

    # 插入一段没有换行符的文本
    def __insertTextWithoutLineBreak(self,xyIndexPosTuple,text):        
        xPos,yPos = xyIndexPosTuple
        curLineText = self.getLineText(yPos)
        self.setLineText(yPos, curLineText[0:xPos] + text + curLineText[xPos:len(curLineText)])

        newXYIndexPos = ( len(curLineText[0:xPos] + text) ,yPos)
        operateRecord = OperateRecord.deleteText( (xPos,yPos),len(text) )
        return RetuInfo.info( newXYIndexPos=newXYIndexPos,operateRecord=operateRecord )
    
    # 从xyPos的位置起向右删掉length长度的字符
    def __deleteText(self,xyIndexPosTuple,length):
        xPos,yPos = xyIndexPosTuple
        operateRecords = []
        
        while len(self.getLineText(yPos))-xPos < length:
            retuRecord = self.__deleteLineBreak(yPos)
            operateRecords.append( retuRecord )
            length -= 1            
        
        curLineText = self.getLineText(yPos)
        self.setLineText( yPos,curLineText[0:xPos]+curLineText[xPos+length:len(curLineText)] )
        operateRecords.append( OperateRecord.insertText( (xPos,yPos),curLineText[xPos:xPos+length] ) )

        return RetuInfo.info( indexPos = xyIndexPosTuple,operateRecords = operateRecords )

    # 删掉第lineIndex行的行尾换行符，其实质是将第lineIndex和第lineIndex+1行的文本合并为一行
    # 如果不存在第lineIndex+1行，则什么都不做
    def __deleteLineBreak(self,lineIndex):
        text1 = self.getLineText(lineIndex)
        text2 = self.getLineText(lineIndex+1,'')
        self.setLineText(lineIndex, text1+text2)
        self.delLine(lineIndex+1)
    
        return OperateRecord.insertText( (len(text1),lineIndex),self.getSplitedChar() )
    
    
    
    
    
    

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
            absV = len(self.getLineText(indexPosA[1])) - indexPosA[0] + 1
            absV += indexPosB[0]
            for index in range( indexPosA[1]+1,indexPosB[1] ):
                absV += len(self.getLineText(index)) + 1
        return positiveSign * absV
    
    # 判断xyIndexPosTuple所标示的光标位置是否存在
    def isIndexPosValid(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple

        lineText = self.getLineText(yPos)
        if lineText == None:
            return False
        if (xPos < 0) or (xPos > len(lineText)):
            return False
        return True
    def formatIndexPos(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple

        lineText = self.getLineText(yPos)
        if lineText == None:
            if yPos < 0:
                return (0,0)
            else:
                l = self.getLineCount()-1
                return ( len(self.getLineText(l)),l )
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
        off = TextDocument.skipSpaceAndWordByLeft( self.getLineText(yPos),xPos )['offset']
        return self.__moveIndexPosByX(xyIndexPosTuple, -off)
    
    # 右移一个单词
    def moveIndexPosRightByWord(self,xyIndexPosTuple):
        xPos,yPos = xyIndexPosTuple
        off = TextDocument.skipSpaceAndWordByRight( self.getLineText(yPos),xPos )['offset']
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
        
        curLineText = self.getLineText(yPos)
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
                xPos += len(self.getLineText(yPos)) + 1
                if xPos >= 0:
                    return (xPos,yPos)                
            
        elif xPos >= len(self.getLineText(yPos))+1:
            while True:
                xPos -= ( len(self.getLineText(yPos))+1 )                
                yPos += 1
                if yPos >= self.getLineCount():
                    l = self.getLineCount() - 1
                    return ( len(self.getLineText(l)),l )                
                if xPos <= len(self.getLineText(yPos)):
                    return (xPos,yPos)
        else:
            return (xPos,yPos)














