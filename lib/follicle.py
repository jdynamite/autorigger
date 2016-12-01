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
    Follicle

:Description:
    Creates a follicle with given inputs
============
Introduction
============
"""
import maya.cmds as cmds
import maya.api.OpenMaya as om
from autorigger import cvshapeinverter

# currently only works for nurbs and nurbsCVs
def createFollicle(node, name="follicle"):
    u = 0.5
    v = 0.5
    sel = node

    cmds.select(node)
    cv = cmds.filterExpand(sm=28, fp=True)

    if cv:
        node = node.split(".")[0]
    shape = cvshapeinverter.get_shape(node)
    folShape = cmds.createNode("follicle", n="{0}_FOLShape".format(name))
    buffer = cmds.pickWalk(d="Up")[0]
    fol = cmds.rename(buffer, "{0}_FOL".format(name))
    cmds.setAttr("{0}.parameterU".format(folShape), u)
    cmds.setAttr("{0}.parameterV".format(folShape), v)

    cmds.connectAttr(
        "{0}.local".format(shape),
        "{0}.inputSurface".format(folShape)
    )

    cmds.connectAttr(
        "{0}.worldMatrix[0]".format(shape),
        "{0}.inputWorldMatrix".format(folShape)
    )

    cmds.connectAttr(
        "{0}.outRotate".format(folShape),
        "{0}.rotate".format(fol)
    )
    cmds.connectAttr(
        "{0}.outTranslate".format(folShape),
        "{0}.translate".format(fol)
    )

    if cv:
        # snap the follicle to the selection
        snapFollicleToCv(sel, shape, folShape)


    return fol


def snapFollicleToCv(cv, surf, folShape):
    pos = cmds.xform(cv, ws=True, t=True, q=True)
    loc = cmds.spaceLocator()[0]

    cmds.xform(loc, t=pos)
    cps = cmds.createNode("closestPointOnSurface")

    cmds.connectAttr(
        "{0}.translate".format(loc),
        "{0}.inPosition".format(cps)
    )

    cmds.connectAttr(
        "{0}.local".format(surf),
        "{0}.inputSurface".format(cps)
    )

    cmds.connectAttr(
        "{0}.parameterU".format(cps),
        "{0}.parameterU".format(folShape)
    )

    cmds.connectAttr(
        "{0}.parameterV".format(cps),
        "{0}.parameterV".format(folShape)
    )

    # delete the loc and cps
    cmds.disconnectAttr(
        "{0}.parameterU".format(cps),
        "{0}.parameterU".format(folShape)
    )

    cmds.disconnectAttr(
        "{0}.parameterV".format(cps),
        "{0}.parameterV".format(folShape)
    )

    cmds.delete(loc, cps)




def isComponent(shape):
    result = None
    cmds.select(shape)
    vert = cmds.polyEvaluate(vertexComponent=True)
    face = cmds.polyEvaluate(faceComponent=True)
    edge = cmds.polyEvaluate(edgeComponent=True)
    if vert > 0:
        result = "vert"
    elif face > 0:
        result = "face"
    elif edge > 0:
        result = "edge"
    else:
        result = False
    return result




