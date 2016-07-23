'''
Hand Class
'''

import maya.cmds as cmds

from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import locator
from autorigger.lib import attribute

from autorigger.modules import part
from autorigger.modules import finger



#limb inherits a bit from IkfkLimb
class Hand(part.Part):

    def __init__(self,
                 name,
                 position = (12,10,0.25),
                 fingerCount=5,
                 fingerPositions=([0.5,0,0.05],[0,0,0.5],[0,0,0],[0,0,-0.5],[0,0,-1]) ):
        super(Hand,self).__init__(name)
        self.position = position
        self.fingerCount = fingerCount
        self.fingerPositions = fingerPositions
        self.guides = list()
        #I don't ever expect to go over 5, but just in case here is 7
        #we can always add more if needed
        fingerNameIterator = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        self.fingerRig = list()
        for i in range(0, self.fingerCount):
            #store finger name in variable
            replaceHand = self.getName().replace('hand', 'finger')
            fingerName = "{0}{1}".format( replaceHand, fingerNameIterator[i] )

            if i==0:
                #thumb would only have a finger count of 4
                self.fingerRig.append(finger.Finger(fingerName,
                                                        jointCount=4,
                                                        positions=(
                                                            [1,0,0],
                                                            [1.5,0,0],
                                                            [2,0,0],
                                                            [2.5,0,0] )))
            else:
                #store class in list
                self.fingerRig.append( finger.Finger(fingerName) )


    def setup(self):
        super(Hand,self).setup()

        #store masterGuide in self.guides
        self.guides.append( self.masterGuide )

        '''
        if self.getSide() == nameSpace.SIDES["right"]:
            self.position = (-12,10,0.25)
            self.fingerPositions = ([-0.5,0,0.05],[0,0,0.5],[0,0,0],[0,0,-0.5],[0,0,-1])
        '''

        #add aim and up attr to masterGuide
        self.aimAttr = attribute.switch(self.masterGuide.getName(),
                        "aim",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])

        self.upAttr = attribute.switch(self.masterGuide.getName(),
                        "up",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])

        self.masterGuide.setPosition( self.position )
        for index,finger in enumerate(self.fingerRig):
            #create all the finger setups
            finger.setup()
            #place the master guides
            finger.masterGuide.setPosition( self.fingerPositions[index] )
            #parent constraint them to masterGuides
            cmds.parentConstraint( self.masterGuide.getName(), finger.setupGroup)
            #connect aim and up from hand master guide to each finger master guide
            cmds.connectAttr( "{0}.aim".format( self.masterGuide.getName() ),
                              "{0}.aim".format( finger.masterGuide.getName() ) )
            cmds.connectAttr( "{0}.up".format( self.masterGuide.getName() ),
                              "{0}.up".format( finger.masterGuide.getName() ) )

            #hide the attributes on the fingers
            cmds.setAttr( "{0}.aim".format(finger.masterGuide.getName()),
                          lock=True, keyable=False, channelBox=False)
            cmds.setAttr( "{0}.up".format(finger.masterGuide.getName()),
                          lock=True, keyable=False, channelBox=False)
            

            #And finally, append finger guide to self.guide
            for guides in finger.guides:

                self.guides.append( guides )


        #rotate thumb (fingerA) to point outwards
        cmds.select(self.fingerRig[0].masterGuide.getName())
        cmds.rotate(0,-90,0,r=True)

        #position hand master guide
        cmds.select( "{0}.cv[*]".format(self.masterGuide.getName()) )
        cmds.scale(1.5,1.5,1.5,r=True)
        cmds.move(0,0.5,0,r=True)
        cmds.select(cl=True)

        #set it's color
        self.masterGuide.setColor(17)
        self.masterGuide.setPosition( self.position )

        print '{0}.up'.format(self.masterGuide.getName())
        cmds.setAttr( '{0}.up'.format(self.masterGuide.getName()), 1 )

    def postSetup(self):
        #super(Hand,self).postSetup()
        #run postSetup on each finger

        for finger in self.fingerRig:
            finger.postSetup()

    def preBuild(self):
        #super(Hand,self).preBuild()
        #run preBuild on each finger

        for finger in self.fingerRig:
            finger.preBuild()

        cmds.delete(self.setupGroup)

    def build(self):
        super(Hand,self).build()

        cmds.createNode("transform", n=self.group)
        cmds.createNode("transform", n=self.hookGroup)
        cmds.parent(self.hookGroup, self.group)

        #run build on each finger
        for index,finger in enumerate(self.fingerRig):

            finger.build()

            #parent all to hook
            cmds.parent(finger.group, self.hookGroup)


        # Connections
        #fingerC1 and D1 rotate at a percentage of fingerE1
        fingerC1Mdn = cmds.createNode('multiplyDivide', n="{0}_mdn".format(self.fingerRig[2].getName() ))
        fingerD1Mdn = cmds.createNode('multiplyDivide', n="{0}_mdn".format(self.fingerRig[3].getName() ))
        #set fingerC1Mdn.input2 to 0.50
        cmds.setAttr( "{0}.input2X".format(fingerC1Mdn), 0.25 )
        cmds.setAttr( "{0}.input2Y".format(fingerC1Mdn), 0.25 )
        cmds.setAttr( "{0}.input2Z".format(fingerC1Mdn), 0.25 )
        #set fingerD1Mdn.input2 to 0.25
        cmds.setAttr( "{0}.input2X".format(fingerD1Mdn), 0.5 )
        cmds.setAttr( "{0}.input2Y".format(fingerD1Mdn), 0.5 )
        cmds.setAttr( "{0}.input2Z".format(fingerD1Mdn), 0.5 )
        #connect fingerE to mdn input1x
        cmds.connectAttr( "{0}.rotate".format(self.fingerRig[4].getfkChainControlName(0)), "{0}.input1".format(fingerC1Mdn) )
        cmds.connectAttr( "{0}.rotate".format(self.fingerRig[4].getfkChainControlName(0)), "{0}.input1".format(fingerD1Mdn) )
        #now connect mdn output to fingerc and d
        cmds.connectAttr( "{0}.output".format(fingerC1Mdn), "{0}.rotate".format(self.fingerRig[2].getfkChainControlName(0)) )
        cmds.connectAttr( "{0}.output".format(fingerD1Mdn), "{0}.rotate".format(self.fingerRig[3].getfkChainControlName(0)) )

        #now hide and lock the finger controls we won't need
        cmds.select( self.fingerRig[1].getfkChainControlName(0),
                     self.fingerRig[2].getfkChainControlName(0),
                     self.fingerRig[3].getfkChainControlName(0) )
        cmds.pickWalk(d='down')
        cmds.delete()

        #make the pinky hand ctrl a little bigger
        cmds.select("{0}.cv[*]".format(self.fingerRig[4].getfkChainControlName(0)))
        cmds.scale(2,2,2,r=True)
        cmds.select(cl=True)


        # clean up: hierarchy


    def postBuild(self):
        super(Hand,self).postBuild()
        #run postBuild on each finger
        for index,finger in enumerate(self.fingerRig):

            finger.postBuild()






