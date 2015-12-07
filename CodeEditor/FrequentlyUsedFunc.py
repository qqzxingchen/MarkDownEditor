import time
from PyQt5 import QtCore
from CodeEditor.RetuInfo import RetuInfo



class FrequentlyUsedFunc:

    @staticmethod
    def isEventKeyIsDirectionKey(key):
        return [QtCore.Qt.Key_Left,QtCore.Qt.Key_Right,QtCore.Qt.Key_Up,QtCore.Qt.Key_Down].count(key) != 0
    
    @staticmethod
    def isEventKeyIsDeleteKey(key):
        return [QtCore.Qt.Key_Backspace,QtCore.Qt.Key_Delete].count(key) != 0

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
            retuObj = RetuInfo.info( first=indexPos1,second=indexPos2,changed=False )
        elif indexPos1[1] == indexPos2[1]:
            if indexPos1[0] >= indexPos2[0]:
                retuObj = RetuInfo.info( first=indexPos2,second=indexPos1,changed=True )
            else:
                retuObj = RetuInfo.info( first=indexPos1,second=indexPos2,changed=False )
        else:
            if indexPos1[1] > indexPos2[1]:
                retuObj = RetuInfo.info( first=indexPos2,second=indexPos1,changed=True )
            else:
                retuObj = RetuInfo.info( first=indexPos1,second=indexPos2,changed=False )
        return retuObj
    





    # 打印函数执行的时间
    # 用法：@FrequentlyUsedFunc.funcExeTime
    @staticmethod
    def funcExeTime(func):
        def newFunc(*args, **args2):  
            t0 = time.time()  
            retValue = func(*args, **args2)
            print ("%.4fs taken for {%s}" % (time.time() - t0, func.__name__))
            return retValue  
        return newFunc  







