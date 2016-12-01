__author__ = 'darata'
#----------------------------------------------------------------------------#
#------------------------------------------------------------------ HEADER --#
"""
:newField description: Description
:newField revisions: Revisions
:newField departments: Departments
:newField applications: Applications
------------------------------------------------------------------------------
:Authors:
    - Daniel Arata
:Title:
    Build Single


:Description:
    Builds a simple rig hierarchy consisting of just a joint and a control.
    Hierarchy looks like:
        CON_NULL
          CON
            JNT_NULL
              JNT
    Handy for when rigging simple separate geo that don't need to necessarily
    need to deform. Think mechanical rigs.
============
Introduction
============
"""
#----------------------------------------------------------------------------#
#----------------------------------------------------------------- IMPORTS --#
# Built-in
# Third Party
import maya.cmds as cmds
# Custom
from autorigger.lib import control
def buildSingle( name, shape="circle", color="yellow", position=(0, 0, 0)):
    """
    Creates a basic joint and control hierarchy
    :parameters:
        name : str
            The PART name of rig. Leave out "_JNT" and "_CON" etc
        shape: str
            Takes a shape name to be input into rig_tools.core.control creation
        color:
            Also takes in a color to be input into rig_tools.core.control creation
    """
    master = "{0}_GRP".format(name)
    cmds.createNode("transform", n=master)
    #create joint
    cmds.select( cl=True )
    jnt = cmds.joint( n=(name + "_JNT") )
    #joint null
    jNull = cmds.group(n=(jnt+"_NULL"))
    #control
    conBuffer = control.Control( name = (name+"_CON"), shape=shape, color=color)
    conBuffer.create()
    con = conBuffer.getName()
    #control null
    cNull = conBuffer.getNull()
    cmds.parent( jNull, master )
    cmds.parent( cNull, master)
    attrs = ["t", "r", "s"]
    for attr in attrs:
        cmds.connectAttr(
            "{0}.{1}".format(con, attr),
            "{0}.{1}".format(jnt, attr)
        )
    #position the mofo
    #cmds.xform( cNull, t=position, ws=True  )
    #kill it off by selecting the con. It pleases me.
    cmds.select(con)
    result = {
        "master": master,
        "cNull": cNull,
        "jNull": jNull,
        "con": con,
        "jnt": jnt
    }
    return result

def buildMultiple(name, count):
    '''

    :param name: name of setup
    :param count: how many singleRigs you'll need
    :return: returns dict of all created in hierarchy
    '''
    result = []

    for i in range(count):
        thisName = name+str(i+1)
        #buildControls with buildSingle
        bs = buildSingle(thisName)
        result.append(bs)

    return result
