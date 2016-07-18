import maya.cmds as cmds
from autorigger.lib import mayaBaseObject
from autorigger.lib import jsonData
from autorigger.lib import controlFilePath
from autorigger.lib import curve as animCurve
from autorigger.lib import nameSpace
from autorigger.lib.util import Switch

reload(mayaBaseObject)


class Control(mayaBaseObject.MayaBaseObject):
    """
    control class comprises of one control, and 1-2 null groups above
    if control name already exists, it will self populate the attrs


    update: sanitize_name and format_name now in mayaBaseClass -dan

    """

    def __init__(self, name=None, align_to="world", shape="circle", nameType=namespace.CONTROL):
        super(Control, self).__init__(name=name, nameType=nameType)

        self.color = "yellow"
        self.shape = shape
        self.align_to = align_to

        if not self.name.endswith(nameSpace.DELIMITER + self.nameType):
            self.name += nameSpace.DELIMITER + self.nameType

    @classmethod
    def bulkCreate(cls, *args):
        # returns the input as instances of the class
        # list[jnt1, jnt2, jnt3] -> list[con(jnt1), con(jnt2), con(jnt3)]
        # string -> con(string)

        result = []
        for arg in args:
            if type(arg) in [list, tuple]:
                objects = [Control(name=obj) for obj in arg]
                filter(lambda o: result.append(o), objects)
            elif type(arg) == basestring:
                result.append(Control(name=obj))
        return result

    @classmethod
    def setColors(cls, objects, color):
        if type(objects) not in [list, tuple]:
            return
        for o in objects:
            if isinstance(o, Control):
                o.set_color(color)

    @classmethod
    def setShapes(cls, objects, shape):
        if type(objects) not in [list, tuple]:
            return
        for o in objects:
            if isinstance(o, Control):
                o.set_shape(shape)

    def getNull(self):
        return self.null

    def pop_control_attributes(self):
        self.align_to = cmds.getAttr("%s.align_to" % self.name)
        self.side = cmds.getAttr("%s.side" % self.name)
        self.color = cmds.getAttr("%s.color" % self.name)

    def create(self):
        self.name = cmds.createNode("transform", n=self.name)
        self.set_shape(self.shape)

        if cmds.objExists(self.align_to):
            cmds.delete(cmds.parentConstraint(
                self.align_to, self.name, mo=False))

        # add some non-keyable attributes to the control
        attrs = {'side': self.side, 'alingTo': self.align_to,
                 'color': self.color, 'isControl': 'y'}

        for attr, value in attrs.iteritems():
            cmds.addAttr(self.name, ln=attr, dt='string', k=False)
            cmds.setAttr(".".join([self.name, attr]),
                         value, type='string')

        self.zero()

    def set_color(self, color):
        color_map = {"red": 13, "yellow": 17, "blue": 6}

        shapes = cmds.listRelatives(self.name, c=True) or []

        for shape in shapes:
            cmds.setAttr("%s.overrideEnabled" % shape, 1)
            if color in color_map:
                cmds.setAttr("%s.overrideColor" % shape, color_map[color])

    def set_shape(self, shape):

        for case in Switch(shape):
            if case('circle'):
                circle = cmds.circle(ch=False)[0]
                self.get_shape_from(circle)
                cmds.delete(circle)
                break

            else:
                # call from prebuilt control shapes saved out to a file
                controlDict = jsonData.load(controlFilePath.controlFilePath())
                for shape in controlDict[self.shape]["shapes"]:
                    positions = controlDict[self.shape][
                        "shapes"][shape]["positions"]
                    degree = controlDict[self.shape]["shapes"][shape]["degree"]
                    # color = controlDict[self.shape]["shapes"][shape]["color"]
                    curve = animCurve.createFromPoints(
                        positions, degree, self.name)

                    self.get_shape_from(curve)
                    cmds.delete(curve)

    def mirror(self):
        # look for a mirror control object on the other side

        sideLower = self.side.lower()
        otherSide = ""
        align_to = ""

        mirror_map_left = {"left": "right", "lf": "rt", "l": "r"}
        mirror_map_right = {"right": "left", "rt": "lf", "r": "l"}

        if sideLower in mirror_map_left.keys():
            otherSide = list(mirror_map_left[sideLower])

        elif sideLower in mirror_map_right.keys():
            otherSide = list(mirror_map_right[sideLower])

        for i, char in enumerate(self.side):
            if char.isupper():
                otherSide[i] = otherSide[i].upper()

        if not len(otherSide):
            raise RuntimeError("Could not find opposite side.")

        otherSide = "".join(otherSide)

        if cmds.objExists(self.align_to):
            align_to = self.align_to.replace(self.side, otherSide)
        else:
            align_to = "world"

        newName = self.name.replace(self.side, otherSide)

        # otherwise, create new control aligned to align_to
        # with same specs as self but different color

        mirrored = Control(newName, align_to, self.shape)

        return mirrored

    def set_to_origin(self):

        # pop control to world origin
        target = ''

        if hasattr(self, 'zero') and cmds.objExists(self.zero):
            target = self.zero
        elif hasattr(self, 'null') and cmds.objExists(self.null):
            target = self.null
        else:
            target = self.name

        cmds.xform(target, cp=True)
        temp_grp = cmds.group(em=True, n='temp_grp_1')
        cmds.delete(cmds.pointConstraint(temp_grp, target))
        cmds.delete(temp_grp)

    def get_shape_from(self, obj):

        obj = cmds.duplicate(obj, rc=True)

        cmds.parent(obj, self.name)
        cmds.makeIdentity(obj, apply=True, t=1, s=1, r=1)
        obj_shapes = cmds.listRelatives(obj, s=True)

        for shape in obj_shapes:
            cmds.parent(shape, self.name, r=True, s=True)
            cmds.rename(shape, "%sShape" % self.name)

        self.set_color(self.color)
        cmds.delete(obj)

    def drive_constrained(self, obj, p=False, r=False, s=False, o=False):
        if not cmds.objExists(obj):
            return
        if s:
            cmds.scaleConstraint(self.name, obj, mo=o)

        if p and r:
            cmds.parentConstraint(self.name, obj, mo=o)

        elif p and not r:
            cmds.pointConstraint(self.name, obj, mo=o)

        elif r and not p:
            cmds.orientConstraint(self.name, obj, mo=o)

    def drive_parented(self, obj):
        if cmds.objExists(obj):
            cmds.parent(obj, self.name)


class Guide(Control):
    def __init__(self, name, position=(0, 0, 0), parent=None):
        super(Guide, self).__init__(name, position, parent)
        self.position = position
        self.parent = parent

    def create(self):
        ctrlName = self.name
        guideShape = cmds.createNode("implicitSphere")
        cmds.rename(cmds.listRelatives(guideShape, p=True), ctrlName)

        # create guide nulls
        null = cmds.createNode("transform", n=ctrlName + "_NULL")
        cmds.parent(ctrlName, null)

        # position null
        self.setPosition(self.position)
        # cmds.xform(null, ws=True, t=self.position)

        print 'parent is {0}'.format(self.parent)

        # insert into hierarchy accordingly
        if self.getParent():
            cmds.parent(null, self.getParent())
