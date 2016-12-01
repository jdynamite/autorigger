'''
attribute library
'''

import maya.cmds as cmds

def switch(node,attr,value=0,inputNames=list(),inputValues=list()):
    '''
    :param node:
    :param attr:
    :param value:
    :param inputName:
    :param inputValues:
    :return:
    '''

    attrName = "{0}.{1}".format(node,attr)
    choiceName = "{0}_{1}_switch".format(node,attr)
    cmds.createNode("choice",name=choiceName)
    cmds.addAttr(node,ln=attr,at="enum",en=":".join(inputNames),dv=value,keyable=True)

    for i in range(len(inputValues)):
        choiceAttr = "output{0}".format(i)
        cmds.addAttr(choiceName,ln=choiceAttr,at="double3")
        cmds.addAttr(choiceName,ln="{0}x".format(choiceAttr),at="double",p=choiceAttr,dv=inputValues[i][0])
        cmds.addAttr(choiceName,ln="{0}y".format(choiceAttr),at="double",p=choiceAttr,dv=inputValues[i][1])
        cmds.addAttr(choiceName,ln="{0}z".format(choiceAttr),at="double",p=choiceAttr,dv=inputValues[i][2])

        cmds.connectAttr("{0}.{1}".format(choiceName,choiceAttr),"{0}.input[{1}]".format(choiceName,i))

    cmds.connectAttr(attrName,"{0}.selector".format(choiceName),f=True)

    return "{0}.output".format(choiceName)

def connect( nodeA, nodeB, t=True, r=True, s=True):

    if t:
        cmds.connectAttr(
            "{0}.t".format(nodeA),
            "{0}.t".format(nodeB)
        )

    if r:
        cmds.connectAttr(
            "{0}.r".format(nodeA),
            "{0}.r".format(nodeB)
        )

    if s:
        cmds.connectAttr(
            "{0}.s".format(nodeA),
            "{0}.s".format(nodeB)
        )



