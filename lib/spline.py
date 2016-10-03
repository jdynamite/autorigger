'''

Spline Class

-----------------
This spline class will duplicate a joint chain and apply a spline IKH to the newly duplicated joint.
So as of right now, you'll need to have a joint chain created in order to use run this module properly.
This shouldn't be a problem since we're using this module as an addition to part rigs such as limb, spline, and neck.
(possibly even tails in the future!)

'''

import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import locator

reload(nameSpace)
reload(control)
reload(joint)
reload(locator)



class Spline(object) :

    def __init__( self, name, startJointDupe, endJointDupe, jointAmmount=7,
                  controlAmmount=3 ):

        '''
        :param name: name of spline
        :param startJointDupe: name of the first joint in the joint chain to be duplicated
        :param endJointDupe: name of the last joint in the joint chain to be duplicated
        :param jointAmmount: ammount of joints in the 'to be duplicated' joint chain
        :param controlAmmount: ammount of controls you'd like. Default is 3
        '''



        self.name = name
        self.jointAmmount = jointAmmount
        self.controlAmmount = controlAmmount
        self.startJointDupe = startJointDupe
        self.endJointDupe = endJointDupe

        self.jointList = list()
        self.curve = "{0}_curveIk".format( self.name )

    # doing this little custom thing so that
    # we can get the mdn that stretches to plug in the global scale
    def getMdn(self):
        return self.mdn

    def getStartCtrl(self):
        return self.startCtrl.getName()

    def getMidCtrl(self):
        return self.midCtrl.getName()

    def getEndCtrl(self):
        return self.endCtrl.getName()

    def getStartCtrlZero(self):
        return self.startCtrl.getNull()

    def getMidCtrlZero(self):
        return self.midCtrl.getNull()

    def getEndCtrlZero(self):
        return self.endCtrl.getNull()

    def getSplineIk(self):
        return self.ik

    def getSplineCurve(self):
        return self.curve

    def getJoint(self):
        return self.jointList

    def setWorldUpObjectStart(self, influence):
        cmds.connectAttr( "{0}.worldMatrix[0]".format(influence), '{0}.dWorldUpMatrix'.format( self.getSplineIk() ) )

    def setWorldUpObjectEnd(self, influence):
        cmds.connectAttr( "{0}.worldMatrix[0]".format(influence), '{0}.dWorldUpMatrixEnd'.format(self.getSplineIk() ) )

    def setup(self):

        #create a 2 joint chain so that we have them pointing correctly
        #duplicate start joint
        startJoint = cmds.duplicate( self.startJointDupe, po=True, n='startJoint' )[0]
        startJointPosition = cmds.xform( startJoint, q=True, ws=True, t=True )


        endJoint = cmds.duplicate( self.endJointDupe, po=True, n='endJoint' )[0]
        endJointPosition = cmds.xform( endJoint, q=True, ws=True, t=True )

        cmds.parent(endJoint, startJoint)


        #create joint chain
        for i in range( 0, self.jointAmmount ):
            jointNum = i+1
            self.jointList.append(
                cmds.duplicate(
                    startJoint,
                    n= '{0}_{1}{2}'.format( self.name, nameSpace.SPLINE, str(jointNum) ),
                    po=True
                )[0]
            )

            #place them accordingly
            #get tx attr
            totalDist = cmds.getAttr( '{0}.tx'.format( endJoint ))
            iteration = totalDist/ (self.jointAmmount-1)
            cmds.setAttr('{0}.radius'.format(self.jointList[i]), 2.25)
            if i>0:
                cmds.parent( self.jointList[i], self.jointList[i-1] )
                cmds.setAttr( '{0}.tx'.format(self.jointList[i]), iteration)
                cmds.setAttr( '{0}.ty'.format(self.jointList[i]), 0)
                cmds.setAttr( '{0}.tz'.format(self.jointList[i]), 0)


        #determine joint chain down axis will always be x


        #create curve
        loc = cmds.spaceLocator(n='inbetweenSpaceLoc')[0]
        cmds.parentConstraint( startJoint, endJoint, loc )
        halfway = cmds.getAttr('{0}.translate'.format(loc))

        points = [

            startJointPosition,
            cmds.xform( loc, q=1, ws=1, t=1),
            endJointPosition

        ]

        print 'Start of curve created at: {0}'.format( str(startJointPosition) )
        print 'End of curve created at: {0}'.format( str(endJointPosition) )

        cmds.curve(ep=points, d=3, n=self.curve )

        #delete the start and end joints, we don't need them anymore
        cmds.delete( startJoint, endJoint )
        #delete the loc
        cmds.delete(loc)

        #Create the spline IKH
        self.ik = cmds.ikHandle( sol="ikSplineSolver",
                            sj=self.jointList[0],
                            ee=self.jointList[-1],
                            ccv = False,
                            c = self.curve,
                            n ="{0}_splineIk".format(self.name) )[0]
        cmds.setAttr('{0}.dTwistControlEnable'.format(self.ik), 1 )
        cmds.setAttr('{0}.dWorldUpType'.format(self.ik), 4 )
        cmds.setAttr('{0}.v'.format(self.ik), 0 )

    #add stretch to joints
        #create curveInfo node
        cmds.select( self.curve )
        arc = cmds.arclen( ch=True )
        arclen = '{0}_arcLength'.format(self.name)
        cmds.rename( arc, arclen )

        #create mdn
        mdn = cmds.createNode( 'multiplyDivide', n='{0}_mdn'.format(self.name) )
        #set mdn to divide
        cmds.setAttr('{0}.operation'.format(mdn), 2)
        #connect curveInfo.arcLength to mdn.input1X and mdn.input2X
        cmds.connectAttr( '{0}.arcLength'.format(arclen), '{0}.input1X'.format(mdn) )
        #query distance
        dist = cmds.getAttr( '{0}.arcLength'.format(arclen) )
        #set distance to input2
        cmds.setAttr( '{0}.input2X'.format(mdn), dist )

        #connect to all joints
        for jnt in self.jointList:

            cmds.connectAttr( '{0}.outputX'.format(mdn), '{0}.sx'.format(jnt) )

        self.mdn = mdn

    # create the control rig setup
    def buildControls(self):


        self.startCtrl = control.Control( 
            "{0}_start_{1}{2}".format(self.name, nameSpace.SPLINE, nameSpace.CONTROL),
            position = cmds.xform( self.jointList[0], q=1, ws=1, t=1),
            shape='cross'
        )
        
        self.startAim = locator.Locator( 
            "{0}_start_{1}".format(self.name, nameSpace.LOCATOR))

        self.midCtrl = control.Control( 
            "{0}_mid_{1}{2}".format(self.name, nameSpace.SPLINE, nameSpace.CONTROL),
             shape='star'
        )

        self.endCtrl = control.Control( 
            "{0}_end_{1}{2}".format(self.name, nameSpace.SPLINE, nameSpace.CONTROL),
             position = cmds.xform( self.jointList[-1], q=1, ws=1, t=1),
             shape='cross')
        
        self.endAim = locator.Locator( "{0}_end_{1}".format(self.name, nameSpace.LOCATOR))

    #start control
        self.startCtrl.create()

        self.startAim.create()
        self.startAim.setParent( self.startCtrl.getName() )
        #snap..
        self.startAim.setPosition( cmds.xform( self.jointList[0], q=1, ws=1, t=1) )


    #mid control
        self.midCtrl.create()
        self.midCtrl.setOrientation('x')
    #end control
        self.endCtrl.create()
        self.endAim.create()
        self.endAim.setParent( self.endCtrl.getName() )
        #snap..
        self.endAim.setPosition( cmds.xform( self.jointList[-1], q=1, ws=1, t=1) )

        #pointConstrain start and end to mid
        cmds.pointConstraint( self.startCtrl.getName(), self.endCtrl.getName(), self.midCtrl.getNull() )
        #aim mid to end ZeroGroup1

        #cmds.aimConstraint( self.endCtrl.getName(), self.midCtrl.getNull(),
        #                    aim = [1,0,0], u = [0,1,0], wut = 'objectrotation', wuo= self.startCtrl.getName() )

    #aim the start and end locators to mid
        cmds.aimConstraint( self.midCtrl.getName(), self.startAim.getName(),
                            aim = [1,0,0], u = [0,1,0], wut = 'objectrotation', wuo= self.startCtrl.getNull() )
        cmds.aimConstraint( self.midCtrl.getName(), self.endAim.getName(),
                            aim = [-1,0,0], u = [0,1,0], wut = 'objectrotation', wuo= self.endCtrl.getNull() )
    #clusters...
        #startClusters
        cmds.select( '{0}.cv[0:1]'.format(self.getSplineCurve()) )
        startCls = cmds.cluster(envelope=True, n='{0}_startCls'.format(self.name) )

        #midClusters
        cmds.select( '{0}.cv[2]'.format(self.getSplineCurve()) )
        midCls = cmds.cluster(envelope=True, n='{0}_midCls'.format(self.name) )

        #endClusters
        cmds.select( '{0}.cv[3:4]'.format(self.getSplineCurve()) )
        endCls = cmds.cluster(envelope=True, n='{0}_endCls'.format(self.name) )

    #parent those clusters!
        cmds.parent( startCls, self.startAim.getName() )
        cmds.parent( midCls, self.midCtrl.getName() )
        cmds.parent( endCls, self.endAim.getName() )

        #hide clusters
        cmds.setAttr( '{0}.v'.format(startCls[1]), 0 )
        cmds.setAttr( '{0}.v'.format(midCls[1]), 0 )
        cmds.setAttr( '{0}.v'.format(endCls[1]), 0 )




