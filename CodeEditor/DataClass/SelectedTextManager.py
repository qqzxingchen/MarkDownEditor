
from PyQt5 import QtCore

from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF

'''
注意：
self.__selectedTextIndexPos是一个二元组
self.__selectedTextIndexPos[0] 光标的起始位置
self.__selectedTextIndexPos[1] 光标的结束位置
    lineText[ self.__selectedTextIndexPos[0][0]:self.__selectedTextIndexPos[1][0] ]正好表示了光标中间的字符串，这是巧合
'''

class SelectedTextManager(QtCore.QObject):
    selectedTextChangedSignal = QtCore.pyqtSignal()
        
    def __init__(self,parent = None):
        QtCore.QObject.__init__(self,parent)
        self.__selectedTextIndexPos = None
        
        #self.selectedTextChangedSignal.connect( lambda : print (self.getSelectedTextIndexPos()) )
    
    # 将本次选中的文本与上次选中的文本进行合并
    def setSelectTextIndexPos(self,startIndexPosTuple,endIndexPosTuple):
        if self.__selectedTextIndexPos != None:
            if FUF.isIndexPosEqual( startIndexPosTuple,self.__selectedTextIndexPos[0] ) and \
                FUF.isIndexPosEqual( endIndexPosTuple,self.__selectedTextIndexPos[1] ):
                return
        if FUF.isIndexPosEqual( startIndexPosTuple,endIndexPosTuple ) == True:
            self.__selectedTextIndexPos = None
        else:
            self.__selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)

        self.selectedTextChangedSignal.emit()
        
    def addSelectTextIndexPos(self,startIndexPosTuple,endIndexPosTuple):
        if self.__selectedTextIndexPos == None:
            self.__selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)
        else:
            if FUF.isIndexPosEqual(self.__selectedTextIndexPos[1],startIndexPosTuple ):
                self.__selectedTextIndexPos = ( self.__selectedTextIndexPos[0],endIndexPosTuple )
            else:
                self.__selectedTextIndexPos = ( endIndexPosTuple,self.__selectedTextIndexPos[1] )
        if FUF.isIndexPosEqual(self.__selectedTextIndexPos[0],self.__selectedTextIndexPos[1]):
            self.__selectedTextIndexPos = None

        self.selectedTextChangedSignal.emit()
    
        
    def getSelectedTextIndexPos(self):
        return self.__selectedTextIndexPos
    
    def getSelectedTextIndexPosSorted(self):
        selectedTextIndexPosRange = self.getSelectedTextIndexPos()
        if selectedTextIndexPosRange == None:
            return None
        
        selectedStart,selectedEnd = selectedTextIndexPosRange
        sortedInfoDict = FUF.sortedIndexPos( selectedStart , selectedEnd )
        return ( sortedInfoDict['first'],sortedInfoDict['second'] )
    
    
    
    def clearSelectedText(self):
        if self.__selectedTextIndexPos != None:
            self.__selectedTextIndexPos = None
            self.selectedTextChangedSignal.emit()












