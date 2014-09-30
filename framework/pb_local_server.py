import sys
import pexpect
import pb_server

class PBLocalServer(pb_server.PBServer):
    def __init__(self, testObj):
        self.local_sh = pexpect.spawn('bash')
        self.username = None
        testObj.AddPBLocalServer(self)
        
    def __del__(self):
        if self.local_sh != None:
            self.local_sh.close()
    
    def getSh(self):
        return self.local_sh
            
