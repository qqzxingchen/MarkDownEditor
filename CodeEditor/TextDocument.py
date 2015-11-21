

from PyQt5 import QtCore


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


    def __init__(self,text = '',parent=None):
        QtCore.QObject.__init__(self,parent)
        
        # 注释看文件头
        self.__lineTextInfoDictArray = []
        self.__lineMaxWidth = 0             # 实时保存最大像素宽度
        
        self.setText(text)      
        
    def setText(self,text = ''):
        self.__text = text
        self.__afterTextChanged()
    def getText(self):
        return self.text
    def getSplitedChar(self):
        return self.__splitedChar
        
        
          
    
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
        return self.__lineTextInfoDictArray[index].get(TextDocument.CHAR_WIDTH_ARRAY)
    def getNormalLineTextPixmapByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        return self.__lineTextInfoDictArray[index].get(TextDocument.NORMAL_LINE_PIXMAP)

    def getLineTextInfoDictByIndex(self,index):
        if index >= len(self.__lineTextInfoDictArray):
            return None
        return self.__lineTextInfoDictArray[index]
    
    def getMaxLineWidth(self):
        return self.__lineMaxWidth
    
    # 获取行数
    def getLineCount(self):
        return len(self.__lineTextInfoDictArray)


    

    

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
    

