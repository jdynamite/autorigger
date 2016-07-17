'''
wrappers.py
Wrapper library for maya and package calls
'''

import maya.cmds as cmds
import joint as animJoint
import mayaBaseObject


def duplicate(node, newName=str(), connections=False):
    '''
    Duplicate
    '''
    if not cmds.objExists(node):
        raise RuntimeError("{0} does not exist in your currecnt scene".format(node))

    if connections:
        cmds.duplicate(node)[0]
    else:
        newNode = cmds.duplicate(node, rr=True, po=True)

    if newName:
        newNode = cmds.rename(newNode, newName)

    return newNode


def duplicateJoint(node, newName=str(), connections=False):
    node = duplicate(node, newName, connections)
    jnt = animJoint.Joint(node, cmds.xform(node, q=True, ws=True, t=True))

    return jnt



