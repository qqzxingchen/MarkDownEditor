

from PyQt5 import QtCore


class TextDocument(QtCore.QObject):

    def __init__(self,text = '',parent=None):
        QtCore.QObject.__init__(self,parent)
        self.userData = {}      # 专门用来存放部分由其它类维护的易用信息
        self.setText(text)        
    
    def setText(self,text = ''):
        self.__text = text
        self.__afterTextChanged()
    
    def getText(self):
        return self.text
    def getSplitedTexts(self):
        return self.__splitedTexts
    def getSplitedChar(self):
        return self.__splitedChar

    # 获取行数
    def getLineCount(self):
        return len(self.__splitedTexts)
    
    # 获取第lineNumber行的内容
    def getTextByLineNumber(self,lineNumber):
        return self.__splitedTexts[lineNumber]


    def __afterTextChanged(self):
        splitN = self.__text.split('\n')
        splitRN = self.__text.split('\r\n')
        if len(splitN) == len(splitRN):
            self.__splitedTexts = splitRN
            self.__splitedChar = '\r\n'
        else:
            self.__splitedTexts = splitN
            self.__splitedChar = '\n'
    


