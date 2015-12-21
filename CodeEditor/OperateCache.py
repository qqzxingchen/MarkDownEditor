
from CodeEditor.RetuInfo import RetuInfo

# 该类是为了记录用户进行的操作， 并用于回滚操作（Ctrl+Z）
# 其分为两个阶段：记录阶段 和 回滚阶段
# 记录阶段：
#     startRecord    开启记录
#     addRecord      原子操作
#     endRecord      结束记录，并将stardRecord和endRecord中间所做的记录保存成一次操作
#                    因为用户的一个操作，可能导致多行多处发生修改，因此将操作和记录分为不同的级别：
#                           一次operate由多条record组成，每条record中记录了一处修改
#     addRecords     可以比较方便地添加一系列record（无需startRecord、endRecord）
# 回滚阶段：
#     pushOperates
#     popOperates

# 数据结构：
#     self.__operates是一个list，最大长度为__CACHE_MAX_LENGTH。它的每个成员也都是一个list
#     self.__operates[index]是第index次操作时的record列表



class OperateRecord:
    OPERATETYPE_INSERTTEXT = 'insertText'
    OPERATETYPE_DELETETEXT = 'deleteText'
    OPERATETYPES = [OPERATETYPE_INSERTTEXT, \
                    OPERATETYPE_DELETETEXT]
    
    insertText = lambda indexPos,text   : OperateRecord(OperateRecord.OPERATETYPE_INSERTTEXT,indexPos = indexPos,text = text)
    deleteText = lambda indexPos,length : OperateRecord(OperateRecord.OPERATETYPE_DELETETEXT,indexPos = indexPos,length = length)

    # 判断record是否可以进行合并。可以合并需要满足以下条件：
    #     recordType相同
    #     indexPos[1]相同
    #     操作连续（如insert(2,5) text:123和insert(5,5) text:123就可以进行合并，合并为：insert(2,5) text:123123）
    @staticmethod
    def isRecordCanCombine(firstRecord,secondRecord):
        if firstRecord.recordType != secondRecord.recordType:
            return False
        if firstRecord.indexPos[1] != secondRecord.indexPos[1]:
            return False
        xPos1 = firstRecord.indexPos[0]
        xPos2 = secondRecord.indexPos[0]
        if firstRecord.recordType == OperateRecord.OPERATETYPE_INSERTTEXT:
            return ( xPos1 == xPos2 ) or ( xPos1 + len(firstRecord.text) == xPos2 )
        else:
            return ( xPos1 == xPos2 + secondRecord.length)



    @staticmethod
    def combineRecords(firstRecord,secondRecord):
        if OperateRecord.isRecordCanCombine(firstRecord, secondRecord) == False:
            return RetuInfo.error()
        else:
            if firstRecord.recordType == OperateRecord.OPERATETYPE_INSERTTEXT:
                if firstRecord.indexPos[0] == secondRecord.indexPos[0]:
                    return RetuInfo.success( combinedRecord = OperateRecord.insertText( firstRecord.indexPos,secondRecord.text + firstRecord.text )  )
                else:
                    return RetuInfo.success( combinedRecord = OperateRecord.insertText( firstRecord.indexPos,firstRecord.text + secondRecord.text ) )
            else:
                return RetuInfo.success( combinedRecord = OperateRecord.deleteText( secondRecord.indexPos,firstRecord.length + secondRecord.length ) )
        
        
    
    # recordType指代了执行
    def __init__(self,recordType,**otherArgs):
        self.recordType = recordType
        for key in otherArgs:
            setattr(self, key, otherArgs.get(key))
    
    
    
        
    # 只是用来展示数据
    def showRecord(self):
        if self.recordType == OperateRecord.OPERATETYPE_INSERTTEXT:
            return 'insert(indexPos:%s) text:%s' % (self.indexPos,self.text)
        else:
            return 'delete(indexPos:%s) length:%s' % (self.indexPos,self.length)



class OperateCache:
    
    __CACHE_MAX_LENGTH = 100
    funcNames = [ 'clearRecord','startRecord','endRecord','addRecord','addRecords',
                    'clearOperates','pushOperates','popOperates' ]
    
    def __init__(self):
        self.__operates = []
        
        self.__recordStart = False
        self.__curRecordList = []

    def clearRecord(self):
        self.__curRecordList = []
    def startRecord(self):
        self.__recordStart = True
        self.__curRecordList = []
    def endRecord(self):
        if len(self.__curRecordList) != 0:
            self.pushOperates( self.__curRecordList )
            self.__curRecordList = []
        self.__recordStart = False    
    def addRecord(self,operate):
        self.__curRecordList.append(operate)
    
    def addRecords(self,*operates):
        self.pushOperates( list( operates ) )
    

    def clearOperates(self):
        self.__operates.clear()
    def pushOperates(self,operate):
        self.__appendOperates(operate)
        if len(self.__operates) > OperateCache.__CACHE_MAX_LENGTH:
            self.__operates.remove( self.__operates[0] )
    def popOperates(self):
        if len(self.__operates) == 0:
            return None
        lastOperate = self.__operates[-1]
        self.__operates.remove(lastOperate)
        return lastOperate

    def __appendOperates(self,operate):
        if len(operate) == 0:
            return
        
        index = len(operate)-1
        while index >= 1:
            retuDict = OperateRecord.combineRecords(operate[index], operate[index-1])
            if retuDict[RetuInfo.SuccessSign]:
                operate.remove(operate[index])
                operate.remove(operate[index-1])
                operate.isnert( index-1,retuDict['combinedRecord'] )
            index -= 1
        
        if len(self.__operates) == 0:
            self.__operates.append( operate )
        else:
            lastOperate = self.__operates[-1]
            retuDict = OperateRecord.combineRecords( operate[0],lastOperate[-1] )
            if retuDict[RetuInfo.SuccessSign]:
                lastOperate.remove( lastOperate[-1] )
                lastOperate.append( retuDict['combinedRecord'] )
            else:
                self.__operates.append( operate )
        


        
        






if __name__ == '__main__':
    
    oc = OperateCache()
    oc.startRecord()
    oc.addRecord(1)
    oc.addRecord(2)
    oc.addRecord(3)
    oc.endRecord()
    oc.addRecords(1,2,3,4,5)
    
    print (oc._OperateCache__operates)
    
    
    
    
    
    
    
    
    


