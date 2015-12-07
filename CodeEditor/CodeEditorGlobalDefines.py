

from PyQt5 import QtGui, QtCore



class CEGlobalDefines():
    
    CharDistancePixel = 1       # 同一行相邻两个字符之间的像素间隔
    TextYOff = 4                # 编辑器文本距离上边的距离
    CursorWidth = 2             # 光标宽度

    

    
    LineNumberPen = QtGui.QPen( QtGui.QColor( 255,0,0 ) )       # 绘制行文本的QPen
    LineStrPen = QtGui.QPen( QtGui.QColor( 0,0,0 ) )            # 绘制行字符串的QPen

    LineSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 100,200,0,100 ),QtCore.Qt.SolidPattern )      # 绘制输入焦点所在行的行背景画刷
    LineUnSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 100,200,0,100 ),QtCore.Qt.NoBrush )
    
    TextSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 200,100,0,150 ),QtCore.Qt.SolidPattern )
    








class GlobalEventFilter(QtCore.QObject):
    def __init__(self,parent = None):
        QtCore.QObject.__init__(self,parent)
        self.__funcObjs__InputMethod = []
        self.__funcObjs__FocusIn = []
    def eventFilter(self, obj, event):
        funcObjArr = []        
        if event.type() == QtCore.QEvent.InputMethod:
            funcObjArr = self.__funcObjs__InputMethod
        elif event.type() == QtCore.QEvent.FocusIn:
            funcObjArr = self.__funcObjs__FocusIn
        
        for funcObjs in funcObjArr:
            funcObjs(event)

        return QtCore.QObject.eventFilter(self, obj, event)

    
    def regListener_InputMethod(self,funcObj):
        self.__funcObjs__InputMethod.append( funcObj )
    def regListener_FocusIn(self,funcObj):
        self.__funcObjs__FocusIn.append(funcObj)
    
    

