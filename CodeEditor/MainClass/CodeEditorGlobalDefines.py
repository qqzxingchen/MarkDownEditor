

from PyQt5 import QtGui, QtCore, QtWidgets


# 负责剪切板管理
class GlobalClipBorard(object):
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance = super(GlobalClipBorard,cls).__new__(cls,*args,**kwargs)
        return cls._instance

    getData = lambda self : QtWidgets.QApplication.clipboard().text()
    setData = lambda self,data : QtWidgets.QApplication.clipboard().setText( data )        



class CodeEditorGlobalDefines:
    
    
    CharDistancePixel = 1       # 同一行相邻两个字符之间的像素间隔
    TextYOff = 4                # 编辑器文本距离上边的距离
    CursorWidth = 2             # 光标宽度

    spaceToInsertTOL = 4        # 当选中文本的情况下，按下tab键时，被选中文本的各行都需要在行首插入spaceToInsertTOL个空白字符
    
    
    # 通用画笔
    
    
    # 特定画笔    
    LineNumberPen = QtGui.QPen( QtGui.QColor( 255,0,0 ) )       # 绘制行文本的QPen
    LineTextPen = QtGui.QPen( QtGui.QColor( 0,0,0 ) )           # 绘制行字符串的QPen

    TextTokenPen = QtGui.QPen( QtGui.QColor( 0,0,255 ) )        # 关键字高亮时用的绘制画笔    
    ExplainNotePen = QtGui.QPen( QtGui.QColor( 192,192,192 ) )  # 注释文本使用的画笔
    StrTextPen = QtGui.QPen( QtGui.QColor( 0,170,0 ) )          # 单引号、双引号、三引号内部文本使用的画笔
    

    # 通用画刷
    WhiteOpaqueBrush = QtGui.QBrush( QtGui.QColor( 255,255,255,255 ),QtCore.Qt.SolidPattern )       # 白色不透明画刷
    
    
    # 特定画刷
    LineSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 64,144,240,32 ),QtCore.Qt.SolidPattern )      # 绘制输入焦点所在行的行背景画刷
    LineUnSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 0,0,0,100 ),QtCore.Qt.NoBrush )
    
    TextSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 200,100,0,64 ),QtCore.Qt.SolidPattern )      # 选中文本高亮时用的背景画刷
    TextAutoSelectedBKBrush = QtGui.QBrush( QtGui.QColor( 255,255,150,160 ),QtCore.Qt.SolidPattern )  # 与选中单词相同的单词高亮时用的背景画刷
    

    
    

