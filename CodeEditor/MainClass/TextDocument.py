
from PyQt5 import QtCore,QtGui

from CodeEditor.DataClass.OperateCache import OperateCache, OperateRecord
from CodeEditor.DataClass.RetuInfo import RetuInfo

from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.MainClass.BaseDocument import BaseDocument


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
        self.operateCache = lambda : self.__operateCache

    def redoOneStep(self):
        lastOperate = self.operateCache().popOperates()
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
                self.operateCache().addRecord( r )
        
        self.totalLevelTextChangedSignal.emit(retuDict['operateRecords'])
        
        return retuDict['indexPos']

    def deleteText(self,xyIndexPosTuple,length,record = True):
        retuDict = self.__deleteText(xyIndexPosTuple, length)
        
        if record == True:
            for r in retuDict['operateRecords']:
                self.operateCache().addRecord( r )

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














