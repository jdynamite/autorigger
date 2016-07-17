'''
mayaBaseObject
'''

import maya.cmds as cmds
import nameSpace


class MayaBaseObject(object):

<<<<<<< HEAD
<<<<<<< HEAD

    def __init__(self, name, position=(0, 0, 0), parent=None, nameType=None):
=======
=======
>>>>>>> origin/master
    kLeftPrefix = ["l", "lf", "l", "left", "L"]
    kRightPrefix = ["r", "rt", "right", "R"]
    kSidePrefix = kLeftPrefix + kRightPrefix

    def __init__(self, name="baseObject", side="", position=(0, 0, 0), parent="None", nameType=nameSpace.NULL):
<<<<<<< HEAD
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
>>>>>>> origin/master

        self.name = name
        self.nameType = nameType
        self.side = side
        self.position = position
        self.parent = parent
        self.long_name = None

<<<<<<< HEAD
<<<<<<< HEAD
        self.side = nameSpace.getSide(self.name)
=======
        self.format_name()
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
        self.format_name()
>>>>>>> origin/master

    '''
    def sanitize_name(self):

        nameTypeWithUnderscore = "_{0}".format(self.nameType)

        if self.name.endswith(nameTypeWithUnderscore):
            self.name = self.name.replace(nameTypeWithUnderscore, "")
 
        for side in self.kSidePrefix:
            if self.name.startswith(side + nameSpace.DELIMITER):
                self.name = self.name[len(side):]

    def format_name(self):

        self.sanitize_name()


        if not len(self.side):
            self.long_name = "_".join([self.name, self.nameType])
            self.color = nameSpace.COLORS["default"]
            return

<<<<<<< HEAD
<<<<<<< HEAD

        # remove alphanumeric characters from side
        #self.side = ''.join([i for i in self.side if i.isalpha()])
=======
        # removed this line since I changed how the formatting works
        # self.side = ''.join([i for i in self.side if i.isalpha()])
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
        # removed this line since I changed how the formatting works
        # self.side = ''.join([i for i in self.side if i.isalpha()])
>>>>>>> origin/master

        if self.side.lower() not in self.kSidePrefix:
            raise NotImplementedError("The input side is not a valid one.")

        # assert if resulting side is left or right

        if self.side.lower() in self.kLeftPrefix:
            self.side = nameSpace.LEFT
            self.color = nameSpace.COLORS["left"]
        else:
            self.side = nameSpace.RIGHT
            self.color = nameSpace.COLORS["right"]

<<<<<<< HEAD
<<<<<<< HEAD
        self.long_name = "_".join([self.side, self.name, self.nameType])
    '''
=======
=======
>>>>>>> origin/master
        self.long_name = nameSpace.DELIMITER.join([self.side, self.name, self.nameType])

    def getSide(self):
        return self.side
<<<<<<< HEAD
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
>>>>>>> origin/master

    def getColor(self):
        return self.color

    def getName(self):
        return self.name

    def getParent(self):
        #parent = cmds.listRelatives(self.getName(), p=True)
        #if parent:
        #    self.setParent(parent[0])
        return self.parent

    def getPosition(self):
        if not cmds.objExists(self.getName()):
            return self.position
<<<<<<< HEAD
<<<<<<< HEAD
        self._position = cmds.xform(self.getName(),q=True,ws=True,t=True)
=======
        self._position = cmds.xform(
            self.getLongName(), q=True, ws=True, t=True)
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
        self._position = cmds.xform(
            self.getLongName(), q=True, ws=True, t=True)
>>>>>>> origin/master
        return self.position

    def getRotation(self):
        self.rotation = cmds.xform(self.long_name, q=True, ws=True, ro=True)
        return self.rotation

    def setColor(self, value):
<<<<<<< HEAD
<<<<<<< HEAD
        if not isinstance(value, int):
            raise TypeError("{0} must be an integer".format(value))
        attr = "{0}.overrideColor".format(self.getName())
=======
=======
>>>>>>> origin/master

        value = self.colorAsInt(value)
        attr = "{0}.overrideColor".format(self.getLongName())

<<<<<<< HEAD
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
>>>>>>> origin/master
        if cmds.objExists(attr):
            cmds.setAttr("{0}.overrideEnabled".format(self.getName()), 1)
            cmds.setAttr(attr, value)
            
        self.color = value

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/master
    def colorAsInt(self, value):
        if not isinstance(value, int):
            if isinstance(value, basestring) and value in nameSpace.COLOR_TO_INT.keys():
                return nameSpace.COLOR_TO_INT[value]
            else:
                raise TypeError("{0} must be an integer".format(value))
        else:
            return value

    def setName(self, value):

        # if isinstance is not none
        if not isinstance(value, basestring):
            raise TypeError("{)} is not of type str or unicode.".format(value))
        # cmds.rename( self.getName(), value )
        self.name = value

>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
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
        if not cmds.objExists(value):
            raise RuntimeError(
                "{0} does not exist in your current scene".format(value))

<<<<<<< HEAD
<<<<<<< HEAD
        parent = cmds.listRelatives(self.getName(), p=True)[0]
=======
=======
>>>>>>> origin/master
        print self.getLongName()
        parent = cmds.listRelatives(self.getLongName(), p=True)[0]
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd

        child = self.getName()

        if not parent:
            cmds.parent(child, value)
        # ! a node may have 2 zeros above it. Change this func later so
        # we can parent the topNode. At the moment this code only parents 1
        # above.
        elif parent:
            cmds.parent(parent, value)

        self._parent = value

    def setPosition(self, value):
        self.position = tuple(value)
        cmds.xform(self.getName(), ws=True, t=self.position)

    def setRotation(self, value):
        self.rotation = value
        cmds.xform(self.long_name, ws=True, ro=self.rotation)

<<<<<<< HEAD
<<<<<<< HEAD



=======
    # def create(self):
    #    self.setGroup(cmds.createNode("transform", n="ikfk_grp"))
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd
=======
    # def create(self):
    #    self.setGroup(cmds.createNode("transform", n="ikfk_grp"))
>>>>>>> origin/master
