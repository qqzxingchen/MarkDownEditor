
from PyQt5 import QtCore
from cmath import rect


class TextCursor(QtCore.QObject):
    
    # 当光标的显隐需要更改时
    cursorVisibleChangedSignal = QtCore.pyqtSignal()
    
    # 当光标的位置被改变时，需要发射该信号，以擦除原来的光标和因光标而高亮的行
    cursorPosChangedSignal = QtCore.pyqtSignal()
    
    
    SHOW_HIDE_INTERVAL = 500
    SHOW_CURSOR = 0
    HIDE_CURSOE = 1
    
    
    def isNeedShowCursor(self):
        return self.__curState == TextCursor.SHOW_CURSOR

    # self.__*Rect(QRect)指代鼠标的当前像素位置，但是它是滚动条无关的
    # 也就是说，必须在这个位置的基础上减掉因滚动条而产生的增量才能得到滚动条需要绘制到界面上的位置
    # 
    def initPos(self,rect,xyIndexTuple):
        self.__oldRect = rect
        self.__curRect = rect

        self.__oldIndexPos = xyIndexTuple
        self.__curIndexPos = xyIndexTuple
    
    def setGlobalCursorPos(self,rect,xyIndexTuple):
        self.__timer.stop()

        # 隐藏旧的光标
        self.__curState = TextCursor.HIDE_CURSOE
        self.cursorVisibleChangedSignal.emit()

        # 显示新的光标
        self.__oldRect = self.__curRect
        self.__curRect = rect
        self.__oldIndexPos = self.__curIndexPos
        self.__curIndexPos = xyIndexTuple
        self.__curState = TextCursor.SHOW_CURSOR        
        self.cursorVisibleChangedSignal.emit()

        self.__timer.start()
        
        # 通知光标位置已经更新
        self.cursorPosChangedSignal.emit()

    def getCursorRect(self,isCurrent = True):
        return self.__curRect if isCurrent == True else self.__oldRect
    def getCursorIndexPos(self,isCurrent = True):
        return self.__curIndexPos if isCurrent == True else self.__oldIndexPos

        
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self,parent)
        self.__curState = TextCursor.SHOW_CURSOR
        self.__timer = QtCore.QTimer()
        self.__timer.setSingleShot(False)
        self.__timer.setInterval(TextCursor.SHOW_HIDE_INTERVAL)
        self.__timer.timeout.connect(self.__onTimeout)
        self.__timer.start()
    
    def __onTimeout(self):
        self.__curState = 1 - self.__curState
        self.cursorVisibleChangedSignal.emit()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    t = TextCursor()
    t.cursorVisibleChangedSignal.connect(lambda : print(1))
    
   
    
    sys.exit( app.exec_() )
    
    
    
            

        