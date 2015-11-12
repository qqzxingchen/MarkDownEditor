

import os

class ResourceManager:
    ResourceDir = None
    
    @staticmethod
    def getResourceAbsPath(*args):
        if ResourceManager.ResourceDir == None:
            return None
        path = ResourceManager.ResourceDir
        for a in args:
            path = os.path.join(path,a)
        if os.path.isfile(path):
            return os.path.abspath(path)
        else:
            return None

if __name__ == '__main__':
    ResourceManager.ResourceDir = '../resources'
    print ( ResourceManager.getResourceAbsPath( 'template.html' ) )



