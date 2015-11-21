
import time

from PyQt5 import QtGui, QtCore


class CEGlobalDefines():
    
    CharDistancePixel = 1       # 同一行相邻两个字符之间的像素间隔
    
    TextYOff = 4                # 编辑器文本距离上边的距离
    
    CursorWidth = 2             # 光标宽度
    
    LineNumberPen = QtGui.QPen( QtGui.QColor( 255,0,0 ) )       # 绘制行文本的QPen
    LineStrPen = QtGui.QPen( QtGui.QColor( 0,0,0 ) )            # 绘制行字符串的QPen

    LineSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 100,200,0,100 ),QtCore.Qt.SolidPattern )      # 绘制输入焦点所在行的行背景画刷
    LineUnSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 100,200,0,100 ),QtCore.Qt.NoBrush )         # 绘制输入焦点所在行的行背景画刷

    



# 打印函数执行的时间
# --exeTime  
def funcExeTime(func):
    def newFunc(*args, **args2):  
        t0 = time.time()  
        retValue = func(*args, **args2)
        print ("%.4fs taken for {%s}" % (time.time() - t0, func.__name__))
        return retValue  
    return newFunc  


