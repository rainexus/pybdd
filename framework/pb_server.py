#!/usr/bin/python
import os
import re
import pexpect
import time
import sys
import pb_exception

class PBServer:
    def __init__(self, testObj, hostname, username, password):        
        if username == 'root':
            SHELL_CHAR = '#' 
        else: SHELL_CHAR = '>'
        #print 'ssh ' + username + '@' + hostname
        ssh_sh = pexpect.spawn('ssh ' + username + '@' + hostname )
        index = ssh_sh.expect (['Password:','yes'])
        if index == 0:
            ssh_sh.sendline (password)
            time.sleep (0.1)
            ssh_sh.expect (SHELL_CHAR)
        elif index == 1:
            ssh_sh.sendline('yes')
            ssh_sh.expect ('Password')
            ssh_sh.sendline (password)
            time.sleep (0.1)
            ssh_sh.expect (SHELL_CHAR)
        
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh_sh = ssh_sh
        testObj.AddPBServer(self)
        
        sh = self.getSh()
        sh.sendline("mkdir -p /data/smart_test/pb_mnt_res")
        sh.sendline("mkdir -p /data/smart_test/pb_tmp_res")
        sh.sendline("chmod 777 /data")
        sh.sendline("chmod 777 /data/smart_test/")
        sh.sendline("chmod 777 /data/smart_test/pb_tmp_res")
        
    def __del__(self):
        if self.ssh_sh != None:
            self.ssh_sh.close()
            
    def getSh(self):
        return self.ssh_sh
    
    def ensureRootSh(self):
        if (self.username != None and self.username != "root"):
            raise pb_exception.PBException("Should use root!") 

    def ensureNotRootSh(self):
        if (self.username != None and self.username == "root"):
            raise pb_exception.PBException("Should not use root!")
        
    def check_pdCpRunning(self):
        return self.runCmdNoE("ps -A | grep -w pbcp_main")[0] == 0

    def check_pdUpRunning(self):
        return self.runCmdNoE("ps -A | grep -w pbup_main")[0] == 0
    
    def check_pdRunRpmInstalled(self, build):
        self.ensureRootSh()
        return self.runCmdNoE("rpm -qa | grep " + "pb_run-" + build)[0] == 0

    def check_pdEnaRpmInstalled(self, build):
        self.ensureRootSh()
        return self.runCmdNoE("rpm -qa | grep " + "pb_ena-" + build)[0] == 0
    
    def input_installPBRunRpmpackage(self, path):
        self.ensureRootSh()
        self.runCmd("rpm -i " + path)

    def input_installPBEnaRpmpackage(self, path):
        self.ensureRootSh()
        self.runCmd("rpm -i " + path)
        
    def input_uninstallPBRunRpmpackage(self, build):
        self.ensureRootSh()
        self.runCmd("rpm -e pb_run-" + build)
    
    def input_uninstallPBEnaRpmpackage(self, build):
        self.ensureRootSh()
        self.runCmd("rpm -e pb_ena-" + build)
    
    def input_startPBCp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmd("./pbcp_start.py")
        
    def input_stopPBCp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmd("./pbcp_stop.py")
        
    def input_statusPBCp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmdNoE("./pbcp_status.py")[0] != 0
        
    def input_startPBUp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmd("./pbup_start.py")
        
    def input_stopPBUp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmd("./pbup_stop.py")
        
    def input_statusPBUp(self):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmdNoE("./pbup_status.py")[0] != 0
    
    def input_runStagebstub(self, stageBInputBinFile):
        self.ensureNotRootSh()
        self.runCmd("cd /jdsu/opt/pb/bin/")
        return self.runCmd("LD_LIBRARY_PATH=../lib:$LD_LIBRARY_PATH ./stagebstub \
        -c /jdsu/etc/opt/pb/config/pb.xml -l /jdsu/etc/opt/pb/config/log4cxx_xupmain.xml -i \
        " + stageBInputBinFile)
    
    # setup helper
    def setup_copyFileFromResServer(self, srcPath, DstPath, timeout=60):
        self.ensureRootSh()
    
        absDstPath = "/data/smart_test/pb_tmp_res/" + DstPath
        absDstDir = os.path.dirname(absDstPath)
        if (absDstDir != ""):
            self.runCmd("mkdir -p " + absDstDir)
    
        self.runCmdNoE("umount /data/smart_test/pb_mnt_res")
        self.runCmd("mount sgpnas02.sin.ds.jdsu.net:/vol/traffic1/ /data/smart_test/pb_mnt_res")
        
        try:
            self.runCmd("cp -avr /data/smart_test/pb_mnt_res/" + srcPath + " /data/smart_test/pb_tmp_res/" + DstPath, timeout)
            self.runCmd("chmod 777 /data/smart_test/pb_tmp_res -R")
        finally:
            self.runCmd("umount /data/smart_test/pb_mnt_res")
    
    def setup_copyFileFromTestClient(self, localServer, srcPath, DstPath, timeout=60):
        self.ensureRootSh()
            
        if (localServer.runCmdNoE("[ -d /data/smart_test/pb_mnt_res ]")[0] != 0):
            localServer.runCmd("mkdir -p /data/smart_test/pb_mnt_res")
    
        absDstPath = "/data/smart_test/pb_tmp_res/" + DstPath
        absDstDir = os.path.dirname(absDstPath)
        if (absDstDir != ""):
            self.runCmd("mkdir -p " + absDstDir)
    
        self.runCmdNoE("umount /data/smart_test/pb_mnt_res")
        self.runCmd("mount sgpnas02.sin.ds.jdsu.net:/vol/traffic1/ /data/smart_test/pb_mnt_res")
        
        localServer.runCmdNoE("umount /data/smart_test/pb_mnt_res")
        localServer.runCmd("mount sgpnas02.sin.ds.jdsu.net:/vol/traffic1/ /data/smart_test/pb_mnt_res")
        
        try:
            if (self.runCmdNoE("[ -d /data/smart_test/pb_mnt_res/sart/MAA/smart_test/pb/pb_tmp_res ]")[0] != 0):
                self.runCmd("mkdir -p /data/smart_test/pb_mnt_res/sart/MAA/smart_test/pb/pb_tmp_res")
            localServer.runCmd("cp -r "+ srcPath + " /data/smart_test/pb_mnt_res/sart/MAA/smart_test/pb/pb_tmp_res/" + DstPath, timeout)
            self.runCmd("cp -r "+ " /data/smart_test/pb_mnt_res/sart/MAA/smart_test/pb/pb_tmp_res/" + DstPath + " /data/smart_test/pb_tmp_res/" + DstPath, timeout)
            self.runCmd("chmod 777 /data/smart_test/pb_tmp_res -R")
        finally:
            self.runCmd("umount /data/smart_test/pb_mnt_res")
            localServer.runCmd("rm -r -f /data/smart_test/pb_mnt_res/sart/MAA/smart_test/pb/pb_tmp_res/*")
            localServer.runCmd("umount /data/smart_test/pb_mnt_res")
    
    def setup_getAbsPath(self, rpath):
        self.ensureRootSh()
        return "/data/smart_test/pb_tmp_res/" + rpath
    
    # clear helpers
    def clear_finalClears(self):    
            try:
                self.runCmdNoE("rm -f -r /data/smart_test/pb_tmp_res/*", 120)
            except:
                pass
    
    def clear_forceClearPBRpm(self):
        pass
    
    # command functions
    def runCmd(self, cmd, timeout=60):
        print ("cmd: " + cmd)
        sh = self.getSh()
        sh.sendline("V6CHa5WEQokYdasIs54Var=54")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}BEGIN > /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline(cmd + " >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt 2>&1")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}RETURN$?RETURN >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}EOF >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline("cat /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.expect("V6CHa5WEQokYdasIs54EOF", timeout)
        before = sh.before
        m = re.search("(V6CHa5WEQokYdasIs54RETURN)(-?[0-9]*\.?[0-9]*)(RETURN)", before)
        output = before[before.find("V6CHa5WEQokYdasIs54BEGIN") + len("V6CHa5WEQokYdasIs54BEGIN") + 2 : before.find(m.group(0))]
        r = int(m.group(2))
        if (r != 0):
            print(output)
            raise pb_exception.PBException("runCmd fail: " + cmd)        
        return output
        
    def runCmdNoE(self, cmd, timeout=60):
        print ("cmd: " + cmd)
        sh = self.getSh()
        sh.sendline("V6CHa5WEQokYdasIs54Var=54")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}BEGIN > /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline(cmd + " >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt 2>&1")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}RETURN$?RETURN >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline("echo V6CHa5WEQokYdasIs${V6CHa5WEQokYdasIs54Var}EOF >> /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.sendline("cat /data/smart_test/pb_tmp_res/V6CHa5WEQokYdasIs54.txt")
        sh.expect("V6CHa5WEQokYdasIs54EOF", timeout)
        before = sh.before
        m = re.search("(V6CHa5WEQokYdasIs54RETURN)(-?[0-9]*\.?[0-9]*)(RETURN)", before)
        output = before[before.find("V6CHa5WEQokYdasIs54BEGIN") + len("V6CHa5WEQokYdasIs54BEGIN") + 2 : before.find(m.group(0))]
        r = int(m.group(2))
        return (r, output)