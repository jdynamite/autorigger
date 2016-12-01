# lips setup using super ribbons

import maya.cmds as cmds
from autorigger.lib import ribbon

def createLipRibbon(name, cvs):
    '''

        DIRECTIONS:
            planes should already be created. Both HR and LR
            CV selection MUST be from left to right ALWAYS

    '''


    # create lips master
    cmds.createNode("transform", n="name_GRP")

    rbn = ribbon.superRibbon(name, cvs)

    # get center of selection count
    cvCount = len(cvs)
    center = cvCount/2

    # then just rename them accordingly
    for cv in range(cvCount):
        prefix = "L_"
        if cv == center:
            prefix = "C_"
        if cv > center:
            prefix = "R_"

        addPrefix(prefix, rbn[cv])

    # parent to hierarchy

def addPrefix(prefix, dict):

    dictList = [
        "master",
        "cNull",
        "jNull",
        "con",
        "jnt",
        "fol"
    ]

    for i in dictList:
        newName = "{0}{1}".format(prefix, dict[i])
        cmds.rename(dict[i], newName)



