import json
import sys
import os
import maya.cmds as cmds
import curve as animCurve
from autorigger.lib import nameSpace
reload(animCurve)
reload(nameSpace)



def dump(data):

    if isinstance(data, dict):
        return json.dumps(data, sort_keys = True, indent = 4)
    else:
        raise TypeError("{0} must be of type dict()".format(data))


def save(data, filepath):

    f = open(filepath,'w')
    newData = dump(data)
    f.write(newData)
    f.close()

# load shapes from filepath
def load(filepath):

    f = open(filepath, "r")
    data = json.loads(f.read())
    f.close()

    return data

def export():
    controlDict = {}
    for ctrl in cmds.ls(type="transform"):
        shapes = cmds.listRelatives(ctrl, shapes=True, type="nurbsCurve")
        print shapes
        if shapes:
            controlDict[ctrl] = dict()
            controlDict[ctrl]["shapes"] = dict()
            for shape in shapes:
                controlDict[ctrl]["shapes"][shape] = dict()
                cvs = animCurve.getCVs(shape)
                cvPositions = animCurve.getCVpositions(cvs)
                controlDict[ctrl]["shapes"][shape]["positions"] = cvPositions
                controlDict[ctrl]["shapes"][shape]["color"] = cmds.getAttr("{0}.overrideColor".format(shape))
                controlDict[ctrl]["shapes"][shape]["degree"] = cmds.getAttr("{0}.degree".format(shape))

    save(controlDict,nameSpace.CONTROL_LIB_PATH)