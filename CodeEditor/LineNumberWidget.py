

from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QWidget

from CodeEditor.CodeEditorGlobalDefines import CodeEditorGlobalDefines as CEGD
from CodeEditor.ToolClass.EditorSettings import EditorSettings



class LineNumberWidget(QWidget):
    
    def setVisibleLineYOffInfoArray(self,visibleLineYOffInfoArray):
        if self.visibleLineYOffInfoArray != visibleLineYOffInfoArray:
            self.visibleLineYOffInfoArray = visibleLineYOffInfoArray
            self.update()
    
    
    def __init__(self,editorSettingObj,parent):
        QWidget.__init__(self,parent)
        self.getSettings = lambda : editorSettingObj
        self.__initData()
                
        self.visibleLineYOffInfoArray = None
        
    def __initData(self):
        for funcName in EditorSettings.getFuncNames:
            setattr(self, funcName, getattr(self.getSettings(), funcName) )
            
        self.getSettings().lineTextLeftXOffChangedSignal.connect( self.__onLeftXOffChanged )
        self.getSettings().lineNumberRightXOffChangedSignal.connect(lambda v: self.update())
        self.getSettings().fontChangedSignal.connect(lambda v: self.update())
        self.getSettings().startDisLineNumberChangedSignal.connect(lambda v: self.update())
        
    def __onLeftXOffChanged(self,newLeftXOff):
        self.resize( newLeftXOff,self.height() )
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setFont(self.getFont())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(CEGD.WhiteOpaqueBrush)
        #painter.drawRect(0,0,self.width(),self.height())

        painter.save()
        self.__drawLineNumber(painter)
        painter.restore()


    # 绘制行号
    def __drawLineNumber(self,painter):
        if self.visibleLineYOffInfoArray == None:
            return
        
        painter.setPen(CEGD.LineNumberPen)   
        for item in self.visibleLineYOffInfoArray:
            curY = item['lineYOff']
            index = item['lineIndex']
            lineNumberRect = painter.boundingRect( 0,curY,0,0,0,str(index+1) )
            lineNumberRect.moveRight( self.getLineNumberRightXOff() - lineNumberRect.x() )
            # painter.drawText( lineNumberRect,0,str(index+1) )
            painter.drawText( lineNumberRect,0,str(index+1) )
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            