'''
Finger class
'''

# imported goods
import maya.cmds as cmds

from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import locator
from autorigger.modules import fkChain


#Class is now in session
class Finger(fkChain.FkChain):

    def __init__(self, name, jointCount=5, positions=([1, 0, 0], [2, 0, 0], [2.5, 0, 0], [3, 0, 0], [3.5, 0, 0]), subCtrl=False ):
        super(Finger,self).__init__(name)

        self.jointPositions = list()
        self.jointCount = jointCount
        self.fkChainJoints = list()
        self.subCtrl = subCtrl

        for count in range(0,self.jointCount):

            #store class in self.fkChainJoints list
            index = count+1

            self.fkChainJoints.append(
                joint.Joint(
                    "{0}{1}_{2}".format(self.getName(),
                    str(index),
                    nameSpace.BINDJOINT)
                )
            )

            self.jointPositions.append( positions[count] )

    def setup(self):
        super(Finger,self).setup()
        #shrink the guides for the fingers. I mean really... Shrink them!

        for i in self.guides:
            cmds.select( i.getName() )
            cmds.scale( 0.2 ,0.2 ,0.2 ,r=True)

        #move the upv
        self.fkChainUpv.setPosition( (2,2,0) )
        #rotate and scale the masterGuides to look more appropriate
        cmds.select("{0}.cv[*]".format( self.masterGuide.getName() ))
        cmds.rotate(90,0,0,r=True)
        cmds.scale(0.9,0.9,0.9,r=True)
        cmds.select(cl=True)


    def postSetup(self):
        super(Finger,self).postSetup()

    def preBuild(self):
        super(Finger,self).preBuild()

    def build(self):
        super(Finger,self).build()
        #scale down the controls! They're too big!
        for i in self.mainCtrls:
            cmds.select( "{0}.cv[*]".format(i.getName()) )
            cmds.scale( 0.25 ,0.25 ,0.25 ,r=True)
            cmds.select(cl=True)


    def postBuild(self):
        super(Finger,self).postBuild()







