
from PyQt5 import QtCore

from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF


class SelectedTextManager(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal()
    
    funcNames = ['setSelectTextIndexPos', 'addSelectTextIndexPos' , \
                 'getSelectedTextIndexPos','getSelectedTextIndexPosSorted' , \
                 'clearSelectedText']
    signalNames = ['updateSignal']
    
    def __init__(self,parent = None):
        QtCore.QObject.__init__(self,parent)
        self.__selectedTextIndexPos = None        
    
    # 将本次选中的文本与上次选中的文本进行合并
    def setSelectTextIndexPos(self,startIndexPosTuple,endIndexPosTuple,update = True):
        if self.__selectedTextIndexPos != None:
            if FUF.isIndexPosEqual( startIndexPosTuple,self.__selectedTextIndexPos[0] ) and \
                FUF.isIndexPosEqual( endIndexPosTuple,self.__selectedTextIndexPos[1] ):
                return
        if FUF.isIndexPosEqual( startIndexPosTuple,endIndexPosTuple ) == True:
            self.__selectedTextIndexPos = None
        else:
            self.__selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)
        if update == True:
            self.updateSignal.emit()
        
    def addSelectTextIndexPos(self,startIndexPosTuple,endIndexPosTuple,update = True):
        if self.__selectedTextIndexPos == None:
            self.__selectedTextIndexPos = (startIndexPosTuple,endIndexPosTuple)
        else:
            if FUF.isIndexPosEqual(self.__selectedTextIndexPos[1],startIndexPosTuple ):
                self.__selectedTextIndexPos = ( self.__selectedTextIndexPos[0],endIndexPosTuple )
            else:
                self.__selectedTextIndexPos = ( endIndexPosTuple,self.__selectedTextIndexPos[1] )
        if FUF.isIndexPosEqual(self.__selectedTextIndexPos[0],self.__selectedTextIndexPos[1]):
            self.__selectedTextIndexPos = None
        if update == True:
            self.updateSignal.emit()
            
    def getSelectedTextIndexPos(self):
        return self.__selectedTextIndexPos
    
    def getSelectedTextIndexPosSorted(self):
        selectedTextIndexPosRange = self.getSelectedTextIndexPos()
        if selectedTextIndexPosRange == None:
            return None
        
        selectedStart,selectedEnd = selectedTextIndexPosRange
        sortedInfoDict = FUF.sortedIndexPos( selectedStart , selectedEnd )
        return ( sortedInfoDict['first'],sortedInfoDict['second'] )
    
    
    
    def clearSelectedText(self,update = True):
        if self.__selectedTextIndexPos != None:
            self.__selectedTextIndexPos = None
            if update == True:
                self.updateSignal.emit()












