'''
Foot class
'''

import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import locator
from autorigger.lib import attribute
from autorigger.modules import part
#from autorigger.lib.setDrivenKey as animSdk

reload(nameSpace)
reload(control)
reload(joint)
reload(locator)
reload(attribute)
reload(part)
#reload(animSdk)

#limb inherits a bit from IkfkLimb
class Foot(part.Part):

    def __init__(self,name, position=( 1,0,0 ) ):
        super(Foot,self).__init__(name)
        self.name = name
        self.position = position

        #call joint classes
        self.ankle = joint.Joint("{0}_ankle_{1}".format(self.getSide(),nameSpace.JOINT))
        self.ball = joint.Joint("{0}_ball_{1}".format(self.getSide(),nameSpace.JOINT))
        self.tipToe = joint.Joint("{0}_tiptoe_{1}".format(self.getSide(),nameSpace.JOINT))
        self.heel = joint.Joint("{0}_heel_{1}".format(self.getSide(),nameSpace.JOINT))
        self.inPivot = joint.Joint("{0}_inPivot_{1}".format(self.getSide(),nameSpace.JOINT))
        self.outPivot = joint.Joint("{0}_outPivot_{1}".format(self.getSide(),nameSpace.JOINT))
        self.jointList = [ self.ankle, self.ball, self.tipToe,  self.heel, self.inPivot, self.outPivot ]
        self.guides = list()

        #self.ankle1
        self.ankle1 = joint.Joint("{0}_topAnkle_{1}".format(self.getSide(),nameSpace.JOINT))

    def setup(self):
        super(Foot,self).setup()

        #create an upvector for the foot joints
        self.footJntUpv = control.Control('{0}_upvGuide'.format(self.getName()), shape='cross')
        self.footJntUpv.create()
        cmds.parent( self.footJntUpv.getName(), self.masterGuide.getName())

        if self.getSide() == nameSpace.SIDES["left"]:
            #default positioning going in the order of self.jointList:
            self.jointPositions = [
                (0.25, 0.29, -0.06), #ankle
                (0.25, 0, 0.644), #ball
                (0.25, 0, 0.95), #tiptoe
                (0.25, 0, -0.215), #heel
                (0.065, 0, 0.5), #inpivot
                (0.46, 0, 0.5) ] #outp

            #move the masterguide
            self.masterGuide.setPosition( (2,0,0) )
            #move the upv
            self.footJntUpv.setPosition( (0.25,1,1) )

        elif self.getSide() == nameSpace.SIDES["right"]:
            #default positioning going in the order of self.jointList:
            self.jointPositions = [
                (-0.25, 0.29, -0.06), #ankle
                (-0.25, 0, 0.644), #ball
                (-0.25, 0, 0.95), #tiptoe
                (-0.25, 0, -0.215), #heel
                (-0.065, 0, 0.5), #inp
                (-0.46, 0, 0.5) ] #outp

            #move the masterguide
            self.masterGuide.setPosition( (-2,0,0) )
            #move the upv
            self.footJntUpv.setPosition( (-0.25,1,1) )

        #add aim and up attr to masterGuide
        self.aimAttr = attribute.switch(self.masterGuide.getName(),
                        "aim",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])

        self.upAttr = attribute.switch(self.masterGuide.getName(),
                        "up",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])
        #iterate through self.jointList
        #for each listItem in self.jointList
        parent = self.skeletonGroup

        for index,jnt in enumerate( self.jointList ):

            #create joint
            jnt.create()
            jnt.setPosition( self.jointPositions[index] )

            #if it's not the pivots
            if (index<4):
                # set parent
                jnt.setParent(parent)
                parent = jnt.getName()

                #if it's the heel, make it world
                if (index==3):
                    #no parent
                    cmds.select( jnt.getName() )
                    cmds.parent( w=True )
                    #and set joint orientations to zero
                    cmds.setAttr( "{0}.jointOrient".format( jnt.getName() )  )

            #if it is, parent them to the ankle
            else:
                jnt.setParent(parent)

            #create guides
            self.guides.append( self.createGuide(jnt.getName().replace(nameSpace.JOINT,nameSpace.GUIDE),
                             jnt.getName(),
                             jnt.getPosition(),
                             self.masterGuide.getName()) )
            #resize those guides.
            #cmds.select( self.guides[index].getName(),r=True )
            cmds.setAttr( "{0}.sx".format(self.guides[index].getName()), 0.15)
            cmds.setAttr( "{0}.sy".format(self.guides[index].getName()), 0.15)
            cmds.setAttr( "{0}.sz".format(self.guides[index].getName()), 0.15)


        aimConstraintList = list()

        for index,jnt in enumerate( self.jointList ):

            if ( index < 2):
                #all others are aimConstrained
                #aim constraint joint[jnt+1] to joint[jnt]
                aimCon = cmds.aimConstraint( self.guides[index+1].getName(),
                                            self.jointList[index].getName(),
                                            worldUpType='object',
                                            worldUpObject= self.footJntUpv.getName() )

                aimConstraintList.append( aimCon[0] )
                cmds.parent(aimConstraintList[index], self.guidesGroup)

        for cst in aimConstraintList:
            cmds.connectAttr(self.upAttr, "{0}.upVector".format(cst),f=True)
            cmds.connectAttr(self.aimAttr, "{0}.aimVector".format(cst),f=True)
            #cmds.setAttr("{0}.worldUpVector".format( cst ), self.upAttr )

        #so that the aim and up are not both x
        cmds.setAttr("{0}.up".format(self.masterGuide.getName()) ,1)
        self.strUpAttr = (cmds.getAttr ("{0}.up".format(self.masterGuide.getName()), asString = True))
        cmds.select(cl=True)

    def postSetup(self):
        super(Foot,self).postSetup()

    def preBuild(self):
        super(Foot,self).preBuild()

    def build(self):
        super(Foot,self).build()
        #get rid of this!
        cmds.delete( self.footJntUpv.getZeroGroup1() )

        #duplicate ball joint
        self.ankle1.create()
        self.ankle1.setPosition ( self.ball.getPosition() )
        #make it a little bigger
        cmds.setAttr("{0}.radius".format(self.ankle1.getName()), 2)
        self.ankle1.setParent( self.heel.getName() )

        #rename and move the bind joints to jointgrp
        self.ankle.setName( self.ankle.getName().replace(nameSpace.JOINT, nameSpace.BINDJOINT) )
        self.ball.setName( self.ball.getName().replace(nameSpace.JOINT, nameSpace.BINDJOINT) )
        self.tipToe.setName( self.tipToe.getName().replace(nameSpace.JOINT, nameSpace.BINDJOINT) )



        #duplicate the bind joints and we'll use them for the ctrl rig
        self.ballJntRig = joint.Joint( self.ball.getName().replace(nameSpace.JOINT, nameSpace.DRVJOINT),
                                           position=self.ball.getPosition(),
                                           parent=self.heel.getName)
        self.toeJntRig = joint.Joint( self.tipToe.getName().replace(nameSpace.JOINT, nameSpace.DRVJOINT),
                                          position=self.tipToe.getPosition(),
                                          parent=self.ballJntRig.getName())
        self.ankleJntRig = joint.Joint( self.ankle.getName().replace(nameSpace.JOINT, nameSpace.DRVJOINT),
                                            position=self.ankle.getPosition(),
                                            parent=self.ankle1.getName())

        self.ballJntRig.create()
        self.toeJntRig.create()
        cmds.select(cl=True)
        self.ankleJntRig.create()
        self.ankleJntRig.setParent( self.ankle1.getName() )

        #parent accordingly


        #first remove parent on pivots
        cmds.parent(self.inPivot.getName() ,w=True)
        cmds.parent(self.outPivot.getName() ,w=True)

        cmds.select(cl=True)


        #ikh names
        self.toeIkh = self.tipToe.getName().replace(nameSpace.BINDJOINT, nameSpace.IK)
        self.ankleIkh = self.ankle1.getName().replace(nameSpace.JOINT, nameSpace.IK)
        #ikh applications
        cmds.ikHandle( sj=self.ballJntRig.getName(), ee=self.toeJntRig.getName(), sol="ikSCsolver", n=self.toeIkh )
        cmds.ikHandle( sj=self.ankle1.getName(), ee=self.ankleJntRig.getName(), sol="ikSCsolver", n=self.ankleIkh )

        #create sdk nodes
        tipToeSdk = cmds.createNode('transform', n=self.tipToe.getName().replace( nameSpace.BINDJOINT, 'sdk' ))
        ankleSdk = cmds.createNode('transform', n=self.ankle.getName().replace( nameSpace.BINDJOINT, 'sdk' ))

        #pointConstraint ball to ankle1jnt
        #cmds.pointConstraint( self.ballJntRig.getName(), self.ankle1.getName())

        #snap
        self.snap( self.ball.getName(), tipToeSdk )
        self.snap( self.ankle1.getName(), ankleSdk)

        #create ikh ctrls
        self.toeCtrl = control.Control( self.tipToe.getName().replace(nameSpace.BINDJOINT, nameSpace.CONTROL),
                                              position=self.tipToe.getPosition(),
                                              parent=tipToeSdk,
                                              shape = "circle" )
        self.ankleCtrl = control.Control( self.ankle.getName().replace(nameSpace.BINDJOINT, nameSpace.CONTROL),
                                              position=self.ankle.getPosition(),
                                              parent=ankleSdk,
                                              shape = "circle" )

        self.ankleCtrl.create()
        self.toeCtrl.create()
        self.toeCtrl.setColor(7)
        self.toeCtrl.setOrientation( 'z' )

        #parent ik handles to ctrls
        cmds.parent( self.toeIkh, self.toeCtrl.getName() )
        cmds.parent( self.ankleIkh, self.ankleCtrl.getName() )


        #replace pivot joints with locators
        self.inPivotLocator = locator.Locator( name="{0}_{1}".format( self.inPivot.getName(), nameSpace.LOCATOR ))
        self.outPivotLocator = locator.Locator( name="{0}_{1}".format( self.outPivot.getName(), nameSpace.LOCATOR ))

        self.inPivotLocator.create()
        self.outPivotLocator.create()

        #snap!
        self.snap( self.inPivot.getName(), self.inPivotLocator.getName())
        self.snap( self.outPivot.getName(), self.outPivotLocator.getName())
        #delete the joints.
        cmds.delete( self.inPivot.getName())
        cmds.delete( self.outPivot.getName())

        #now implement the hierarchy
        cmds.parent( self.outPivotLocator.getName(),self.inPivotLocator.getName())
        cmds.parent( self.heel.getName(), self.outPivotLocator.getName())
        cmds.parent( tipToeSdk, ankleSdk, self.heel.getName() )

        #create foot control
        self.footCtrl = control.Control( name="{0}_{1}".format( self.getName(), nameSpace.CONTROL),
                                             position = self.ankle.getPosition(),
                                             parent = self.controlsGroup,
                                             shape = 'square')
        self.footCtrl.create()
        cmds.parent(self.inPivotLocator.getName(), self.footCtrl.getName())
        self.footCtrl.setColor(7)
        #add attributes
        cmds.select(self.footCtrl.getName())
        cmds.addAttr( ln="footRoll", at="float", max=45, min=-45, k=True)
        cmds.addAttr( ln="toeBend", at="float", max=45, min=-45, k=True)
        cmds.addAttr( ln="tilt", at="float", max=45, min=-45, k=True)

    #set driven keys
        footRoll = ("{0}.footRoll".format( self.footCtrl.getName() ))
        toeBend = ("{0}.toeBend".format( self.footCtrl.getName() ))
        tilt = ("{0}.tilt".format( self.footCtrl.getName() ))
        #foot roll
        
        '''
        #ball footRoll
        animSdk.setDrivenKey(footRoll, 0, "{0}.rx".format(ankleSdk), 0)
        animSdk.setDrivenKey(footRoll, 45, "{0}.rx".format(ankleSdk), 90)
        #heel footRoll
        animSdk.setDrivenKey(footRoll, 0, "{0}.rx".format(self.heel.getName()), 0)
        animSdk.setDrivenKey(footRoll, -45, "{0}.rx".format(self.heel.getName()), -90)
        #toe bend
        animSdk.setDrivenKey(toeBend, 0, "{0}.rx".format(tipToeSdk), 0)
        animSdk.setDrivenKey(toeBend, 45, "{0}.rx".format(tipToeSdk), 90)
        animSdk.setDrivenKey(toeBend, -45, "{0}.rx".format(tipToeSdk), -90)
        #tilt
        if self.getSide() == nameSpace.SIDES["left"]:
            animSdk.setDrivenKey(tilt, 0, "{0}.rz".format(self.inPivotLocator.getName()), 0)
            animSdk.setDrivenKey(tilt, 45, "{0}.rz".format(self.inPivotLocator.getName()), 90)
            animSdk.setDrivenKey(tilt, 0, "{0}.rz".format(self.outPivotLocator.getName()), 0)
            animSdk.setDrivenKey(tilt, -45, "{0}.rz".format(self.outPivotLocator.getName()), -90)
        else:
            animSdk.setDrivenKey(tilt, 0, "{0}.rz".format(self.inPivotLocator.getName()), 0)
            animSdk.setDrivenKey(tilt, 45, "{0}.rz".format(self.inPivotLocator.getName()), -90)
            animSdk.setDrivenKey(tilt, 0, "{0}.rz".format(self.outPivotLocator.getName()), 0)
            animSdk.setDrivenKey(tilt, -45, "{0}.rz".format(self.outPivotLocator.getName()), 90)
        '''
        
        #delete the unessecaries
        cmds.delete( self.noXformGroup, self.hookGroup )



    def postBuild(self):
        super(Foot,self).postBuild()







