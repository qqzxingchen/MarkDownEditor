
import sys,os,codecs

from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication,QWidget,QSplitter,QHBoxLayout
from PyQt5.QtCore import QUrl

from Widgets.TextEditor import TextEditor
from GlobalTool.ResourceManager import ResourceManager




class TestWindow(QWidget):
    TMPDIR = "tmp"
    TMPHTMLFILE = os.path.join(TMPDIR,'tmptext.html')
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        
        if os.path.isdir(TestWindow.TMPDIR) == False:
            os.mkdir(TestWindow.TMPDIR)
        
        self.textEditor = TextEditor(self)
        self.webViewer = QWebView(self)
        self.setupUI()
        self.textEditor.textChangeSignal.connect(self.reloadText)
    
    def reloadText(self,dataDict):
        if self.webViewer.isVisible() == False:
            self.webViewer.show()
        with codecs.open( ResourceManager.getResourceAbsPath('template.html'),'r','utf-8' ) as templateFileObj:
            templateStr = templateFileObj.read()
        with open( TestWindow.TMPHTMLFILE,'wb' ) as tempFileObj:
            tempFileObj.write( (templateStr % dataDict[TextEditor.KEY_ORIGINALTXET]).encode('utf-8') )
        self.webViewer.load(QUrl( "file:///%s" % os.path.abspath( TestWindow.TMPHTMLFILE ) ))


    def setupUI(self):
        self.webViewer.hide()
        
        layout = QHBoxLayout(self)
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.textEditor)
        self.splitter.addWidget(self.webViewer)
        layout.addWidget(self.splitter)

        self.textEditor.resize(400,600)
        self.webViewer.resize(400,600)
        self.resize(800,600)
        
        self.splitter.setStyleSheet("background-color:green;")
        self.textEditor.setStyleSheet("background-color:white;border:none;")
        self.webViewer.setStyleSheet("background-color:white;")
        


        
    

if __name__ == "__main__":
    ResourceManager.ResourceDir = 'resources'
    
    app = QApplication(sys.argv)
    
    widget = TestWindow()
    widget.show()

    sys.exit(app.exec_())
    
    