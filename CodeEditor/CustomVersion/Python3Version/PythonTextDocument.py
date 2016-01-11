
import keyword,re,copy

from PyQt5 import QtGui

from CodeEditor.TextDocument import TextDocument
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF
from CodeEditor.RetuInfo import RetuInfo

class PythonTextDocument(TextDocument):
    
    DESC_STR_INDEXPOS_ARRAY = 'descAndStrInfo'
    LASTKEY_ARR = [None,"'",'"',"'''",'"""']
    
    def getStrAndDescInfoByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.getLineTextInfo(index, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY) == None:
            self.__findLineDescAndStrPosInfo(index)
        return self.getLineTextInfo(index, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY)
        
    def getLineTextInfoDictByIndex(self,index,outOfIndexValue=None):
        if self.isLineIndexValid(index) == False:
            return outOfIndexValue
        if self.getLineTextInfo(PythonTextDocument.DESC_STR_INDEXPOS_ARRAY) == None:
            self.__findLineDescAndStrPosInfo(index)
        return TextDocument.getLineTextInfoDictByIndex(self, index, outOfIndexValue)
    
    
    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        TextDocument.__init__(self, font, parent)
        
        self.__descIndexPosArr = []
        self.__strIndexPosArr = []
        
        #self.userChangeTextSignal.connect(self.generateStrPosAndDescPos)
        self.userChangeTextSignal.connect(self.afterUserOperate)
        
    
    # 作为一个代码编辑器，文本高亮是必备的。因此，区分位于注释内、位于字符串内的代码语句块是很有必要的
    # 当前的实现方法是，每行文本内容改变时，都将会重新生成该行文本内 注释关键字(python中是#)、字符串边界关键字(python中包括：' " ''' """)在该行中的位置
    #     然后当用户的一步操作之后（可能多行文本都发生了改变），将会根据该行文本内关键字的位置，重新生成 注释、字符串的边界的IndexPos范围
    #     注意：该函数在实现时，是lazy的，也就是说，除非有人调用 self.getStrAndDescInfoByIndex、self.getLineTextInfoDictByIndex，否则该函数不会被调用
    # 如果要适配于其它语言，则可能不需要缓存每行的这些位置，也即根本就不需要重写该函数
    # 返回值：
    #     默认是空的list（[]）
    #     如果重写了该函数，那么为了利用它，一般也需要重写afterUserOperate函数
    
    
    # 根据指定的lineIndex，找到该行中包含的 # 、 连续的 ' 、 连续的 " 的位置
    
    def __findLineDescAndStrPosInfo(self,lineIndex):
        arr = self.__calcSharpAndQuotePoss( self.getLineTextByIndex(lineIndex) )
        afterExecuteArr = []
        for key in PythonTextDocument.LASTKEY_ARR:
            retuDict = self.__calcDescAndStrIndexPosRanges(key, lineIndex, copy.deepcopy(arr))            
            afterExecuteArr.append( retuDict )
        self.setLineTextInfo(lineIndex, PythonTextDocument.DESC_STR_INDEXPOS_ARRAY,afterExecuteArr )

        
    
    def afterUserOperate(self):
        #oldDescIndexPosArr = self.__descIndexPosArr
        #oldStrIndexPosArr = self.__strIndexPosArr
        
        retuDict = self.__genNewDescAndStrRange()
        self.__descIndexPosArr = retuDict['descIndexPosArr']
        self.__strIndexPosArr = retuDict['strIndexPosArr']

    
    def __genNewDescAndStrRange(self):
        lastKey = None
        lastPos = None
        descIndexPosArr = []
        strIndexPosArr = []
        
        for index in range(self.getLineCount()):
            afterExecuteArr = self.getStrAndDescInfoByIndex(index)
            i = PythonTextDocument.LASTKEY_ARR.index( lastKey )
            item = afterExecuteArr[i]
            
            descIndexPosArr += item['descIndexPosArr']
            strIndexPosArr += item['strIndexPosArr']
            lastKey = item['lastKey']
            lastPos = item['lastPos']
            if lastPos != None:
                strIndexPosArr.append( lastPos )

            self.clearCharWidthArrayByIndex(index)
            self.clearNormalLineTextPixmapByIndex(index)

        l = self.getLineCount()-1
        strIndexPosArr.append( (len(self.getLineTextByIndex(l)),l) )
        return RetuInfo.info( descIndexPosArr=descIndexPosArr,strIndexPosArr=strIndexPosArr )
    
    
    
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
        lineText = self.getLineTextByIndex(lineIndex)
        descIndexPosArr = []
        strIndexPosArr = []
        
        lastPos = None 
        index = 0
        while index < len(sharpAndQuotePoss):
            pos,token = sharpAndQuotePoss[index]
            index += 1
            
            if lastKey == None:
                if token == '#':
                    descIndexPosArr.append( (pos,lineIndex) )       # 如果一个 # 不在字符串内，则它右边的字符串将会全部视为注释
                    break
                else:
                    if len(token) == 1 or len(token) == 3:
                        lastPos = (pos,lineIndex)
                        lastKey = token
                    elif len(token) == 2:
                        strIndexPosArr.append( (pos,lineIndex) )
                        strIndexPosArr.append( (pos+2,lineIndex) )
                        # strIndexPosArr.append( {'start':,'end':,'key':token[0]} )
                    elif len(token) > 3:
                        lastKey = token[0:3]
                        lastPos = (pos,lineIndex)
                        sharpAndQuotePoss.insert( index, (pos+3,token[3:]) )
            
            elif lastKey == "'''" or lastKey == '"""' or lastKey == "'" or lastKey == '"':
                if lastKey[0] != token[0]:
                    continue
            
                # 如果当前遇到的token的左侧存在转义符的个数为奇数个，则token中的第一个字符将会被转义
                escapeNumber = 0
                i = pos-1
                while i >= 0:
                    if lineText[i] == '\\':
                        escapeNumber += 1
                        i -= 1
                    else:
                        break
                validLength = len(token) - escapeNumber % 2

                
                # 如果剩下来的边界字符个数小与lastKey的字符个数，则表明本次匹配失败
                lastKeyLength = len(lastKey)
                if validLength < lastKeyLength:
                    continue
                else:
                    if lastPos != None:
                        strIndexPosArr.append( lastPos )
                    strIndexPosArr.append( (pos+lastKeyLength,lineIndex) )

                    lastKey = None
                    lastPos = None

                    # 如果剩下来的边界字符个数大与lastKey的字符个数，则需要将剩下来的字符再放回去
                    if validLength > lastKeyLength:
                        sharpAndQuotePoss.insert( index, (pos+lastKeyLength,token[lastKeyLength:]) )
        
        # 如果该行剩余 ' 或 " 没有匹配，则默认匹配到该行尾（不跨行）
        if lastKey == '"' or lastKey == "'":
            if len(lineText) >= 1:
                if lineText[-1] != '\\':
                    if lastPos != None:
                        strIndexPosArr.append( lastPos )
                    strIndexPosArr.append( ( len(lineText) ,lineIndex) )
                    lastKey = None
                    lastPos = None
        
        return RetuInfo.info( descIndexPosArr=descIndexPosArr,strIndexPosArr=strIndexPosArr,lastKey=lastKey,lastPos=lastPos )



    def isCharInStr(self,indexPos):
        for index in range( int( len(self.__strIndexPosArr)/2 ) ):
            start = self.__strIndexPosArr[index*2]
            end = self.__strIndexPosArr[index*2+1]
        
            if start[1] == end[1]:
                if indexPos[1] == start[1]:
                    if (start[0] <= indexPos[0]) and (indexPos[0] < end[0]):
                        return True
            else:
                if indexPos[1] == start[1]:
                    if indexPos[0] >= start[0]:
                        return True
                elif indexPos[1] == end[1]:
                    if indexPos[0] < end[0]:
                        return True
                elif indexPos[1] > start[1] and indexPos[1] < end[1]:
                    return True

        return False
        
    def isCharInDesc(self,indexPos):
        for descPos in self.__descIndexPosArr:
            if descPos[1] == indexPos[1] and descPos[0] <= indexPos[0]:
                return True
        return False




    def generateCharMatchedSettings(self,lineIndex):
        lineStr = self.getLineTextByIndex(lineIndex)
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








