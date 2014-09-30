#!/usr/bin/python
import os
import sys
import pb_exception

def genFakeTaskInfo():
    taskInfo = {}
    taskInfo["TestDir"] = os.getcwd()
    taskInfo["ClientDir"] =  os.getcwd()
    taskInfo["TestCaseId"] = 2002
    taskInfo["TestResultId"] = 2002
    taskInfo["DownloadCommand"] = "cp /smart_test/%input %output"
    taskInfo["ScriptPath"] = "pb_test.py"
    taskInfo["ScriptArgs"] = 'reinstall=yes'
    taskInfo["TestProperties"] = [{ "Name": "Software.build", "Value": "1.0.0-010"}, \
                                  { "Name": "SUT.hostname", "Value": "maa-taa-01.sin.ds.jdsu.net"}]
    taskInfo["TestClientInfo"] = { "Name": "sa-pi-02.sin.ds.jdsu.net", \
                                   "Properties": [{ "Name": "res.loc", "Value": "sgp"}], \
                                   "Criteria" : [ { "Name": "res.loc", "Value": "sgp" }] }
    taskInfo["ResourcesInfo"] = [ { "Name": "maa-taa-01.sin.ds.jdsu.net",
                                    "Properties": [{ "Name": "comp.type", "Value": "pb"}, { "Name": "Server.type", "Value": "TAA"}], \
                                    "Criteria": [{ "Name": "Server.type", "Value": "TAA"}]}, \
                                  { "Name": "sa-pi-02.sin.ds.jdsu.net", \
                                    "Properties": [{ "Name": "Server.type", "Value": "TG"}], \
                                    "Criteria": [{ "Name": "Server.type", "Value": "TG"}]}, \
                                ]
    return taskInfo

def getPropertyValue(taskInfo, name):
    value = None
    for prop in taskInfo["TestProperties"]:
        if (prop["Name"] == name):
            value = prop["Value"]
            break
    if value == None:
        raise pb_exception.PBException("Can not find " + name + " in Property")
    return value

def getPropertyValueFromList(properties, name):
    value = None
    for prop in properties:
        if (prop["Name"] == name):
            value = prop["Value"]
            break
    if value == None:
        raise pb_exception.PBException("Can not find " + name + " in Property")
    return value