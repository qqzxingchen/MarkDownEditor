
import keyword,re,copy

from PyQt5 import QtGui

from CodeEditor.MainClass.TextDocument import TextDocument
from CodeEditor.MainClass.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF

from CodeEditor.DataClass.RetuInfo import RetuInfo


class PythonTextDocument(TextDocument):
    
    DESC_STR_INDEXPOS_ARRAY = 'descAndStrInfo'
    LASTKEY_ARR = [None,"'",'"',"'''",'"""']
    PENARR = [CEGD.LineTextPen,CEGD.TextTokenPen,CEGD.ExplainNotePen,CEGD.StrTextPen]    
        
    
    # @FUF.funcExeTime
    def getSharpAndQuotePos(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.getLineTextInfoByKey(index, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY) == None:
            return self.__findSharpAndQuotePos(index)
        return self.getLineTextInfoByKey(index, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY)

    # 重写 isLinePixmapAndCharWidthArrValid 函数，使得某行的pixmap等信息可以被该类直接控制：
    # 如果行号存在于self.__invalidPixmapAndCharWidthArrIndexs中，则该行的这类数据一定是无效的
    def isLinePixmapAndCharWidthArrValid(self,index):
        retV = TextDocument.isLinePixmapAndCharWidthArrValid(self, index)
        if retV == True:
            return self.__invalidPixmapAndCharWidthArrIndexs.count(index) == 0
        else:
            return retV
    
    
    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        TextDocument.__init__(self, font, parent)
        
        self.__descIndexPosArr = []
        self.__strIndexPosArr = []
        self.__invalidPixmapAndCharWidthArrIndexs = []

        self.totalLevelTextChangedSignal.connect(self.afterUserOperate)
        self.afterGeneratePixmapAndCharWidthArrSignal.connect(self.afterGeneratePixmapAndCharWidthArr)
        
    
    # 作为一个代码编辑器，文本高亮是必备的。因此，区分位于注释内、位于字符串内的代码语句块是很有必要的
    # 当前的实现方法是，每行文本内容改变时，都将会重新生成该行文本内 注释关键字(python中是#)、字符串边界关键字(python中包括：' " ''' """)在该行中的位置
    #     然后当用户的一步操作之后（可能多行文本都发生了改变），将会根据该行文本内关键字的位置，重新生成 注释、字符串的边界的IndexPos范围
    #     注意：该函数在实现时，是lazy的，也就是说，除非有人调用 self.getSharpAndQuotePos，否则该函数不会被调用
    # 如果要适配于其它语言，则可能不需要缓存每行的这些位置，也即根本就不需要重写该函数
    # 返回值：
    #     默认是空的list（[]）
    #     如果重写了该函数，那么为了利用它，一般也需要重写 afterUserOperate 函数
    # 根据指定的lineIndex，找到该行中包含的 # 、 连续的 ' 、 连续的 " 的位置
    def __findSharpAndQuotePos(self,lineIndex):
        arr = self.__calcSharpAndQuotePoss( self.getLineText(lineIndex) )
        afterExecuteArr = []
        for key in PythonTextDocument.LASTKEY_ARR:
            retuDict = self.__calcDescAndStrIndexPosRanges(key, lineIndex, copy.deepcopy(arr))            
            afterExecuteArr.append( retuDict )
        self.setLineTextInfoByKey(lineIndex, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY,afterExecuteArr )
        return afterExecuteArr



    def afterGeneratePixmapAndCharWidthArr(self,index):
        if self.__invalidPixmapAndCharWidthArrIndexs.count(index) != 0:
            self.__invalidPixmapAndCharWidthArrIndexs.remove(index)

    def afterUserOperate(self,operates):
        if operates == None:
            for index in range(self.getLineCount()):
                self.__findSharpAndQuotePos(index)

        self.__invalidPixmapAndCharWidthArrIndexs = list(range(self.getLineCount()))
        self.__descIndexPosArr = []
        self.__strIndexPosArr = []
        self.__descAndStrCurState = { 'executedLine':0,'lastKey':None }

    # 在afterUserOperate函数执行完毕之后，self.__descIndexPosArr和self.__strIndexPosArr都是空的
    def generateStrAndDescRangesToLineIndex(self,lineIndex):
        if lineIndex > self.getLineCount():
            lineIndex = self.getLineCount() 
        if lineIndex <= self.__descAndStrCurState['executedLine']:
            return
        
        lastKey = self.__descAndStrCurState['lastKey']
        for index in range( self.__descAndStrCurState['executedLine'],lineIndex ):
            afterExecuteArr = self.getSharpAndQuotePos(index)
            item = afterExecuteArr[ PythonTextDocument.LASTKEY_ARR.index( lastKey ) ]
            
            for pos in item['descIndexPosArr']:
                self.__descIndexPosArr.append( (pos,index) )
            for pos in item['strIndexPosArr']:
                self.__strIndexPosArr.append( (pos,index) )
            lastKey = item['lastKey']
            lastPos = item['lastPos']
            if lastPos != None:
                self.__strIndexPosArr.append( (lastPos,index) )
        self.__descAndStrCurState = { 'executedLine':lineIndex,'lastKey':lastKey }

    def __isIndexPosInRange(self,indexPos,start,end):
        if start[1] == end[1]:
            if indexPos[1] == start[1] and start[0] <= indexPos[0] and indexPos[0] < end[0]:
                return True
        else:
            if indexPos[1] == start[1] and indexPos[0] >= start[0]:
                return True
            elif indexPos[1] == end[1] and indexPos[0] < end[0]:
                return True
            elif indexPos[1] > start[1] and indexPos[1] < end[1]:
                return True
        return False

    # 根据Python的规则，找到 #、'、" 的位置以及个数
    def __calcSharpAndQuotePoss(self,lineText):
        arr = []
        index = 0
        while index < len(lineText):
            if ["'",'"','#'].count( lineText[index] ) == 0:
                index += 1
                continue            
            
            if lineText[index] == '#':
                pos = index
                token = '#'
            elif lineText[index] == '\'' or lineText[index] == '\"':
                pos = index
                token = lineText[index]
                
                for c in lineText[index+1:]:
                    if c == token[0]:
                        token += c
                    else:
                        break
            
            arr.append( (pos,token) )
            index += len(token)
        return arr

    def __calcDescAndStrIndexPosRanges(self,lastKey,lineIndex,sharpAndQuotePoss):
        lineText = self.getLineText(lineIndex)
        descIndexPosArr = []
        strIndexPosArr = []
        
        lastPos = None 
        index = 0
        while index < len(sharpAndQuotePoss):
            pos,token = sharpAndQuotePoss[index]
            index += 1
            
            if lastKey == None:
                if token == '#':
                    descIndexPosArr.append( pos )       # 如果一个 # 不在字符串内，则它右边的字符串将会全部视为注释
                    break
                else:
                    if len(token) == 1 or len(token) == 3:
                        lastPos = pos
                        lastKey = token
                    elif len(token) == 2:
                        strIndexPosArr.append( pos )
                        strIndexPosArr.append( pos+2 )
                        # strIndexPosArr.append( {'start':,'end':,'key':token[0]} )
                    elif len(token) > 3:
                        lastKey = token[0:3]
                        lastPos = pos
                        sharpAndQuotePoss.insert( index, (pos+3,token[3:]) )
            
            elif lastKey == "'''" or lastKey == '"""' or lastKey == "'" or lastKey == '"':
                if lastKey[0] != token[0]:
                    continue
            
                # 如果当前遇到的token的左侧存在转义符的个数为奇数个，则token中的第一个字符将会被转义
                # realEscapeNumber表示作为转义符而存在的转义符（如 '\\'中的第二个 \ ，实际上是作为被转义符而不是转义符存在的）
                realEscapeNumber = PythonTextDocument.__findEscapeCharNumberFromRightToLeft(lineText,pos) % 2
                pos += realEscapeNumber
                token = token[realEscapeNumber:]
                
                # 如果剩下来的边界字符个数小与lastKey的字符个数，则表明本次匹配失败
                lastKeyLength = len(lastKey)
                if len(token) < lastKeyLength:
                    continue
                else:
                    if lastPos != None:
                        strIndexPosArr.append( lastPos )
                    strIndexPosArr.append( pos+lastKeyLength )

                    lastKey = None
                    lastPos = None
                    
                    # 如果剩下来的边界字符个数大与lastKey的字符个数，则需要将剩下来的字符再放回去
                    if len(token) >  lastKeyLength:
                        sharpAndQuotePoss.insert( index, (pos+lastKeyLength,token[lastKeyLength:]) )                    
        
        # 如果该行剩余 ' 或 " 没有匹配，则默认匹配到该行尾（不跨行）
        if lastKey == '"' or lastKey == "'":
            if PythonTextDocument.__findEscapeCharNumberFromRightToLeft( lineText,len(lineText) ) % 2 == 0:
                if lastPos != None:
                    strIndexPosArr.append( lastPos )
                strIndexPosArr.append( len(lineText) )
                lastKey = None
                lastPos = None
        
        return RetuInfo.info( descIndexPosArr=descIndexPosArr,strIndexPosArr=strIndexPosArr,lastKey=lastKey,lastPos=lastPos )

    # 计算从pos位置开始，向左查，一共有多少个连续的反斜杠，不包括对这个值的判断：lineText[pos]
    @staticmethod
    def __findEscapeCharNumberFromRightToLeft(lineText,pos):
        if len(lineText) < pos:
            return 0
        index = pos - 1
        escapeNumber = 0
        while index >= 0:
            if lineText[index] == '\\':
                escapeNumber += 1
                index -= 1
            else:
                return escapeNumber
        return escapeNumber
            
        



    def getStrPosByYPos(self,yPos):
        self.generateStrAndDescRangesToLineIndex( (int(yPos/100)+1)*100 )
        lineTextLength = len(self.getLineText(yPos))
        complementStrRanges = self.__strIndexPosArr + [ (lineTextLength,yPos) ]
        posArr = []
        for index in range( int(len(complementStrRanges)/2) ):
            start = complementStrRanges[index*2]
            end = complementStrRanges[index*2+1]
            if end[1] < yPos:
                continue
            if start[1] > yPos:
                break
            if start[1] < yPos:
                start = (0,yPos)
            if end[1] > yPos:
                end = (lineTextLength,yPos)
            posArr.append( start )
            posArr.append( end )
        return posArr

    def getDescPosByYPos(self,yPos):
        self.generateStrAndDescRangesToLineIndex( (int(yPos/100)+1)*100 )
        posArr = []
        for descPos in self.__descIndexPosArr:
            if descPos[1] == yPos:
                posArr.append( descPos )
            if descPos[1] > yPos:
                break
        return posArr


    
    def generateCharMatchedSettings(self,lineIndex):
        lineStr = self.getLineText(lineIndex)
        retuArr = []
        arr = len(lineStr) * [0]
        
        for metaObj in re.finditer( r'\b[a-zA-Z]+\b' , lineStr):
            if keyword.kwlist.count( lineStr[metaObj.span()[0]:metaObj.span()[1]] ) != 0:
                for index in range( metaObj.span()[0],metaObj.span()[1] ):
                    arr[index] = 1
        descPos = self.getDescPosByYPos(lineIndex)
        for descPos in descPos:
            for i in range( descPos[0],len(self.getLineText(lineIndex)) ):
                arr[i] = 2
        strPos = self.getStrPosByYPos(lineIndex)
        for index in range( int(len(strPos)/2) ):
            start = strPos[index*2]
            end = strPos[index*2+1]
            for i in range( start[0],end[0] ):
                arr[i] = 3
            
        for index in range(len(arr)):
            if FUF.isChineseChar(lineStr[index]):
                font = self.getChineseCharFont()
            else:
                font = self.getFont()                
            retuArr.append( ( PythonTextDocument.PENARR[ arr[index] ] ,font) )
        return retuArr



    




















    # 以下为老版本的部分函数
    '''
    def __genNewDescAndStrRange(self):
        lastKey = None
        lastPos = None
        descIndexPosArr = []
        strIndexPosArr = []
        
        import time
        sum13 = 0
                
        for index in range(self.getLineCount()):
            
            t0 = time.time()  
            
            afterExecuteArr = self.getSharpAndQuotePos(index)
            i = PythonTextDocument.LASTKEY_ARR.index( lastKey )
            item = afterExecuteArr[i]
            
            descIndexPosArr += item['descIndexPosArr']
            strIndexPosArr += item['strIndexPosArr']
            lastKey = item['lastKey']
            lastPos = item['lastPos']
            if lastPos != None:
                strIndexPosArr.append( lastPos )

            self.setLineTextInfoByKey(index, TextDocument.LINETEXT_PIXANDCHARWIDTHARRVALID, False)
            
            t3 = time.time()
            
            if t3-t0 != 0:
                print (index,"%.17fs" % (t3-t0))

        # 如果个数为奇数，那么表明某个左引号序列没有匹配的右引号序列，因此把行尾添加到list中
        if len(strIndexPosArr) % 2 != 0:
            l = self.getLineCount()-1
            strIndexPosArr.append( (len(self.getLineText(l)),l) )
        return RetuInfo.info( descIndexPosArr=descIndexPosArr,strIndexPosArr=strIndexPosArr )
    
    
    def isCharInStr(self,indexPos):
        self.generateStrAndDescRangesToLineIndex( (int(indexPos[1]/100)+1)*100 )
        for index in range( int( len(self.__strIndexPosArr)/2 ) ):
            start = self.__strIndexPosArr[index*2]
            end = self.__strIndexPosArr[index*2+1]
            if self.__isIndexPosInRange(indexPos, start, end) == True:
                return True
        if len(self.__strIndexPosArr) % 2 != 0:
            l = self.getLineCount()-1
            return self.__isIndexPosInRange( indexPos,self.__strIndexPosArr[-1],(len(self.getLineText(l)),l) )
        return False
        
        
    def isCharInDesc(self,indexPos):
        self.generateStrAndDescRangesToLineIndex( (int(indexPos[1]/100)+1)*100 )
        for descPos in self.__descIndexPosArr:
            if descPos[1] == indexPos[1] and descPos[0] <= indexPos[0]:
                return True
        return False
    

    
    @FUF.funcExeTime
    def generateCharMatchedSettings(self,lineIndex):
        lineStr = self.getLineText(lineIndex)
        retuArr = []
        arr = len(lineStr) * [0]
        
        for metaObj in re.finditer( r'\b[a-zA-Z]+\b' , lineStr):
            if keyword.kwlist.count( lineStr[metaObj.span()[0]:metaObj.span()[1]] ) != 0:
                for index in range( metaObj.span()[0],metaObj.span()[1] ):
                    arr[index] = 1
        for index in range(len(arr)):
            if self.isCharInDesc( (index,lineIndex) ):
                pen = CEGD.ExplainNotePen
            elif self.isCharInStr( (index,lineIndex) ):
                pen = CEGD.StrTextPen
            else:
                if arr[index] == 1:
                    pen = CEGD.TextTokenPen
                else:
                    pen = CEGD.LineTextPen

            if FUF.isChineseChar(lineStr[index]):
                font = self.getChineseCharFont()
            else:
                font = self.getFont()
                
            retuArr.append( (pen,font) )

        return retuArr
    '''


















