
import os
from PyQt5 import uic


class UIFileCompiler:
    def __init__(self):
        self.__dataInfo = []

    def addFileToCompile(self,uiFileName,pyFileName = None):
        if os.path.isfile( uiFileName ) == False:
            return False
        uiFileName = os.path.abspath( uiFileName )
        if pyFileName == None:
            fileDir,fileName = os.path.split(uiFileName)            
            piFileName = os.path.join( fileDir,'UI_%s.py' % os.path.splitext(fileName)[0] )
        else:
            piFileName = os.path.abspath( piFileName )
        
        self.__dataInfo.append( (uiFileName,piFileName) )
        return True

    def compile(self):
        print ('start compile')
        for item in self.__dataInfo:
            try:
                with open( item[1],'w' ) as f:
                    uic.compileUi(item[0], f , True)
                print ( item,'compile success' )
            except Exception as reason:
                print ( item,'compile failed : %s' % str(reason) )
        print ('end compile')
        
if __name__ == '__main__':
    uiCompiler = UIFileCompiler()
    uiCompiler.addFileToCompile( 'SearchDialog.ui' )
    uiCompiler.compile()









