



class RetuInfo:
    SuccessSign = 'isSuccess'
    
    @staticmethod
    def info(**args):
        retuObj = {}
        for key in args:
            retuObj[key] = args[key]
        return retuObj

    @staticmethod
    def success(**args):
        retuObj = RetuInfo.info(**args)
        retuObj[RetuInfo.SuccessSign] = True
        return retuObj
        
    @staticmethod
    def error(**args):
        retuObj = RetuInfo.info(**args)
        retuObj[RetuInfo.SuccessSign] = False
        return retuObj


if __name__ == '__main__':
    print ( RetuInfo.info(a=1,b=2)['isSuccess']() )
    print ( RetuInfo.success(c=3,d=4)['isSuccess']()  )
    print ( RetuInfo.error(c=5,d=6)['isSuccess']()  )
    




