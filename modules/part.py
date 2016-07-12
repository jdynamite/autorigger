'''

Modules will inherit mainly from this base Part Class

-Setup: position joints
-Build: build off positioned joints

'''

import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import mayaBaseObject
from autorigger.lib import control
from autorigger.lib import nameSpace

reload(control)

class Part(mayaBaseObject.MayaBaseObject):

    def __init__(self, name, side, position=[0,0,0]):
        super(Part, self).__init__(name=name, side=side, position=position, nameType=nameSpace.GROUP)
        self.group = "{0}_master_{1}".format(self.long_name, nameSpace.GROUP)
        self.jointsGroup = "{0}_joints_{1}".format(self.long_name, nameSpace.GROUP)
        self.controlsGroup = "{0}_controls_{1}".format(self.long_name, nameSpace.GROUP)
        self.noXformGroup = "{0}_noXform_{1}".format(self.long_name, nameSpace.GROUP)
        self.hookGroup = "{0}_hook_{1}".format(self.long_name, nameSpace.GROUP)

    def hookTo(self, hooker):
        pass

    def initializeSetup(self):
        self.setupGroup = nameSpace.DELIMITER.join([self.side, self.name, nameSpace.SETUP, nameSpace.GROUP])
        self.skeletonGroup = "{0}_{1}_skeleton_{2}".format(self.side, self.name, nameSpace.GROUP)
        self.guidesGroup = nameSpace.DELIMITER.join([self.side, self.name, nameSpace.GUIDE, nameSpace.GROUP])
        self.masterGuide = control.Control(name="master_{1}".format(self.getName(), nameSpace.GUIDE), side=self.side)

    def setup(self):

        #create self.variable for groups
        self.initializeSetup()

        cmds.createNode("transform", n=self.setupGroup)
        cmds.createNode("transform", n=self.skeletonGroup)
        cmds.createNode("transform", n=self.guidesGroup)

        cmds.parent(self.skeletonGroup, self.setupGroup)
        cmds.parent(self.guidesGroup, self.setupGroup)

        self.masterGuide.setParent(self.guidesGroup)

    def postSetup(self):
        pass

    def runSetup(self):
        self.setup()
        self.postSetup()

    def preBuild(self):
        # delete setup data(which is the guides)
        cmds.createNode("transform", n=self.group)
        cmds.addAttr(self.group, ln="bindJnts", at="message")
        cmds.createNode("transform", n=self.jointsGroup)
        cmds.createNode("transform", n=self.controlsGroup)
        cmds.createNode("transform", n=self.noXformGroup)
        cmds.createNode("transform", n=self.hookGroup)

        cmds.parent(self.jointsGroup, self.group)
        cmds.parent(self.controlsGroup, self.group)
        cmds.parent(self.noXformGroup, self.group)
        cmds.parent(self.hookGroup, self.group)

        cmds.delete(self.guidesGroup)

        cmds.parent(cmds.listRelatives(self.skeletonGroup, c=True), self.jointsGroup)

        cmds.delete(self.setupGroup)


    def build(self):
        #build will be coded in respective modules. This is just going to be inhereited empty
        pass

    def postBuild(self):
        pass

    def runBuild(self):
        self.preBuild()
        self.build()
        self.postBuild()

    def createGuide(self, name, side, jnt, position=(0, 0, 0), parent="world"):
        guide = control.Guide(name=name, position=position, side=side, parent=parent)

        # guide.create()
        guide.setColor(self.getColor())

        # [0] because i think constriants returns 2 in a variable
        # just like how polygons get returned in an array in mel thanks to shape

        # this line is bugging out, firs argument used to be name
        # but changing to guide.long_name didn't work
        constraint = cmds.pointConstraint(guide.long_name, jnt)[0]
        cmds.parent(constraint)

        return guide