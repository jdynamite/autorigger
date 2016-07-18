'''
mayaBaseObject
'''

import maya.cmds as cmds
import nameSpace


class MayaBaseObject(object):

    def __init__(self, name, position=(0, 0, 0), parent=None, nameType=None):

        self.name = name
        self.nameType = nameType

        self.position = position
        self.parent = parent
        self.long_name = None

        self.side = nameSpace.getSide(self.name)

    '''
    def sanitize_name(self):
        if self.name is None:
            self.name = "control"

        nameTypeWithUnderscore = "_{0}".format(self.nameType)
        if nameTypeWithUnderscore in self.name:
            self.name = self.name.replace(nameTypeWithUnderscore, "")

        for side in self.kSidePrefix:
            if self.name.startswith("%s_" % side):
                self.name = "".join(self.name.split("_")[1:])


    def format_name(self):

        self.sanitize_name()


        if not len(self.side):
            self.long_name = "_".join([self.name, self.nameType])
            return


        # remove alphanumeric characters from side
        #self.side = ''.join([i for i in self.side if i.isalpha()])

        if self.side.lower() not in self.kSidePrefix:
            raise NotImplementedError("The input side is not a valid one.")

        # assert if resulting side is left or right

        if self.side.lower() in self.kLeftPrefix:
            self.color = "blue"
        else:
            self.color = "red"

        self.long_name = "_".join([self.side, self.name, self.nameType])
    '''

    def getColor(self):
        return self.color

    def getName(self):
        return self.name

    def getParent(self):
        #parent = cmds.listRelatives(self.getName(), p=True)
        # if parent:
        #    self.setParent(parent[0])
        return self.parent

    def getPosition(self):
        if not cmds.objExists(self.getName()):
            return self.position
        self._position = cmds.xform(self.getName(), q=True, ws=True, t=True)
        return self.position

    def getRotation(self):
        self.rotation = cmds.xform(self.long_name, q=True, ws=True, ro=True)
        return self.rotation

    def setColor(self, value):
        if not isinstance(value, int):
            raise TypeError("{0} must be an integer".format(value))
        attr = "{0}.overrideColor".format(self.getName())
        if cmds.objExists(attr):
            cmds.setAttr("{0}.overrideEnabled".format(self.getName()), 1)
            cmds.setAttr(attr, value)
        self.color = value

    def setLongName(self, value):

        # if isinstance is not none
        if not isinstance(value, basestring):
            raise TypeError("{)} is not of type str or unicode.".format(value))
        # cmds.rename( self.getName(), value )
        self.long_name = value

    def setOrientation(self, downAxis):

        correctInput = (downAxis == "x" or "y" or "z")
        # if downAxis input is not x, y, or z, raise RuntimeError
        if (not correctInput):
            raise RuntimeError(
                "setOrientation proc only takes in 'x', 'y', or 'z' CASE SENSITIVE")
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
        print value

        if not cmds.objExists(value):
            raise RuntimeError(
                "{0} does not exist in your current scene".format(value))

        parent = cmds.listRelatives(self.getName(), p=True) or []
        child = self.getName()

        if not len(parent):
            cmds.parent(child, value)

        # ! a node may have 2 zeros above it. Change this func later so
        # we can parent the topNode. At the moment this code only parents 1
        # above.

        # ^ i added small function to take care of this
        # and make it flexible enough for other stuff

        else:
            parent = parent[0]
            parent = self.checkParent(parent, nameSpace.ZERO)
            cmds.parent(parent, value)

        self.parent = value

    def checkParent(self, obj, nameType):
        # returns parent if it matches nameType

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
        cmds.xform(self.long_name, ws=world, ro=self.rotation)
