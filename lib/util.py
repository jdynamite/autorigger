'''

Utility nodes

'''

import maya.cmds as cmds
import maya.api.OpenMaya as om
import math


class Switch(object):
    """
    switch routine to mimic other languages switch
    """

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):

        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

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
        err = "Must an aim vector and an up vector."
        raise RuntimeError(err)
        return

    newArgs = []

    for arg in args:
        if type(arg) in instances[:2]:
            if len(arg) == 3:
                newArgs.append(om.MVector(arg[0], arg[1], arg[2]))
            else:
                error = "Passed argument {0} is not of len 3."
                raise RuntimeError(error.format(arg))
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

    return [math.degrees(eu) for eu in [euler.x, euler.y, euler.z]]


def plugCheck(obj, plug):
    if not cmds.objExists(obj):
        raise RuntimeError("{0} doesn't exist.".format(obj))

    if not cmds.attributeQuery(plug, node=obj, exists=True):
        warn = "Couldn't find the attr {0} in {1}."
        print warn.format(plug, obj)

        plug = 'output' + plug[0].upper() + plug[1:]
        if not cmds.attributeQuery(plug, node=obj, exists=True):
            err = "Couldn't find the attr {0} in {1}."
            raise RuntimeError(err.format(plug, obj))
        else:
            print "Using {0} instead.".format(plug)

    return '.'.join([obj, plug])


def subtract(a, b, plug="translate", name=None):
    """
    subtract b.plug from a.plug
    returns plusMinusAverage
    """

    # determine which plug to use

    objects = [a, b]
    plugs = [plug, plug]

    plugs = [plugCheck(obj, p) for obj, p in zip(objects, plugs)]

    # create use general input (translate) or tx | ty | tz ?

    useTriple = True

    for p in plugs:
        for axis in ["X", "Y", "Z"]:
            if p.endswith(axis) or p.endswith(axis.lower()):
                useTriple = False

    name = name if name is not None else "plusMinusAverage#"
    pma = cmds.createNode("plusMinusAverage", n=name)
    cmds.setAttr("{0}.operation".format(pma), 2)
    attrs = ["input3D[0]", "input3D[1]"] if useTriple else [
        "input3D[0].input3Dx", "input3D[1].input3Dx"]
    inputs = ['.'.join([pma, attr]) for attr in attrs]

    for p, input in zip(plugs, inputs):
        cmds.connectAttr(p, input, f=True)

    return pma


def add(a, b, plug="translate", name=None):
    """
    add a and b with PMA if plug is not a component plug
    """

    # determine which plug to use

    objects = [a, b]
    plugs = [plug, plug]

    plugs = [plugCheck(obj, p) for obj, p in zip(objects, plugs)]

    # create PMA or doubleLinear ?

    useTriple = True

    for p in plugs:
        for axis in ["X", "Y", "Z"]:
            if p.endswith(axis) or p.endswith(axis.lower()):
                useTriple = False

    if useTriple:
        name = name if name is not None else "plusMinusAverage#"
        pma = cmds.createNode("plusMinusAverage", n=name)
        attrs = ["input3D[0]", "input3D[1]"]
        inputs = ['.'.join([pma, attr]) for attr in attrs]
        for p, input in zip(plugs, inputs):
            cmds.connectAttr(p, input, f=True)
        return pma
    else:
        name = name if name is not None else "addDoubleLinear#"
        adl = cmds.createNode("addDoubleLinear", n=name)
        attrs = ["input1", "input2"]
        inputs = ['.'.join([adl, attr]) for attr in attrs]
        for p, input in zip(plugs, inputs):
            cmds.connectAttr(p, input, f=True)
        return adl


def multiply(a, b):
    pass


def divide(a, b):
    pass


def getParam(pt=[0, 0, 0], crv=None):

    if crv is None:
        return

    point = om.MPoint(pt[0], pt[1], pt[2])
    curveFn = om.MFnNurbsCurve(getDag(crv))
    isOnCurve = curveFn.isPointOnCurve(point)

    if isOnCurve:
        return curveFn.getParamatAtPoint(point, 0.001, om.MSpace.kObject)
    else:
        point = curveFn.closestPoint(point, 0.001, om.MSpace.kObject)
        return curveFn.getParamAtPoint(point, 0.001, om.MSpace.KObject)


def getDag(obj):

    if not cmds.objExists(obj):
        err = "{0} doesn't exist."
        raise RuntimeError(err.format(obj))

    if 'dagNode' not in cmds.nodeType(obj, inherited=True):
        err = "{0} is not a dag node"
        raise RuntimeError(err.format(obj))

    sel = om.MSelectionList()

    if type(obj) in [list, tuple]:
        for i, o in enumerate(obj):
            sel.add(o)
            return sel.getDagPath(i)
    elif isinstance(obj, basestring):
        sel.add(obj)
        return sel.getDagPath(0)
    else:
        warn = "Couldn't parse {0} as it isn't str | list | tuple."
        raise RuntimeWarning(warn.format(obj))
        return obj


def getMObject(obj):
    sel = om.MSelectionList()
    if type(obj) in [list, tuple]:
        for i, o in enumerate(obj):
            sel.add(o)
            return sel.getDependNode(i)
    elif isinstance(obj, basestring):
        sel.add(obj)
        return sel.getDependNode(0)
    else:
        warn = "Couldn't parse {0} as it isn't str | list | tuple."
        raise RuntimeWarning(warn.format(obj))
        return obj


def strBetween(string, start, end):
    """
    given string="body.vtx[0]"
    and start '.', end '['
    will return "vtx"
    """

    if not all(isinstance(arg, basestring) for arg in [string, start, end]):
        raise RuntimeError("Please pass three strings.")

    iis = string.index(start) + 1
    iie = string.index(end)

    return string[iis:iie]
