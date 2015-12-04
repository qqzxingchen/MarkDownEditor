
from PyQt5 import QtCore


class FrequentlyUsedFunc:
    @staticmethod
    def isEventKeyIsDirectionKey(key):
        return [QtCore.Qt.Key_Left,QtCore.Qt.Key_Right,QtCore.Qt.Key_Up,QtCore.Qt.Key_Down].count(key) != 0

    hasModifier         = lambda modifiers:int(modifiers) != int(QtCore.Qt.NoModifier)
    hasShiftModifier    = lambda modifiers:int(modifiers) &  int(QtCore.Qt.ShiftModifier) != 0
    hasCtrlModifier     = lambda modifiers:int(modifiers) &  int(QtCore.Qt.ControlModifier) != 0
    hasAltModifier      = lambda modifiers:int(modifiers) &  int(QtCore.Qt.AltModifier) != 0
    onlyShiftModifier   = lambda modifiers:int(modifiers) == int(QtCore.Qt.ShiftModifier)
    onlyCtrlModifier    = lambda modifiers:int(modifiers) == int(QtCore.Qt.ControlModifier)
    onlyAltModifier     = lambda modifiers:int(modifiers) == int(QtCore.Qt.AltModifier)
    
    @staticmethod
    def isIndexPosEqual(indexPos1,indexPos2):
        return (indexPos1[0] == indexPos2[0]) and (indexPos1[1] == indexPos2[1])
    
    @staticmethod
    def sortedIndexPos(indexPos1,indexPos2):
        if FrequentlyUsedFunc.isIndexPosEqual(indexPos1, indexPos2):
            return (indexPos1,indexPos2)
        
        if indexPos1[1] == indexPos2[1]:
            if indexPos1[0] >= indexPos2[0]:
                sortedIndexPosTuple = (indexPos2,indexPos1)
            else:
                sortedIndexPosTuple = (indexPos1,indexPos2)
        else:
            if indexPos1[1] > indexPos2[1]:
                sortedIndexPosTuple = (indexPos2,indexPos1)
            else:
                sortedIndexPosTuple = (indexPos1,indexPos2)
        return sortedIndexPosTuple
    



