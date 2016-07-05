'''
mayaBaseObject
'''

import maya.cmds as cmds


class MayaBaseObject(object):
    def __init__(self, name, position=(0, 0, 0), parent="None"):

        self.name = name
        self.position = position
        self.parent = parent

    def getColor(self):
        return self.color

    def getName(self):
        return self.name

    def getParent(self):
        parent = cmds.listRelatives(self.getName(), p=True)
        if parent:
            self.setParent(parent[0])
        return self.parent

    def getPosition(self):
        if not cmds.objExists(self.getName):
            return self.position
        self._position = cmds.xform(self.getName(),q=True,ws=True,t=True)
        return self.position

    def getRotation(self):
        self.rotation = cmds.xform(self.name,q=True,ws=True,ro=True)
        return self.rotation

    def setColor(self, value):
        if not isinstance(value, int):
            raise TypeError("{0} must be an integer".format(value))
        attr = "{0}.overrideColor".format(self.getName())
        if cmds.objExists(attr):
            cmds.setAttr("{0}.overrideEnabled".format(self.getName()), 1)
            cmds.setAttr(attr, value)
        self.color = value

    def setName(self, value):

        # if isinstance is not none
        if not isinstance(value, basestring):
            raise TypeError("{)} is not of yype str or unicode.".format(value))
        # cmds.rename( self.getName(), value )
        self.name = value

    def setOrientation(self, downAxis):

        correctInput = (downAxis == "x" or "y" or "z")
        #if downAxis input is not x, y, or z, raise RuntimeError
        if ( not correctInput):
            raise RuntimeError("setOrientation proc only takes in 'x', 'y', or 'z' CASE SENSITIVE")
        else:
            if (downAxis == 'x'):
                #select all CV
                cmds.select( "{0}.cv[*]".format(self.getName()) )
                #rotate to point down X
                cmds.rotate( 0,0,-90, r=True)

            if (downAxis == 'z'):
                #select all CV
                cmds.select( "{0}.cv[*]".format(self.getName()) )
                #rotate to point down X
                cmds.rotate( 90,0,0, r=True)

    def setParent(self, value):
        if not cmds.objExists(value):
            raise RuntimeError("{0} does not exist in your current scene".format(value))

        parent = cmds.listRelatives(self.getName(), p=True)

        child = self.getName()

        if not parent:
            cmds.parent(child, value)
        elif parent and not value == parent[0]:
            cmds.parent(child, value)

        self._parent = value

    def setPosition(self, value):
        self.position = tuple(value)
        cmds.xform(self.getName(), ws=True, t=self.position)

    def setRotation(self,value):
        self.rotation = value
        cmds.xform(self.name, ws=True,ro=self.rotation)



    #def create(self):
    #    self.setGroup(cmds.createNode("transform", n="ikfk_grp"))





