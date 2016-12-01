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
    meatBrow

:Departments:
    rigging
:Description:
    This is my attempt for creating a non-modular meatBrow rig

:DIRECTIONS:
    Select components and run meatBrowRig(name)

============
Introduction
============
"""
import maya.cmds as cmds
from autorigger.lib import follicle
from buildSingle import buildSingle

def ribbonRig(name):
    #plane should already be created. UV 0-1
    # select CV's and run script

    # get CV position

    # find closest UV to CV



def meatBrowRig(name):
    components = cmds.ls(fl=True, orderedSelection=True)
    master = "{0}_GRP".format(name)
    if cmds.objExists(master):
        raise RuntimeError(
            "Naming convention of {0} already exists in scene. Please come up with someting more unique.".format(name)
        )
    cmds.createNode("transform", n=master)
    for i,component in enumerate(components):
        eval = follicle.isComponent(component)
        if not eval:
            raise RuntimeError("Must select polygon component(s) or nurbs CV(s)")
        else:
            prefix = "{}{:02d}".format(name, i+1)
            fol = setupRig(prefix, component)
            cmds.parent(fol, master)
    cmds.select(cl=True)



def setupRig(name, face):
    fol = follicle.createFollicle(
        node=face,
        name=name
    )
    bs = buildSingle(name, shape="sphere", color="yellow", position=(0, 0, 0))
    cmds.delete(cmds.parentConstraint(fol, bs["master"]))
    cmds.parent(bs["master"], fol)
    return fol