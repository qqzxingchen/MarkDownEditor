
import keyword,re

from PyQt5 import QtGui

from CodeEditor.TextDocument import TextDocument
from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF

class PythonTextDocument(TextDocument):
    def __init__(self,font=QtGui.QFont('Consolas',11) ,parent=None):
        TextDocument.__init__(self, font, parent)
        self.userChangeTextSignal.connect(self.generateStrPosAndDescPos)
    
    
    
    # 根据Python的规则，找到 #、'、" 的位置以及个数
    def generateDescAndStrIndexPoss(self,lineIndex):
        lineText = self.getLineTextByIndex(lineIndex)
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

                
    def generateStrPosAndDescPos(self):
        descIndexPosArr = []
        strIndexPosArr = []
        lastKey = None
        lastPos = None
        for lineIndex in range(self.getLineCount()):
            quotationMarksAndSharpPoss = self.getStrAndDescIndexPossByIndex(lineIndex)

            index = 0
            while index < len(quotationMarksAndSharpPoss):
                pos,token = quotationMarksAndSharpPoss[index]
                index += 1
                
                if lastKey == None:
                    if token == '#':
                        # 如果一个 # 不在字符串内，则它右边的字符串将会全部视为注释
                        descIndexPosArr.append( (pos,lineIndex) )
                        break
                    else:
                        if len(token) == 1 or len(token) == 3:
                            lastPos = (pos,lineIndex)
                            lastKey = token
                        elif len(token) == 2:
                            strIndexPosArr.append( {'start':(pos,lineIndex),'end':(pos+2,lineIndex),'key':token[0]} )
                        elif len(token) > 3:
                            lastKey = token[0:3]
                            lastPos = (pos,lineIndex)
                            quotationMarksAndSharpPoss.insert( index, (pos+3,token[3:]) )
                
                elif lastKey == "'''" or lastKey == '"""' or lastKey == "'" or lastKey == '"':
                    if lastKey[0] != token[0]:
                        continue
                
                    # 如果当前遇到的token的左侧存在转义符的个数为奇数个，则token中的第一个字符将会被转义                    
                    lineText = self.getLineTextByIndex(lineIndex)
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
                        # 否则，匹配成功
                        strIndexPosArr.append( {'start':lastPos,'end':(pos+lastKeyLength,lineIndex),'key':lastKey} )
                        lastKey = None
                        lastPos = None

                        # 如果剩下来的边界字符个数大与lastKey的字符个数，则需要将剩下来的字符再放回去
                        if validLength > lastKeyLength:
                            quotationMarksAndSharpPoss.insert( index, (pos+lastKeyLength,token[lastKeyLength:]) )
            
            # 如果该行剩余 ' 或 " 没有匹配，则默认匹配到该行尾（不跨行）
            if lastKey == '"' or lastKey == "'":
                lineTextLength = len(self.getLineTextByIndex(lineIndex))
                strIndexPosArr.append( { 'start':lastPos,'end':(lineTextLength,lineIndex),'key':lastKey } )
                lastKey = None
                lastPos = None

        # 如果剩余 ''' 或 """ 没有匹配，则默认匹配到该行尾（不跨行）
        if lastKey == '"""' or lastKey == "'''":
            lineTextLength = len(self.getLineTextByIndex(self.getLineCount()-1))
            strIndexPosArr.append( { 'start':lastPos,'end':(lineTextLength,self.getLineCount()-1),'key':lastKey } )
            lastKey = None
            lastPos = None

        self.descIndexPosArr = descIndexPosArr
        self.strIndexPosArr = strIndexPosArr
        for i in range(self.getLineCount()):
            self.clearLineTextInfoDict(i)

    def isCharInStr(self,indexPos):
        for posInfo in self.strIndexPosArr:
            start = posInfo['start']
            end = posInfo['end']
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
        for descPos in self.descIndexPosArr:
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








