

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
    OPERATETYPE_CHANGETEXT = 'changeText'
    OPERATETYPE_DELLINE = 'delLine'
    OPERATETYPE_ADDLINE = 'addLine'
    OPERATETYPES = [OPERATETYPE_CHANGETEXT,OPERATETYPE_DELLINE,OPERATETYPE_ADDLINE]
    
    changeText =    lambda lineIndex,text   : OperateRecord( OperateRecord.OPERATETYPE_CHANGETEXT,lineIndex,text )
    delLine =       lambda lineIndex        : OperateRecord( OperateRecord.OPERATETYPE_DELLINE,lineIndex )
    addLine =       lambda lineIndex,text   : OperateRecord( OperateRecord.OPERATETYPE_ADDLINE,lineIndex,text )
    
    # recordType指代了执行
    def __init__(self,recordType,lineIndex,text = None):
        self.recordType = recordType
        self.lineIndex = lineIndex
        self.text = text
        
        



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
        self.__operates.append( operate )
        if len(self.__operates) > OperateCache.__CACHE_MAX_LENGTH:
            self.__operates.remove( self.__operates[0] )
    def popOperates(self):
        if len(self.__operates) == 0:
            return None
        lastOperate = self.__operates[-1]
        self.__operates.remove(lastOperate)
        return lastOperate

if __name__ == '__main__':
    
    oc = OperateCache()
    oc.startRecord()
    oc.addRecord(1)
    oc.addRecord(2)
    oc.addRecord(3)
    oc.endRecord()
    oc.addRecords(1,2,3,4,5)
    
    print (oc._OperateCache__operates)
    
    
    
    
    
    
    
    
    


