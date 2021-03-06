
from PyQt5 import QtCore,QtGui
from PyQt5.QtWidgets import QWidget



class EditorSettings(QtCore.QObject):
    startDisLineNumberChangedSignal = QtCore.pyqtSignal(int)
    startDisLetterXOffChangedSignal = QtCore.pyqtSignal(int)
    
    lineTextMaxPixelChangedSignal = QtCore.pyqtSignal(int)
    fontChangedSignal = QtCore.pyqtSignal(QtGui.QFont)
    editableChangedSignal = QtCore.pyqtSignal(bool)

    getFuncNames = ['getLineNumberRightXOff', \
                    'getLineTextLeftXOff', \
                    'getStartDisLineNumber', \
                    'getStartDisLetterXOff', \
                    'getFont', \
                    'getFontMetrics', \
                    'getLineTextMaxPixel', \
                    'isEditable', \
                    'getUserDataByKey']
    setFuncNames = ['setLineNumberRightXOff', \
                    'setLineTextLeftXOff', \
                    'setStartDisLineNumber', \
                    'setStartDisLetterXOff', \
                    'setLineTextMaxPixel', \
                    'setFont', \
                    'setEditable', \
                    'setUserDataByKey']
    clearFuncNames = ['clearUserData']
    signalNames = ['startDisLineNumberChangedSignal', \
                   'startDisLetterXOffChangedSignal', \
                   'lineTextMaxPixelChangedSignal', \
                   'fontChangedSignal', \
                   'editableChangedSignal']


    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        
        self.__startDisLineNumber = 0       # 当前将会从第 startDisLineNumber 行开始显示
        self.__startDisLetterXOff = 0       # 每行文本将会向左偏移 startDisLetterNumber 个像素
        self.__lineTextMaxPixels = 0        # 当前文本在绘制时，最大的像素数（横轴滚动条将会根据它设置的maxrange）        
        
        self.__editAble = True
        
        self.__font = QtGui.QFont('Consolas',11)
        self.__font.setBold(True)
        self.__fontMetrics = QtGui.QFontMetrics(self.__font)
        
        self.__userData = {}                # 用来记录程序使用中的暂存数据
    
    
    
    def clearUserData(self):
        self.__userData = {}

    
    

    def getStartDisLineNumber(self):
        return self.__startDisLineNumber
    def getStartDisLetterXOff(self):
        return self.__startDisLetterXOff
    def getLineTextMaxPixel(self):
        return self.__lineTextMaxPixels
    def getFont(self):
        return self.__font
    def getFontMetrics(self):
        return self.__fontMetrics
    def isEditable(self):
        return self.__editAble
    def getUserDataByKey(self,key,defaultValue = None):
        return self.__userData.get(key,defaultValue)




        
    def setStartDisLineNumber(self,newStartDisLineNumber,emitSignal = True):
        if self.__startDisLineNumber == newStartDisLineNumber:
            return 
        self.__startDisLineNumber = newStartDisLineNumber
        if emitSignal:
            self.startDisLineNumberChangedSignal.emit(newStartDisLineNumber)
        
    def setStartDisLetterXOff(self,newStartDisLetterXOff,emitSignal = True):
        if self.__startDisLetterXOff == newStartDisLetterXOff:
            return
        self.__startDisLetterXOff = newStartDisLetterXOff
        if emitSignal:
            self.startDisLetterXOffChangedSignal.emit(newStartDisLetterXOff)
        
    def setLineTextMaxPixel(self,newLineTextMaxPixel,emitSignal = True):
        if self.__lineTextMaxPixels == newLineTextMaxPixel:
            return 
        self.__lineTextMaxPixels = newLineTextMaxPixel
        if emitSignal:
            self.lineTextMaxPixelChangedSignal.emit(newLineTextMaxPixel)
        
    def setFont(self,newFontObj,emitSignal = True):
        if self.__font == newFontObj:
            return 
        self.__font = newFontObj
        self.__fontMetrics = QtGui.QFontMetrics(self.__font)
        if emitSignal:
            self.fontChangedSignal.emit(newFontObj)

    def setEditable(self,editAble,emitSignal = True):
        if self.__editAble == editAble:
            return 
        self.__editAble = editAble
        if emitSignal:
            self.editableChangedSignal.emit(editAble)
    
    def setUserDataByKey(self,key,value):
        self.__userData[key] = value
        
        
        
        
        
        





