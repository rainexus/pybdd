#!/usr/bin/python
import traceback
import sys
import pb_exception

class PBTestTemplate:
    def __init__(self, taskInfo):
        self.taskInfo = taskInfo
        self.pdServers = dict()
        self.pdLocalServer = None

    def AddPBServer(self, pdServer):
        if (pdServer.username == "root"):
            self.pdServers[pdServer.hostname] = pdServer
    
    def AddPBLocalServer(self, pdLocalServer):
        self.pdLocalServer = pdLocalServer
    
    def getTaskInfoStr(self):
        build = None
        for prop in self.taskInfo["TestProperties"]:
            if (prop["Name"] == "Software.build"):
                build = prop["Value"]
                break
        if build == None:
                raise pb_exception.PBException("Can not find build number in Property")
                
        return "TestCaseId=" + str(self.taskInfo["TestCaseId"]) + \
        ", ScriptPath=" + self.taskInfo["ScriptPath"]  + ", build=" + build

    def setup(self):
        raise NotImplementedError("setup")

    def execute(self):
        raise NotImplementedError("execute")
    
    def verify(self):
        raise NotImplementedError("verify")
    
    def clear(self):
        raise NotImplementedError("clear")
    
    def doTest(self):
        result = (False, "")
        testInfo = "Can't get testInfo"
        try:
            testInfo = self.getTaskInfoStr();
            print("testInfo " + testInfo)
            
            print("**** setup ********")
            self.setup()
            print("setup successfully")
            
            print("\n**** execute ********")
            self.execute()
            print("execute successfully")
            
            print("\n**** verify ********")
            self.verify()
            print("verify successfully")
            
            result = (True, testInfo)
        except:
            result = (False, testInfo + "\n" + traceback.format_exc(4))
        
        try:
            print("\n**** clear ********")
            self.clear()
        except:
            result = (False, result[1] + "\n" + traceback.format_exc(4))
        
        print("\n**** final clear ********")
        if (self.pdLocalServer != None):
            self.pdLocalServer.clear_finalClears()   
        for hostName, server in self.pdServers.items():
            server.clear_finalClears()
        
        if (result[0] == True):
            print("clear successfully")
        
        print("\n**** result ********")
        if (result[0] == True):
            print("pass, " + result[1])
        else:
            print("fail, " + result[1])
        return result