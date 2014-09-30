#!/usr/bin/python
import os
import sys
import pb_exception

def pdTestcaseGen():
    cwd = os.getcwd()
    (parrentPath, folder_name) = os.path.split(cwd)
    testcaseName = folder_name
    
    if (os.path.exists("./description.txt") == False):
        print("description.txt does not exist!")
        return False
    
    f = open("./description.txt", "r")
    description = f.read()
    f.close()
    
    os.system("touch __init__.py")
    f = open("./pd_test.py", "w")
    f.write(pdTestcaseGenCodes(description))
    f.close()
    os.system("chmod +x ./pd_test.py")

class Tabs:
    def __init__(self):
        self.nTabs = 0

    def clear(self):
        self.nTabs = 0

    def addTab(self):
        self.nTabs += 1
    
    def delTab(self):
        self.nTabs -= 1
        if (self.nTabs < 0):
            raise pb_exception.PBException("self.nTabs < 0")
        
    def getStr(self):
        ts = ""
        for i in range(self.nTabs):
            ts += "    "
        return ts;

class Block:
    def __init__(self):
        self.comments = []
        self.codeLine = None
    def getCodeStr(self):
        return self.codeLine[1 : ].strip().replace(" ", "_").replace("'s", "").replace("'", "").replace(",", "").replace(".", "_")

def pdTestcaseGenCodes(description):
    secotions = pdTestcaseSections(description)
    
    tabs = Tabs()
    codes = tabs.getStr() + "#!/usr/bin/python\n"
    codes += tabs.getStr() + "import traceback\n"
    codes += tabs.getStr() + "import sys\n"
    codes += tabs.getStr() + "import pb_test_template\n"
    codes += tabs.getStr() + "import pb_exception\n"
    codes += tabs.getStr() + "import pb_common_funcs\n"
    codes += tabs.getStr() + "import pb_server\n"
    codes += "\n"
    
    codes += tabs.getStr() + "def smartTest(taskInfo):\n"
    tabs.addTab()
    codes += tabs.getStr() + "test = PBSmartTest(taskInfo)\n"
    for block in secotions["header"]:
        for comment in block.comments:
            codes += tabs.getStr() + "print(\"## " + comment.strip() + " ##\")\n"
    codes += tabs.getStr() + "print(\"\")\n"
    codes += tabs.getStr() + "return test.doTest()\n"
    tabs.delTab()
    codes += "\n"

    tabs.clear()
    for block in secotions["header"]:
        for comment in block.comments:
            codes += tabs.getStr() + "# " + comment.strip() + "\n"
    codes += tabs.getStr() + "class PBSmartTest(pb_test_template.PBTestTemplate):\n"
    for k in ["setup", "execute", "verify", "clear"]:    
        tabs.clear()
        tabs.addTab()
        codes += tabs.getStr() + "def " + k + "(self):\n"
        tabs.addTab()
        
        if (k == "clear"):
            codes += tabs.getStr() + "info = \"\"\n"
        
        for block in secotions[k]:
            if (block.codeLine != None):
                if (k == "clear"):
                    codes += tabs.getStr() + "try:\n"
                    tabs.addTab()
                    codes += tabs.getStr() + "print(\"*" + block.codeLine + " **\")\n"
                    for comment in block.comments:
                        codes += tabs.getStr() + "print(\"## " + comment.strip() + " ##\")\n"
                    codes += tabs.getStr() + "self." + block.getCodeStr() + "()\n"
                    codes += tabs.getStr() + "print(\"\")\n"
                    tabs.delTab()
                    codes += tabs.getStr() + "except:\n"
                    tabs.addTab()
                    codes += tabs.getStr() + "info += traceback.format_exc(4)\n"
                    tabs.delTab()
                else:
                    codes += tabs.getStr() + "print(\"*" + block.codeLine + " **\")\n"
                    for comment in block.comments:
                        codes += tabs.getStr() + "print(\"## " + comment.strip() + " ##\")\n"
                    codes += tabs.getStr() + "self." + block.getCodeStr() + "()\n"
                    codes += tabs.getStr() + "print(\"\")\n"
        
        if (k == "clear"):
            codes += tabs.getStr() + "if (info != \"\"):\n"
            tabs.addTab()
            codes += tabs.getStr() + "raise pb_exception.PBException(\"clear fail\" + info)\n"
            tabs.delTab()
        codes += "\n"
    
    for k in ["setup", "execute", "verify", "clear"]:
        tabs.clear()
        tabs.addTab()
        codes += tabs.getStr() + "# all " + k + " sub-fucntions\n"
        for block in secotions[k]:
            if (block.codeLine != None):
                for comment in block.comments:
                    codes += tabs.getStr() + "# " + comment.strip() + "\n"
                codes += tabs.getStr() + "def " + block.getCodeStr() + "(self):\n"
                tabs.addTab()
                codes += tabs.getStr() + "raise NotImplementedError(\"" + block.codeLine + "\")\n"
                tabs.delTab()
                codes += "\n"
    
    return codes

def pdTestcaseSections(description):
    secotions = dict()
    secotions["header"] = [Block()]
    secotions["setup"] = [Block()]
    secotions["execute"] = [Block()]
    secotions["verify"] = [Block()]
    secotions["clear"] = [Block()]
    
    curSection = secotions["header"]
    
    lines = description.split("\n")
    for line in lines:
        sline = line.strip() 
        if (sline != ""):
            if (sline == "setup:"):
                curSection = secotions["setup"]
            elif (sline == "execute:"):
                curSection = secotions["execute"]
            elif (sline == "verify:"):
                curSection = secotions["verify"]
            elif (sline == "clear:"):
                curSection = secotions["clear"]
            elif (curSection == secotions["header"]):
                curSection[-1].comments.append(sline.replace("\t", "    "))
            else:
                if (sline[0] == "*"):
                    curSection.append(Block())
                    curSection[-1].codeLine = sline.replace("\t", "    ")
                else:
                    curSection[-1].comments.append(sline.replace("\t", "    "))

    return secotions

if __name__ == '__main__':
    pdTestcaseGen()