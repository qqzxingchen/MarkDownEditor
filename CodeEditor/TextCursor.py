
from PyQt5 import QtCore


class TextCursor(QtCore.QObject):
    cursorVisibleChangedSignal = QtCore.pyqtSignal()
    
    SHOW_HIDE_INTERVAL = 500
    
    SHOW_CURSOR = 0
    HIDE_CURSOE = 1
    
    
    def isNeedShowCursor(self):
        return self.__curState == TextCursor.SHOW_CURSOR

    
    def initPos(self,rect):
        self.__oldPos = rect
        self.__newPos = rect
    def setPos(self,rect):
        self.__oldPos = self.__newPos
        self.__newPos = rect
    def getNewPos(self):
        return self.__newPos
    def getOldPos(self):
        return self.__oldPos

    
    def reset(self):
        self.__timer.stop()
        self.__curState = TextCursor.SHOW_CURSOR
        self.__timer.start()
        
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
    
    
    
            

        