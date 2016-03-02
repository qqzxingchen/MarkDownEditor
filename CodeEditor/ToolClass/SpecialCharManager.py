



from PyQt5 import QtGui,QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget
from CodeEditor.MainClass.FrequentlyUsedFunc import FrequentlyUsedFunc as FUF

from CodeEditor.MainClass.CodeEditorGlobalDefines import GlobalClipBorard

class SpecialCharViewer(QWidget):
    
    @staticmethod
    def getUnicodeCharByUnicodeID(unicodeID):
        if unicodeID < 0 or unicodeID > 0xFFFF:
            return ''
        else:
            v = '%X' % unicodeID
            v = (4-len(v))*'0' + v
            return eval( "'\\u%s'" % v )
    
    startDisCodeChanged = QtCore.pyqtSignal(int)
    selectedCodeChanged = QtCore.pyqtSignal(int)
    
    getCharAreaLength = lambda : 28
    getLineCharNumber = lambda : 16
    getLineNumber = lambda : 10
    getOffX = lambda : 10
    getOffY = lambda : 10
    getXLabelAreaLength = lambda : 48
    getYLabelAreaLength = lambda : 24
    
    
    def __adjustSize(self):
        SCV = SpecialCharViewer
        
        self.__scrollBar.adjustSize()        
        w = SCV.getCharAreaLength() * SCV.getLineCharNumber() + 2 * SCV.getOffX() + SCV.getXLabelAreaLength()
        self.__scrollBar.setGeometry( w, SCV.getYLabelAreaLength() + SCV.getOffY(), \
                                      self.__scrollBar.width(), SCV.getCharAreaLength() * SCV.getLineNumber() )
        
        totalWidth = w + self.__scrollBar.width()
        totalHeight = SCV.getCharAreaLength() * SCV.getLineNumber() + 2 * SCV.getOffY() + SCV.getYLabelAreaLength()        
        self.setMinimumSize(totalWidth, totalHeight)
        self.setMaximumSize(totalWidth, totalHeight)
        
        
        
    
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
    
        self.__startDisCode = 0
        self.startDisCodeChanged.connect( lambda : self.update() )

        self.__selectedCode = None
        self.selectedCodeChanged.connect( self.__onSelectedCodeChanged )

        self.__scrollBar = QtWidgets.QScrollBar(self)
        self.__scrollBar.setRange( 0,0xFFF0 )
        self.__scrollBar.valueChanged.connect( self.setStartDisCode )
        self.startDisCodeChanged.connect( self.__scrollBar.setValue )

        self.__adjustSize()

        
    def getStartDisCode(self):
        return self.__startDisCode
    
    def setStartDisCode(self,newStartDisCode):
        code = FUF.calcMidNumberByRange(0, newStartDisCode, 0xFFFF)
        code = (code // 16) * 16
        if code != self.__startDisCode:
            self.__startDisCode = code
            self.startDisCodeChanged.emit(code)
    
    def getSelectedCode(self):
        return self.__selectedCode

    def setSelectedCode(self,code):
        code = FUF.calcMidNumberByRange(0, code, 0xFFFF)
        if code != self.__selectedCode:
            self.__selectedCode = code
            self.selectedCodeChanged.emit(code)

    
    def __onSelectedCodeChanged(self,curSelectedCode):
        SCV = SpecialCharViewer
        curDisCodeRange = ( self.getStartDisCode(),self.getStartDisCode() + SCV.getLineCharNumber()*SCV.getLineNumber()  )
        if curSelectedCode < curDisCodeRange[0]:
            self.setStartDisCode( (curSelectedCode // 16) * 16 )            
        elif curSelectedCode > curDisCodeRange[1]:
            self.setStartDisCode( (curSelectedCode // 16) * 16 )
        self.update()
        
    
    def wheelEvent(self, event):
        changedV = 3 if event.angleDelta().y() < 0 else -3
        self.setStartDisCode( self.getStartDisCode() + changedV*16 )
    
    def mousePressEvent(self, event):
        selectedCode = self.__getCharCodeByPos(event.x(), event.y())
        if selectedCode != None:
            self.setSelectedCode(selectedCode)
    
    # 在鼠标的左、右、中三个键没有按下的时候，如果没有进行特殊设置，则将不会出发该事件
    # 即只有在鼠标某键按下的情况下移动鼠标，才会出发该键
    def mouseMoveEvent(self, event):
        selectedCode = self.__getCharCodeByPos(event.x(), event.y())
        if selectedCode != None:
            self.setSelectedCode(selectedCode)
        
    def __getCharCodeByPos(self,posX,posY):
        SCV = SpecialCharViewer
        
        x = posX - (SCV.getXLabelAreaLength() + SCV.getOffX())
        y = posY - (SCV.getYLabelAreaLength() + SCV.getOffY())
        if x >= 0 and x <= SCV.getCharAreaLength() * SCV.getLineCharNumber() and \
            y >= 0 and y <= SCV.getCharAreaLength() * SCV.getLineNumber():
            code = self.getStartDisCode() + 16 * ( y // SCV.getCharAreaLength() ) + (x // SCV.getCharAreaLength())
            return code
        else:
            return None
        
        
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        painter.save()
        self.__drawColumnNumber(painter)
        painter.restore()
        
        painter.save()
        self.__drawRawText(painter)
        painter.restore()
        
        painter.save()
        self.__drawBorderLine(painter)
        painter.restore()
        
        painter.save()
        self.__drawUnicodeChar(painter)
        painter.restore()
        
        painter.save()
        self.__highlightSelectedArea(painter)
        painter.restore()

    
    def __drawColumnNumber(self,painter):
        font = painter.font()
        font.setBold(True)
        painter.setFont( font )
        
        SCV = SpecialCharViewer
        width = SCV.getCharAreaLength()
        # 绘制列号（ 0-F ）
        for j in range(SCV.getLineCharNumber()):
            x = SCV.getXLabelAreaLength() + SCV.getOffX() + j*width
            painter.drawText( x,0,width,SCV.getYLabelAreaLength(), QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter , '%X' % j)
    
    def __drawBorderLine(self,painter):
        painter.setPen( QtGui.QPen( QtGui.QColor(200,200,200) ) )
        painter.setBrush( QtGui.QBrush( QtGui.QColor(255,255,255) ) )
        
        SCV = SpecialCharViewer
        width = SCV.getCharAreaLength()
        height = SCV.getCharAreaLength()
        for i in range(SCV.getLineNumber()):
            y = SCV.getYLabelAreaLength() + SCV.getOffY() + i*height
            for j in range(SCV.getLineCharNumber()):
                x = SCV.getXLabelAreaLength() + SCV.getOffX() + j*width
                painter.drawRect( x,y,width,height )

    def __drawRawText(self,painter):
        font = painter.font()
        font.setBold(True)
        painter.setFont( font )
        
        SCV = SpecialCharViewer
        height = SCV.getCharAreaLength()
        for i in range(SCV.getLineNumber()):
            y = SCV.getYLabelAreaLength() + SCV.getOffY() + i*height
            
            code = self.getStartDisCode() + 16 * i
            if code < 0 or code > 0xFFF0:
                continue 
            
            codeText = '%X' % code
            codeText = '0x' + (4-len(codeText))*'0' + codeText
            painter.drawText( 0,y,SCV.getXLabelAreaLength(),height, \
                              QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter , codeText)

    def __drawUnicodeChar(self,painter):
        SCV = SpecialCharViewer
        width = SCV.getCharAreaLength()
        height = SCV.getCharAreaLength()
        for i in range(SCV.getLineNumber()):
            y = SCV.getYLabelAreaLength() + SCV.getOffY() + i*height            
            for j in range(SCV.getLineCharNumber()):
                x = SCV.getXLabelAreaLength() + SCV.getOffX() + j*width
                painter.drawText( x,y,width,height,QtCore.Qt.AlignCenter,SpecialCharViewer.getUnicodeCharByUnicodeID(self.getStartDisCode() + 16 * i + j) )
            
    def __highlightSelectedArea(self,painter):
        highlightArea = self.__calcHighlightArea()
        if highlightArea != None:
            painter.fillRect( highlightArea , QtGui.QBrush( QtGui.QColor( 200,100,0,64 ) ) )
                
    def __calcHighlightArea(self):
        SCV = SpecialCharViewer
        selectedCode = self.getSelectedCode()
        if selectedCode == None:
            return None
        
        if selectedCode >= self.getStartDisCode():
            relativeCode = selectedCode - self.getStartDisCode()
            x = (relativeCode % 16) * SCV.getCharAreaLength()
            y = (relativeCode // 16 ) * SCV.getCharAreaLength()
            return QtCore.QRect( SCV.getXLabelAreaLength() + SCV.getOffX() + x , \
                                 SCV.getYLabelAreaLength() + SCV.getOffY() + y , \
                                 SCV.getCharAreaLength(),SCV.getCharAreaLength() )            
        else:
            return None











class SpecialCharDetailInfoWidget(QWidget):
    disCharCodeChangedSignal = QtCore.pyqtSignal( int )
    disCharChangedSignal = QtCore.pyqtSignal( int )
    
    CONTROLWIDTH = 128
    
    
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.__initWidget()
        
        setattr(self.__disCharCodeLineEdit, 'setText', self.__disCharCodeLineEdit_setText)
        setattr(self.__disCharLineEdit, 'setText', self.__disCharLineEdit_setText)
        
        self.disCharCodeLineEdit = lambda : self.__disCharCodeLineEdit
        self.disCharLineEdit = lambda : self.__disCharLineEdit
    
    def __disCharCodeLineEdit_setText(self,text):
        if text != self.__disCharCodeLineEdit.text():
            QtWidgets.QLineEdit.setText( self.__disCharCodeLineEdit,text )
        
    def __disCharLineEdit_setText(self,text):
        if text != self.__disCharLineEdit.text():
            QtWidgets.QLineEdit.setText( self.__disCharLineEdit,text )
        
    
    
    def __initWidget(self):
        self.__disCharCodeLineEdit = QtWidgets.QLineEdit( self )
        self.__disCharLineEdit = QtWidgets.QLineEdit( self )
        
        self.__disCharCodeLineEdit.setAlignment( QtCore.Qt.AlignCenter )
        self.__disCharLineEdit.setAlignment( QtCore.Qt.AlignCenter )
        
        self.__disCharCodeLineEdit.setMaxLength(4)
        self.__disCharLineEdit.setMaxLength(1)
        
        # 使得中文输入法对它无效
        self.__disCharCodeLineEdit.setAttribute( QtCore.Qt.WA_InputMethodEnabled,False ) 
        self.__disCharCodeLineEdit.textChanged.connect( self.__onDisCodeControlTextChanged )
        self.__disCharLineEdit.textChanged.connect( self.__onDisCharControlTextChanged )
        
        length = SpecialCharDetailInfoWidget.CONTROLWIDTH
        self.__disCharCodeLineEdit.setMinimumWidth(length)
        self.__disCharCodeLineEdit.setMaximumWidth(length)
        self.__disCharLineEdit.setMinimumSize(length, length)
        self.__disCharLineEdit.setMaximumSize(length, length)

        font=QtGui.QFont('Consolas',length // 2)
        font.setBold(True)
        self.__disCharLineEdit.setFont( font )        

        self.__copyButton = QtWidgets.QPushButton('复制',self)
        self.__copyButton.clicked.connect( lambda : GlobalClipBorard().setData( self.__disCharLineEdit.text() ) )
        

        self.__charWidgetLayout = QtWidgets.QFormLayout( self )
        self.__charWidgetLayout.setContentsMargins(0,0,0,10)
        self.__charWidgetLayout.addRow( '代码（0x）' , self.__disCharCodeLineEdit )
        self.__charWidgetLayout.addRow( '字符' , self.__disCharLineEdit )
        self.__charWidgetLayout.addRow( '',self.__copyButton )
        
        self.adjustSize()
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())
        
    def __onDisCodeControlTextChanged(self,newText):
        validText = ''
        for c in newText:
            cAsciiValue = ord(c)
            if (cAsciiValue >= ord('0') and cAsciiValue <= ord('9')) or (cAsciiValue >= ord('A') and cAsciiValue <= ord('F')):
                validText += c
            elif cAsciiValue >= ord('a') and cAsciiValue <= ord('f'):
                validText += c.upper()
        self.__disCharCodeLineEdit.setText( validText )
        
        if len(validText) != 0:
            self.disCharCodeChangedSignal.emit( int(validText,16) )

    def __onDisCharControlTextChanged(self,newText):
        if len(newText) != 0:
            self.disCharChangedSignal.emit( ord(newText) )







    
    





class SpecialCharManager(QWidget):
    
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        
        self.__initWidget()

    
    def __onDetailCharChanged(self,code):
        self.__viewer.setSelectedCode(code)
        self.__detailViewer.disCharCodeLineEdit().setText( '%X' % code )
        self.__detailViewer.disCharLineEdit().setText( SpecialCharViewer.getUnicodeCharByUnicodeID( code ) )
        
    def __initWidget(self):
        SCV = SpecialCharViewer
        
        self.__viewer = SpecialCharViewer(self)
        self.__viewer.setGeometry( 0,0,self.__viewer.width(),self.__viewer.height() )

        self.__detailViewer = SpecialCharDetailInfoWidget(self)
        self.__detailViewer.setGeometry( SCV.getXLabelAreaLength() + SCV.getOffX(),self.__viewer.height(), \
                                         self.__detailViewer.width(),self.__detailViewer.height() )
        
        self.__viewer.selectedCodeChanged.connect( self.__onDetailCharChanged )
        self.__detailViewer.disCharChangedSignal.connect( self.__onDetailCharChanged )
        self.__detailViewer.disCharCodeChangedSignal.connect( self.__onDetailCharChanged )
        
        self.adjustSize()
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())
        
        
        



            

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    

    
    a = SpecialCharManager()
    a.show()

    sys.exit( app.exec_() )

    

            
            
            
            
            
            
            
            
            
            
            












