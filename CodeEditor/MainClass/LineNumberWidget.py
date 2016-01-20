

from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QWidget

from CodeEditor.MainClass.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD



class LineNumberWidget(QWidget):
    
    def setVisibleLineYOffInfoArray(self,visibleLineYOffInfoArray):
        if self.__visibleLineYOffInfoArray != visibleLineYOffInfoArray:
            self.__visibleLineYOffInfoArray = visibleLineYOffInfoArray
            self.update()
    
    # 行号的文本将会右对齐于该函数的返回值
    def getLineNumberRightXOff(self):
        return self.width()-8

    def __init__(self,editorSettingObj,parent):
        QWidget.__init__(self,parent)
        self.setMinimumWidth(24)
        self.setMaximumWidth(64)
        self.settings = lambda : editorSettingObj
        
        self.__forceUpdate = lambda *arg1,**arg2:self.update()
        self.settings().fontChangedSignal.connect( self.__forceUpdate )
        self.settings().startDisLineNumberChangedSignal.connect( self.__forceUpdate )
                
        self.__visibleLineYOffInfoArray = None
        
        
    def mouseDoubleClickEvent(self, event):
        print (event.x(),event.y())
        
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setFont(self.settings().getFont())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(CEGD.WhiteOpaqueBrush)
        #painter.drawRect(0,0,self.width(),self.height())

        painter.save()
        self.__drawLineNumber(painter)
        painter.restore()

    # 绘制行号
    def __drawLineNumber(self,painter):
        if self.__visibleLineYOffInfoArray == None:
            return
        
        painter.setPen(CEGD.LineNumberPen)   
        for item in self.__visibleLineYOffInfoArray:
            curY = item['lineYOff']
            index = item['lineIndex']
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(index+1) )
            lineNumberRect.moveRight( self.getLineNumberRightXOff() - lineNumberRect.x() )
            painter.drawText( lineNumberRect,0,str(index+1) )
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            