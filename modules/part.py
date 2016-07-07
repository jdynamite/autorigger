'''

Modules will inherit mainly from this base Part Class

-Setup: position joints
-Build: build off positioned joints

'''

import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import mayaBaseObject
from autorigger import control

class Part(mayaBaseObject.MayaBaseObject):

    def __init__(self, name, position=[0,0,0]):

        self.name = name
        # base position of the partRig
        self.position = position

        self.group = "{0}_master_{1}".format(name, nameSpace.GROUP)
        self.jointsGroup = "{0}_joints_{1}".format(name, nameSpace.GROUP)
        self.controlsGroup = "{0}_controls_{1}".format(name, nameSpace.GROUP)
        self.noXformGroup = "{0}_noXform_{1}".format(name, nameSpace.GROUP)
        self.hookGroup = "{0}_hook_{1}".format(name, nameSpace.GROUP)

        self.nameType = nameSpace.GROUP

    def hookTo(self, hooker):
        pass

    def initializeSetup(self):
        self.setupGroup = "{0}_{1}_{2}".format(self.getName(), nameSpace.SETUP, nameSpace.GROUP)
        self.skeletonGroup = "{0}_skeleton_{1}".format(self.getName(), nameSpace.GROUP)
        self.guidesGroup = "{0}_{1}_{2}".format(self.getName(), nameSpace.GUIDE, nameSpace.GROUP)
        self.masterGuide = control.Control("{0}_master_{1}".format(self.getName(), nameSpace.GUIDE))

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
