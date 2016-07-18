'''

Utility nodes

'''

import maya.cmds as cmds
import maya.api.OpenMaya as om
import math

# returns grp if it exists, otherwise creates the grp and returns it


def getGroup(grp):
    if not isinstance(grp, basestring):
        raise RuntimeError("Pass a string puhleeze.")
        return grp

    return grp if cmds.objExists(grp) else cmds.createNode("transform", n=grp)


# checks if a plugin is loaded. If not it will attempt to load it
def isPluginLoaded(plugin):

    checker = cmds.pluginInfo(plugin, query=True, l=True)
    if not checker:
        cmds.loadPlugin(plugin)

# pops and orients object's pivot to world origin without moving it


def pivotToOrigin(obj):

    is_parented = False
    old_par = cmds.listRelatives(obj, p=True)

    cmds.parent(obj, w=True)
    cmds.xform(obj, ztp=True, piv=[0.0, 0.0, 0.0])

    if old_par is not None and len(old_par):
        is_parented = True

    cmds.select(cl=True)
    grp = cmds.group(em=True)

    cmds.parent(obj, grp)
    cmds.makeIdentity(obj, apply=True, t=True, s=True, r=True)

    if is_parented:
        cmds.parent(obj, old_par)
    else:
        cmds.parent(obj, w=True)

    cmds.delete(grp)


def orthoOrient(*args):

    instances = [list, tuple, om.MVector, om.MPoint]

    if len(args) != 2:
        raise RuntimeError("Must pass exactly two arguments.")
        return

    newArgs = []
    for i, arg in enumerate(args):
        if type(arg) in instances[:2]:
            if len(arg) == 3:
                newArgs.append(om.MVector(arg[0], arg[1], arg[2]))
            else:
                error = "Passed argument {0} is not of len 3."
                raise RuntimeError(error.format(arg))
                return
        elif type(arg) not in instances[2:]:
            error = "Passed argument {0} is of invalid type {1}."
            raise RuntimeError(error.format(arg, type(arg)))

    a = args[0] if len(newArgs) == 0 else newArgs[0]
    b = args[1] if len(newArgs) < 1 else newArgs[1]

    cross = a ^ b
    b = cross ^ a

    rotMatrix = om.MMatrix()

    rotMatrix.setElement(0, 0, a.x)
    rotMatrix.setElement(0, 1, a.y)
    rotMatrix.setElement(0, 2, a.z)

    rotMatrix.setElement(1, 0, b.x)
    rotMatrix.setElement(1, 1, b.y)
    rotMatrix.setElement(1, 2, b.z)

    rotMatrix.setElement(2, 0, cross.x)
    rotMatrix.setElement(2, 1, cross.y)
    rotMatrix.setElement(2, 2, cross.z)

    matrixFn = om.MTransformationMatrix(rotMatrix)
    euler = matrixFn.rotation()

    return [math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)]
