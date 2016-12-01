'''
Ribbon Class
'''

import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import wrappers
import follicle
from autorigger.util import buildSingle
reload(nameSpace)
reload(control)
reload(joint)
reload(wrappers)

'''
reload (nameSpace)
reload (control)
reload (joint)
reload (wrappers)
'''

def superRibbon(name, cvs):

    # the surface should already be created.
    # All you have to do is select the CV's
    result = []
    for i,cv in enumerate(cvs):
        thisName = name+str(i+1)
        fol = follicle.createFollicle(cv, thisName)
        #buildControls with buildSingle
        bs = buildSingle.buildSingle(thisName)
        cmds.delete(cmds.parentConstraint(fol, bs['master']))
        cmds.parent(bs['master'], fol)

        bs["fol"] = fol
        result.append(bs)
    return result


#3 control set up ribbon
class Ribbon(object):

    def __init__(self,name,jointAmmount=3,startPosition=(0,0,0),endPosition=(0,5,0) ):
        self._name = name
        self.jointAmmount = jointAmmount
        self.startPosition = startPosition
        self.endPosition= endPosition
        self.follicles = list()

        self.nameSpace = ("{0}Ribbon".format(self.getName()))
        self.middle = ( (int(self.jointAmmount) /2) + 1 )
        self.middleList = ( int(self.jointAmmount) /2 )
        self.middleCount = ( int(self.jointAmmount) - 2 )

        self.ribbonCtrls = list()
        self.ribbonJnts = list()
        self.ribbonUpvs = list()
        self.ribbonZeros = list()
        self.ribbonLocs = list()
    def getName(self):
        return self._name

    def getJointAmmount(self):
        return self.jointAmmount

    def getStartPosition(self):
        return self.startPosision

    def getEndPositoin(self):
        return self.getEndPosition

    def setStartPosition(self,value):
        self.startPosition = value
        cmds.xform(self.name, ws=True,t=self.startPosition)

    def setEndPosition(self,value):
        self.endPosition = value
        cmds.xform(self.name, ws=True,t=self.endPosition)

    def getStartCtrl(self):
        return self.ribbonCtrls[0]

    def getStartZeroGroup(self):
        return self.ribbonZeros[0]

    def getMidCtrl(self):
        pass
        #it's called when created

    def getMidZeroGroup(self):
        pass
        #it's called when created

    def getEndCtrl(self):
        return self.ribbonCtrls[-1]

    def getEndZeroGroup(self):
        return self.ribbonZeros[-1]

    def getMasterGroup(self):
        return self.masterGrp

    def getStartJoint(self):
        return self.ribbonJnts[0]

    def getEndJoint(self):
        return self.ribbonJnts[-1]

    def getMidLoc(self):
        return self.midLoc.getName()

    def getPlane(self):
        return self.plane[0]

    def getFollicle(self, index):
        return self.follicles[index]

#-----------------------------------------------
# SET UP DEF
#-----------------------------------------------
    def setup(self):

    #handle which direction UPV will be in
        x = 5
        y = 0
        z = 0
    #control and grp frz creation

    #organize and place into groups
        #ctrlGroup
        self.ctrlGrp = cmds.createNode("transform", n="{0}_ctrl_grp".format(self.getName()))
        #Master Group
        self.masterGrp = cmds.createNode("transform", n = "{0}_rbn_grp".format(self.getName()))

        for i in range(int(self.jointAmmount)):

            inc = i + 1
            #check if it's the MID!!!
            if i == self.middleList:
                #ctrl creation
                midCtrl = control.Control("{0}_ctrl{1}".format(self.nameSpace,inc),(0,i,0),shape="star")
                midCtrl.create()
                midCtrl.setColor(17)
                self.ribbonCtrls.append(midCtrl.getName())
                #joint creation
                midJnt = joint.Joint("{0}_{1}{2}".format(self.nameSpace,nameSpace.JOINT,inc),(0,i,0),parent=midCtrl.getName())
                midJnt.create()
                self.ribbonJnts.append(midJnt.getName())
                #midJnt.setPosition([0,i,0])
                #upv creation
                upvCtrl = control.Control("{0}_{1}{2}".format(self.nameSpace,nameSpace.UPV,inc),(0,i,0),shape="cross")
                upvCtrl.create()
                self.ribbonUpvs.append(upvCtrl.getName())
                cmds.select(upvCtrl.getZeroGroup1())
                cmds.move(x,y,z, r=True)
                cmds.parent(upvCtrl.getZeroGroup1(), self.masterGrp)
                #hide upvector. Animators don't need to see it!
                cmds.setAttr("{0}.visibility".format(upvCtrl.getName()), 0)

                self.ribbonZeros.append(midCtrl.getZeroGroup1())
                self.getMidCtrl = midCtrl.getName()
                self.getMidZeroGroup = midCtrl.getZeroGroup1()

                cmds.parent (midCtrl.getZeroGroup1(), self.ctrlGrp)

                #midLocator
                self.midLoc = control.Control("{0}_midpoint".format(self.nameSpace),(0,i,0),shape="cross")
                self.midLoc.create()
                #hide it
                cmds.setAttr("{0}.visibility".format(self.midLoc.getName()), 0)


            else:
                #ctrl creation
                ribbonCtrl = control.Control("{0}_ctrl{1}".format(self.nameSpace,inc),(0,i,0),shape = "square")
                ribbonCtrl.create()
                self.ribbonCtrls.append(ribbonCtrl.getName())
                #loc creation
                ribbonLoc = cmds.spaceLocator(n="{0}_loc{1}".format(self.nameSpace,inc))
                cmds.parent(ribbonLoc[0],ribbonCtrl.getName())
                self.ribbonLocs.append(ribbonLoc[0])
                cmds.setAttr ("{0}.ty".format(ribbonLoc[0]), 0)
                #hide it
                cmds.setAttr("{0}.visibility".format(ribbonLoc[0]), 0 )
                #joint creation
                ribbonJnt = joint.Joint("{0}_{1}{2}".format(self.nameSpace,nameSpace.JOINT,inc),(0,i,0),parent=ribbonCtrl.getName())
                ribbonJnt.create()
                self.ribbonJnts.append(ribbonJnt.getName())
                #upv creation
                upvCtrl = control.Control("{0}_{1}{2}".format(self.nameSpace,nameSpace.UPV,inc),(0,i,0),shape="cross")
                upvCtrl.create()
                self.ribbonUpvs.append(upvCtrl.getName())
                cmds.parent(upvCtrl.getZeroGroup1(),ribbonCtrl.getName())
                cmds.select(upvCtrl.getZeroGroup1())
                cmds.move(x,y,z, r=True)

                #hide upvector. Animators don't need to see it!
                cmds.setAttr("{0}.visibility".format(upvCtrl.getName()), 0)

                self.ribbonZeros.append(ribbonCtrl.getZeroGroup1())

                cmds.parent (ribbonCtrl.getZeroGroup1(), self.ctrlGrp)

                #orientControls. ribbons are default set to z-downaxis
                ribbonCtrl.setOrientation('z')
                #make them a little smaller too
                cmds.select("{0}.cv[*]".format(ribbonCtrl.getName()))
                cmds.scale(0.6,0.6,0.6,r=True)


        #aim contraint startLoc to midCtrl
        cmds.aimConstraint(self.ribbonCtrls[1],self.ribbonLocs[0],mo=True,
                           wut="object",
                           wuo=self.ribbonUpvs[0])

        #aim constraint endLoc to midCtrl
        cmds.aimConstraint(self.ribbonCtrls[1],self.ribbonLocs[-1],mo=True,
                           wut="object",
                           wuo=self.ribbonUpvs[-1])

        #parentConstraint start and end ctrls to midloc
        cmds.parentConstraint(self.ribbonCtrls[0],self.ribbonCtrls[-1],self.midLoc.getName())

        #pointConstraint midZeroGrp to midLoc
        cmds.pointConstraint(self.midLoc.getName(), self.ribbonZeros[1])

        #aim midZero to startCtrl
        cmds.aimConstraint(self.ribbonCtrls[-1],self.ribbonZeros[1],
                           wut="object",
                           wuo=self.ribbonUpvs[1],
                           mo=True)
        #parentConstraint startUpv and endUpv to midUpv
        cmds.parentConstraint (self.ribbonUpvs[-1],self.ribbonUpvs[0],self.ribbonUpvs[1])








    def createFollicle(self, planeShape, name, parameterV=0.5):

        #create follicle node
        self.follicle = cmds.createNode ('follicle', n=("{0}_folShape{1}".format( self.nameSpace,name )))
        cmds.pickWalk(d="Up")
        self.follicleTransform = cmds.ls(sl=True)

        #connect nurbs shape to follicle shape
        cmds.connectAttr( ("{0}.local".format(planeShape)), ("{0}.inputSurface".format(self.follicle)), f=True)
        cmds.connectAttr( ("{0}.worldMatrix[0]".format(planeShape)), ("{0}.inputWorldMatrix".format(self.follicle)), f=True )

        cmds.connectAttr( ("{0}.outRotate".format(self.follicle)), ("{0}.rotate".format(self.follicleTransform[0])), f=True )
        cmds.connectAttr( ("{0}.outTranslate".format(self.follicle)), ("{0}.translate".format(self.follicleTransform[0])), f=True )

        #setAttr on U and V parameters
        cmds.setAttr ("{0}.parameterU".format(self.follicleTransform[0]), 0.5)
        cmds.setAttr ("{0}.parameterV".format(self.follicleTransform[0]), parameterV)
        cmds.setAttr("{0}.visibility".format(self.follicle), 0)

        return self.follicleTransform

#build will connect the follicle def and create def
    def build(self):
        #create the ribbon rig
        self.setup()

        #create the plane
        self.plane = cmds.nurbsPlane(n=("{0}_surf".format(self.nameSpace)),u=1,v=3,w=1,lr=float(self.jointAmmount)-1)
        cmds.move(0,self.middleList,0)
        cmds.rotate(0,90,0)
        cmds.makeIdentity( apply=True )
        self.planeShape = cmds.listRelatives(self.plane,s=True)
        #cmds.delete(constructionHistory=True)

        #create 3 follicles
        self.follicles.append( self.createFollicle( self.planeShape[0], "lo", parameterV=0.175 ) )
        self.follicles.append( self.createFollicle( self.planeShape[0], "mid", parameterV=0.5 ) )
        self.follicles.append( self.createFollicle( self.planeShape[0], "up", parameterV=0.825 ) )
        self.follicles.append( self.createFollicle( self.planeShape[0], "end", parameterV=1 ) )



        #skin the plane
        cmds.skinCluster( self.ribbonJnts[0],
                          self.ribbonJnts[1],
                          self.ribbonJnts[-1],
                          self.plane[0],
                          dr=3,
                          mi=2,

                          sw=1)

        #parentConstraint follicle over midCtrl
        #cmds.parentConstraint( self.follicleTransform, self.getMidZeroGroup, mo=True )
        cmds.parent ( self.plane[0], self.masterGrp)

        #parent follicle
        #group follicles
        folGrp = cmds.createNode('transform', n=('grpFol_{0}').format(self.nameSpace))
        cmds.parent( self.follicles[0], self.follicles[1], self.follicles[2], self.follicles[3], folGrp)
        cmds.parent ( folGrp, self.masterGrp)

        #parent all Groups under master
        cmds.parent ( self.ctrlGrp, self.masterGrp )
        cmds.parent ( self.midLoc.getZeroGroup1(), self.masterGrp)





