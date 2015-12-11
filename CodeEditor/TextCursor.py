
from PyQt5 import QtCore, QtWidgets 


class TextCursor(QtWidgets.QLabel):
    
    # 当光标的显隐需要更改时
    cursorVisibleChangedSignal = QtCore.pyqtSignal()
    
    # 当光标的位置被改变时，需要发射该信号，以擦除原来的光标和因光标而高亮的行
    cursorPosChangedSignal = QtCore.pyqtSignal()
    
    
    SHOW_HIDE_INTERVAL = 500
    SHOW_CURSOR = 0
    HIDE_CURSOE = 1
    
    
    def isNeedShowCursor(self):
        if self.__forceHide == True:
            return False
        return self.__curState == TextCursor.SHOW_CURSOR

    
    # 也就是说，必须在这个位置的基础上减掉因滚动条而产生的增量才能得到滚动条需要绘制到界面上的位置
    # self.__*IndexPos(tuple)指代光标的当前字符位置，是与TextDocument相关的
    def initPos(self,xyIndexTuple):
        self.__oldIndexPos = xyIndexTuple
        self.__curIndexPos = xyIndexTuple
    
    def setGlobalCursorPos(self,xyIndexTuple):        
        self.__timer.stop()

        # 隐藏旧的光标
        self.__curState = TextCursor.HIDE_CURSOE
        self.cursorVisibleChangedSignal.emit()

        # 显示新的光标
        self.__oldIndexPos = self.__curIndexPos
        self.__curIndexPos = xyIndexTuple
        self.__curState = TextCursor.SHOW_CURSOR        
        self.cursorVisibleChangedSignal.emit()

        self.__timer.start()
        
        # 通知光标位置已经更新
        self.cursorPosChangedSignal.emit()

    def getCursorIndexPos(self,isCurrent = True):
        return self.__curIndexPos if isCurrent == True else self.__oldIndexPos

    def setForceHide(self,forceHide = True):
        self.__forceHide = forceHide
        self.__refreshDisState()
    
    def isForceHide(self):
        return self.__forceHide


    def __init__(self, parent = None):
        QtWidgets.QLabel.__init__(self,parent)
        self.setAttribute( QtCore.Qt.WA_InputMethodEnabled,True ) 
        self.setStyleSheet( "background-color:red;" )
        
        self.__curState = TextCursor.SHOW_CURSOR
        self.__oldIndexPos = None
        self.__curIndexPos = None
        self.__forceHide = False
        self.cursorVisibleChangedSignal.connect( self.__refreshDisState )
                
        self.__timer = QtCore.QTimer()
        self.__timer.setSingleShot(False)
        self.__timer.setInterval(TextCursor.SHOW_HIDE_INTERVAL)
        self.__timer.timeout.connect(self.__onTimeout)
        self.__timer.start()
        

    
    def __onTimeout(self):
        self.__curState = 1 - self.__curState
        self.cursorVisibleChangedSignal.emit()

    def __refreshDisState(self):
        self.setVisible( True if self.isNeedShowCursor() else False )



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    t = TextCursor()
    t.cursorVisibleChangedSignal.connect(lambda : print(1))
    
   
    
    sys.exit( app.exec_() )
    
    
    
            

        