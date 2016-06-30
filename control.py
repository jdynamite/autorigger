import maya.cmds as cmds
from rig import switch


class Control:
    """
    control class comprises of one control, and 1-2 null groups above
    if control name already exists, it will self populate the attrs
    """

    def __init__(self, name=None, side=None, align_to=None, shape=None):

        self.side_formats = ["l", "lf", "l", "left", "r", "rt", "right"]

        self.name = name
        self.sanitize_name()

        self.color = "yellow"

        if side is None:
            side = ""
        self.side = side

        if align_to is None:
            align_to = "world"
        self.align_to = align_to

        if shape is None:
            shape = "circle"
        self.shape = shape

        self.format_name()

        if cmds.objExists("%s.isControl" % (self.long_name)):
            self.pop_control_attributes()

        else:
            self.build_control()

    def sanitize_name(self):
        if self.name is None:
            self.name = "control"

        if "_CON" in self.name:
            self.name = self.name.replace("_CON", "")

        for side in self.side_formats:
            if self.name.startswith("%s_" % side):
                self.name = "".join(self.name.split("_")[1:])

    def pop_control_attributes(self):
        self.align_to = cmds.getAttr("%s.align_to" % self.long_name)
        self.side = cmds.getAttr("%s.side" % self.long_name)
        self.color = cmds.getAttr("%s.color" % self.long_name)

    def build_control(self):
        self.long_name = cmds.createNode("transform", n=self.long_name)
        self.set_shape(self.shape)

        if cmds.objExists(self.align_to):
            cmds.delete(cmds.parentConstraint(self.align_to, self.long_name))

        # add some non-keyable attributes to the control
        attrs = {'side': self.side, 'alingTo': self.align_to,
                 'color': self.color, 'isControl': 'y'}

        for attr, value in attrs.iteritems():
            cmds.addAttr(self.long_name, ln=attr, dt='string', k=False)
            cmds.setAttr(".".join([self.long_name, attr]),
                         value, type='string')

        self.zero_out()

    def set_color(self, color):
        color_map = {"red": 13, "yellow": 17, "blue": 6}

        shapes = cmds.listRelatives(self.long_name, c=True) or []

        for shape in shapes:
            cmds.setAttr("%s.overrideEnabled" % shape, 1)
            if color in color_map:
                cmds.setAttr("%s.overrideColor" % shape, color_map[color])

    def set_parent(self, par):
        self.parent = par
        full_attr = ".".join([self.long_name, 'parent'])

        if not cmds.objExists(full_attr):
            cmds.addAttr(self.long_name, ln='parent', dt='string', k=False)

        cmds.setAttr(full_attr, par)

    def set_shape(self, shape):
        for case in switch(shape):
            if case('circle'):
                circle = cmds.circle(ch=False)[0]
                self.get_shape_from(circle)
                cmds.delete(circle)
                break

    def mirror(self):
        # look for a mirror control object on the other side

        side_lower = self.side.lower()
        other_side = ""
        align_to = ""

        mirror_map_left = {"left": "right", "lf": "rt", "l": "r"}
        mirror_map_right = {"right": "left", "rt": "lf", "r": "l"}

        if side_lower in mirror_map_left.keys():
            other_side = list(mirror_map_left[side_lower])

        elif side_lower in mirror_map_right.keys():
            other_side = list(mirror_map_right[side_lower])

        for i, char in enumerate(self.side):
            if char.isupper():
                other_side[i] = other_side[i].upper()

        if not len(other_side):
            raise RuntimeError("Could not find opposite side.")

        other_side = "".join(other_side)

        if cmds.objExists(self.align_to):
            align_to = self.align_to.replace(self.side, other_side)
        else:
            align_to = "world"

        # otherwise, create new control aligned to align_to
        # with same specs as self but different color

        mirrored = Control(self.name, other_side, align_to, self.shape)

        return mirrored

    def format_name(self):

        self.sanitize_name()

        if not len(self.side):
            self.long_name = "_".join([self.name, "CON"])
            return

        # remove alphanumeric characters from side
        self.side = ''.join([i for i in self.side if i.isalpha()])

        if self.side.lower() not in self.side_formats:
            raise NotImplementedError("The input side is not a valid one.")

        # assert if resulting side is left or right

        if self.side.lower() in ["l", "lf", "left"]:
            self.color = "blue"
        else:
            self.color = "red"

        self.long_name = "_".join([self.side, self.name, "CON"])

    def set_to_origin(self):

        # pop control to world origin
        target = ''

        if hasattr(self, 'zero') and cmds.objExists(self.zero):
            target = self.zero
        elif hasattr(self, 'null') and cmds.objExists(self.null):
            target = self.null
        else:
            target = self.long_name

        cmds.xform(target, cp=True)
        temp_grp = cmds.group(em=True, n='temp_grp_1')
        cmds.delete(cmds.pointConstraint(temp_grp, target))
        cmds.delete(temp_grp)

    def zero_out(self, suffix="NULL", method="default"):

        # super : zero -> null -> con
        # default : null -> con

        null = self.long_name.replace("CON", suffix)
        self.null = cmds.duplicate(self.long_name, rc=True,
                                   n=null)[0]

        # delete children
        cmds.delete(cmds.listRelatives(self.null, ad=True))
        cmds.parent(self.long_name, self.null)

        if method == "super":
            zero = self.long_name.replace("CON", "ZERO")
            self.zero = cmds.duplicate(self.long_name, rc=True,
                                       n=zero)[0]

            # delete children
            cmds.delete(cmds.listRelatives(self.zero, ad=True))
            cmds.parent(self.null, self.zero)

    def get_shape_from(self, obj):

        obj = cmds.duplicate(obj, rc=True)

        cmds.parent(obj, self.long_name)
        cmds.makeIdentity(obj, apply=True, t=1, s=1, r=1)
        obj_shapes = cmds.listRelatives(obj, s=True)

        for shape in obj_shapes:
            cmds.parent(shape, self.long_name, r=True, s=True)
            cmds.rename(shape, "%sShape" % self.long_name)

        self.set_color(self.color)
        cmds.delete(obj)

    def drive_constrained(self, obj, p=True, r=True, s=False, o=False):
        if not cmds.objExists(obj):
            return
        if s:
            cmds.scaleConstraint(self.long_name, obj, mo=o)

        if p and r:
            cmds.parentConstraint(self.long_name, obj, mo=o)

        elif p and not r:
            cmds.pointConstraint(self.long_name, obj, mo=o)

        elif r and not p:
            cmds.orientConstraint(self.long_name, obj, mo=o)

    def drive_parented(self, obj):
        if cmds.objExists(obj):
            cmds.parent(obj, self.long_name)
