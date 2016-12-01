'''
Writing rig modules with this autorigger

Class: Test

I will be going over things you should know when writing rig modules. Most of this pertains to stuff inherited in
part.


-Setup: Creates joints, guides and groups for hierarchy purposes. The guides will be positioned in modules that are inheriting from Part
        ie: Limb, Foot, Spine, etc

        Each group has it's own variable that can be called

            self.group: master group. The top node
            self.jointsGroup: the joints group.
            self.controlsGroup: controls group
            self.noXformGroup: parts of rig that should not xform with parent
            self.hookGroup: the parts of the rig that need a 'hook' will go here

-Build: build off positioned joints. This is where most of your coding will go.

Notable procs:

Notable variables:
self.joints: list of joints
self.guides: list of guides
self.placeGuides: places guides in .setup() according to positions input. part.setup() will create your joints and guides,
                  but it's up to you to position them.

'''


import maya.cmds as cmds

# It is really important that you import part,
# because we'll be inheriting most of our toys from there.
import part

# Define your class
class Test(part.Part):
    def __init__(self, name, positions=([5, 5, 0], [7.5, 5, -3], [11, 5, 0]), jointAmmount=3, mirror=True):
        super(Test, self).__init__(name)
        '''
        name: name of the rig
        position: list of each joint position. Ammount of positions must match jointAmmount
        jointAmmount: ammount of joints to be created.
        mirror: Mirror? self explanatory

        NOTE: This setup only works with single chain hierarchys. Won't be able to create forked joint chains just yet.
              With that in mind, each of our modules/setups should be made for each chain. Think fingers, each finger will have it's
              own call and then hooked up to hand.
        '''
        self.positions = positions
        # do you want it to mirror?
        self.mirror = mirror

        '''
        IMPORTANT:
        it's also a good practice to declare you up and down axises here in the init
        '''
        # like this
        self.downAxis='x'
        self.upAxis='y'


    def setup(self):
        super(Test, self).setup()
        '''
        *Use the command: self.placeGuides(self.positions) * to place your joints.
        It takes in a list of positional data, such as self.positions.

        part.Part.setup() will already create the joints and guides to be positioned.
        So the only thing you'll have to do here is to position those guides.

        note that masterGuide will be moved instead of the first guide in hierarchy
        '''


        self.placeGuides(self.positions)

        '''
        use self.setPositionUPVS() to position all UPVs relative to their parent(the guide)
        '''
        self.setPositionUPVS([0,0,5])

        '''
        Also, you can edit your up axis and down axis
        '''
        self.downAxis('x')
        self.upAxis('-y')


    def postSetup(self):
        super(Test, self).postSetup()
        # before you delete the master guide, query the down axis
        # get what you want from him, then kill him! Bwuahahaha
        self.strAimAttr = (
            cmds.getAttr("{0}.aim".format(self.masterGuide.getName()), asString=True)
        )
        # remove the - if there is one
        if (len(self.strAimAttr)):
            self.downAxis = self.strAimAttr[-1]
        else:
            self.downAxis = self.strAimAttr

    def preBuild(self):
        super(Test, self).preBuild()

        '''
        preBuild() will delete some of the setup data and create new groups to build.
        '''


    def build(self):
        super(Test, self).build()

        '''
        This is where all the coding will go.
        Make sure to parent them to their respective groups.

        Controls go under self.controlsGroup, etc
        '''

    def postBuild(self):
        super(Test, self).postBuild()

        if cmds.objExists(self.ikfkSystem.getHandle()):
            cmds.setAttr("{0}.v".format(self.ikfkSystem.getHandle()), 0)

        for jnt in self.ikfkSystem.getBlendJoints():
            cmds.setAttr("{0}.visibility".format(jnt), 1)

        # delete bind joints
        cmds.delete(self.startJoint.getName())

