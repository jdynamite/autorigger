'''
mayaBaseObject
'''

import maya.cmds as cmds
import control
import nameSpace


class MayaBaseObject(object):

    def __init__(self, name, position=(0, 0, 0), parent=None, nameType=nameSpace.NULL):

        self.name = name
        self.nameType = nameType
        self.position = position
        self.parent = parent
        self.side = nameSpace.getSide(self.name)

    def getColor(self):
        return self.color

    def getName(self):
        return self.name

    def getParent(self):
        return self.parent

    def getPosition(self):
        if not cmds.objExists(self.getName()):
            return self.position
        self._position = cmds.xform(self.getName(), q=True, ws=True, t=True)
        return self.position

    def getRotation(self):
        self.rotation = cmds.xform(self.getName(), q=True, ws=True, ro=True)
        return self.rotation

    def setColor(self, value):
        if not isinstance(value, int):
            raise TypeError("{0} must be an integer".format(value))
        attr = "{0}.overrideColor".format(self.getName())
        if cmds.objExists(attr):
            cmds.setAttr("{0}.overrideEnabled".format(self.getName()), 1)
            cmds.setAttr(attr, value)
        self.color = value

    def setOrientation(self, downAxis):

        downAxis = downAxis.lower()

        # if downAxis input is not x, y, or z, raise RuntimeError
        if downAxis not in ['x', 'y', 'z']:
            err = "setOrientation proc only takes in 'x' | 'y' | 'z'"
            raise RuntimeError(err)
        else:
            if (downAxis == 'x'):
                # select all CV
                cmds.select("{0}.cv[*]".format(self.getName()))
                # rotate to point down X
                cmds.rotate(0, 0, -90, r=True)

            if (downAxis == 'z'):
                # select all CV
                cmds.select("{0}.cv[*]".format(self.getName()))
                # rotate to point down X
                cmds.rotate(90, 0, 0, r=True)

    def setParent(self, value):
        if not cmds.objExists(value):
            err = "{0} does not exist in your current scene."
            raise RuntimeWarning(err.format(value))
            return

        parent = cmds.listRelatives(self.getName(), p=True) or []
        child = self.getName()

        if not len(parent):
            cmds.parent(child, value)
            print 'here i am'

        else:
            parent = parent[0]
            parent = self.checkParent(parent, nameSpace.ZERO)
            cmds.parent(parent, value)
            print ' jk here i am'

        self.parent = value

    def checkParent(self, obj, nameType):
        # returns parent if parent matches nameType

        if obj is None:
            raise RuntimeError("Passed none to checkParent")
            return

        par = cmds.listRelatives(obj, p=True)

        if par is None:
            return obj

        suffix = nameSpace.DELIMITER + nameType
        par = par[0] if par[0].endswith(suffix) else obj
        return par

    def setPosition(self, value, world=True):
        self.position = tuple(value)
        cmds.xform(self.getName(), ws=world, t=self.position)

    def setRotation(self, value, world=True):
        self.rotation = value
        cmds.xform(self.getName(), ws=world, ro=self.rotation)

    def zero(self):
        null = self.name.strip(nameSpace.DELIMITER + self.nameType)
        null += nameSpace.DELIMITER + nameSpace.NULL
        self.null = cmds.duplicate(
            self.name,
            rc=True,
            n=null)[0]

        # delete children
        cmds.delete(cmds.listRelatives(self.null, ad=True))
        cmds.parent(self.name, self.null)
        self.parent = self.null

        if cmds.objExists(self.parent) and self.null is not self.parent:

            cmds.parent(self.null, self.parent)
