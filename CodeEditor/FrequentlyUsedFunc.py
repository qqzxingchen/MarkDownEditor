import time,uuid
from PyQt5 import QtCore
from CodeEditor.RetuInfo import RetuInfo



class FrequentlyUsedFunc:
    SingleCharKeyRanges = [(0x20,0x2F),(0x3A,0x3F),(0x40,0x40), \
                           (0x5B,0x5F),(0x60,0x60),(0x7B,0x7E)]
    @staticmethod
    def isSingleCharKey(key):
        for keyRange in FrequentlyUsedFunc.SingleCharKeyRanges:
            if (key >= keyRange[0]) and (key <= keyRange[1]):
                return True
        return False
        
    isEventKeyIsDirectionKey    = lambda key : [QtCore.Qt.Key_Left,QtCore.Qt.Key_Right,QtCore.Qt.Key_Up,QtCore.Qt.Key_Down].count(key) != 0    
    isEventKeyIsDeleteKey       = lambda key : [QtCore.Qt.Key_Backspace,QtCore.Qt.Key_Delete].count(key) != 0
    isEventKeyIsNumber          = lambda key : (QtCore.Qt.Key_0 <= key) and (key <= QtCore.Qt.Key_9)
    isEventKeyIsChar            = lambda key : (QtCore.Qt.Key_A <= key) and (key <= QtCore.Qt.Key_Z)
    isEventKeyIsPageUpDownKey   = lambda key : [QtCore.Qt.Key_PageUp,QtCore.Qt.Key_PageDown].count(key) != 0
    isEventKeyIsHomeEndKey      = lambda key : [QtCore.Qt.Key_Home,QtCore.Qt.Key_End].count(key) != 0
    isEventKeyIsEnterKey        = lambda key : [QtCore.Qt.Key_Enter,QtCore.Qt.Key_Return].count(key) != 0
    isEventKeyIsTabKey          = lambda key : QtCore.Qt.Key_Tab == key

    hasModifier         = lambda modifiers:int(modifiers) != int(QtCore.Qt.NoModifier)
    hasShiftModifier    = lambda modifiers:int(modifiers) &  int(QtCore.Qt.ShiftModifier) != 0
    hasCtrlModifier     = lambda modifiers:int(modifiers) &  int(QtCore.Qt.ControlModifier) != 0
    hasAltModifier      = lambda modifiers:int(modifiers) &  int(QtCore.Qt.AltModifier) != 0
    onlyShiftModifier   = lambda modifiers:int(modifiers) == int(QtCore.Qt.ShiftModifier)
    onlyCtrlModifier    = lambda modifiers:int(modifiers) == int(QtCore.Qt.ControlModifier)
    onlyAltModifier     = lambda modifiers:int(modifiers) == int(QtCore.Qt.AltModifier)


    isChineseChar = lambda c : (ord(c) >= 0x4e00) and (ord(c) <= 0x9fa5)
    


    
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
    



    @staticmethod
    def splitTextToLines(text):
        splitN = text.split('\n')
        splitRN = text.split('\r\n')
        if len(splitN) == len(splitRN):
            splitedTexts = splitRN
            splitedChar = '\r\n'
        else:
            splitedTexts = splitN
            splitedChar = '\n'
        return RetuInfo.info( splitedTexts=splitedTexts,splitedChar=splitedChar )

    @staticmethod
    def calcMidNumberByRange(minNumber,value,maxNumber):
        minNumber = min( [minNumber,maxNumber] )
        maxNumber = max( [minNumber,maxNumber] )
        if value < minNumber:
            return minNumber
        elif value > maxNumber:
            return maxNumber
        else:
            return value
        
    @staticmethod
    def genUUID():
        return uuid.uuid1()


    # 打印函数执行的时间
    # 用法：@FUF.funcExeTime
    TotalTime = 0
    @staticmethod
    def funcExeTime(func):
        def newFunc(*args, **args2):  
            t0 = time.time()  
            retValue = func(*args, **args2)
            FrequentlyUsedFunc.TotalTime += time.time() - t0

            print ("%.10fs taken for {%s},total is %.10fs" % (time.time() - t0, func.__name__, FrequentlyUsedFunc.TotalTime))
            
            return retValue  
        return newFunc  

if __name__ == '__main__':
    print (FrequentlyUsedFunc.calcMidNumberByRange( -1,2,4 ))





