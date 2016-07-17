import maya.cmds as cmds

from autorigger.lib import mayaBaseObject
reload(mayaBaseObject)

class Locator(mayaBaseObject.MayaBaseObject):
    def __init__(self,name,position=(0,0,0),parent=None):
        super(Locator,self).__init__(name)

        self._position = tuple(position)
        self._parent = parent


    def create(self):
        cmds.spaceLocator(name=self.getName(), position=self.getPosition())