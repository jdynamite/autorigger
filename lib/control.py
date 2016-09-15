import maya.cmds as cmds
import maya.mel as mel
import cPickle as pickle
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

    def __init__(self, name=None, position=(0, 0, 0), align_to="world", parent="world", shape="circle", nameType=nameSpace.CONTROL):
        super(Control, self).__init__(
            name=name, position=position, parent=parent, nameType=nameType)

        self.color = "yellow"
        self.shape = shape
        self.align_to = align_to
        self.position = position

        if not self.name.endswith(nameSpace.DELIMITER + self.nameType):
            self.name += nameSpace.DELIMITER + self.nameType

        if cmds.objExists(self.name + ".isControl"):
            self.pop_control_attributes()

    @classmethod
    def getDefaultPath(cls, filename=None):
        sceneName = cmds.file(q=True, sceneName=True)
        wd = cmds.file(q=True, sceneName=True)
        if filename and isinstance(filename, basestring):
            if not filename.endswith('.shapes'):
                filename += '.shapes'
            wd = wd.strip(sceneName)
            wd += filename
            return wd
        else:
            wd = wd.strip('.ma')
            wd = wd.strip('.mb')
            return wd + '.shapes'

    @classmethod
    def bulkCreate(cls, *args):
        # returns the input as instances of the class
        # list[jnt1, jnt2, jnt3] -> list[con(jnt1), con(jnt2), con(jnt3)]
        # string -> con(string)

        result = []
        for arg in args:
            if type(arg) in [list, tuple]:
                objects = [Control(name=obj) for obj in arg]
                map(lambda o: result.append(o), objects)
            elif type(arg) == basestring:
                result.append(Control(name=obj))
        return result

    @classmethod
    def setColors(cls, objects, color):
        if type(objects) not in [list, tuple]:
            return
        objects = [o for o in objects if isinstance(o, Control)]
        map(lambda x: o.set_color(color), objects)

    @classmethod
    def setShapes(cls, objects, shape):
        if type(objects) not in [list, tuple]:
            return
        objects = [o for o in objects if isinstance(o, Control)]
        map(lambda x: o.setShape(shape), objects)

    @classmethod
    def mirrorShape(cls):
        sel = cmds.ls(sl=True) or []

        if len(sel) != 2:
            err = "Please select two curves. Driver -> Driven"
            raise RuntimeError(err)

        driver = sel[0]
        driven = sel[1]

        driver_shapes = cmds.listRelatives(driver, s=True) or []
        driven_shapes = cmds.listRelatives(driven, s=True) or []

        driver_shapes = [s for s in driver_shapes if not s.endswith("Orig")]
        driven_shapes = [s for s in driven_shapes if not s.endswith("Orig")]

        if not len(driver_shapes) or not len(driven_shapes):
            err = "Couldn't find any shapes attached to one or both objects."
            raise RuntimeError(err)

        for driver_shape, driven_shape in zip(driver_shapes, driven_shapes):
            cvs = cmds.getAttr("{0}.cp".format(driver_shape), s=1)
            cvs_driven = cmds.getAttr("{0}.cp".format(driven_shape), s=1)

            if cvs != cvs_driven:
                raise RuntimeError()

            for i in xrange(cvs):
                cv = "{0}.cv[{1}]"
                driverCv = cv.format(driver_shape, str(i))
                drivenCv = cv.format(driven_shape, str(i))

                driverPos = cmds.xform(driverCv, q=True, ws=True, t=True)
                drivenPos = [driverPos[0] * -1, driverPos[1], driverPos[2]]
                cmds.xform(drivenCv, ws=True, t=drivenPos)

    @classmethod
    def saveShapes(cls):
        keywords = ['Control', nameSpace.CONTROL]
        path = cls.getDefaultPath()
        the_file = open(path, 'wb')
        shapesData = {}

        # list nurbs curves
        shapes = cmds.ls(type="nurbsCurve")
        shapes = [s for s in shapes if not s.endswith('Orig')]
        shapes = [s for s in shapes if any(key in s for key in keywords)]
        shapes = [s for s in shapes if s is not None]

        for s in shapes:
            parent = cmds.listRelatives(s, p=True) or []

            if not len(parent):
                continue
            else:
                parent = parent[0]

            if parent not in shapesData.keys():
                shapesData[parent] = {}

            if s not in shapesData[parent].keys():
                shapesData[parent][s] = {}

            curveInfo = cmds.createNode("curveInfo")
            inputPlug = "{0}.inputCurve".format(curveInfo)
            shapePlug = "{0}.worldSpace[0]".format(s)
            cmds.connectAttr(shapePlug, inputPlug)

            knots = "{0}.knots".format(curveInfo)
            deg = "{0}.degree".format(s)
            cvs = "{0}.cv[*]".format(s)

            degree = cmds.getAttr(deg)
            period = cmds.getAttr("{0}.f".format(s))
            positions = cmds.getAttr(cvs)

            # check empty positions
            for pos in positions:
                if all(p == 0 for p in pos):
                    cmds.select(s)
                    mel.eval('doBakeNonDefHistory( 1, {"prePost"});')
                    cmds.select(cl=True)
                    positions = cmds.getAttr(cvs)
                    degree = cmds.getAttr(deg)
                    period = cmds.getAttr("{0}.f".format(s))
                    break

            knots = cmds.getAttr(knots)[0]

            if period > 0:
                for i in xrange(degree):
                    positions.append(positions[i])

            knots = knots[:len(positions) + degree - 1]
            shapesData[parent][s]['knots'] = knots
            shapesData[parent][s]['period'] = period
            shapesData[parent][s]['positions'] = positions
            shapesData[parent][s]['degree'] = degree

            cplug = "{0}.overrideEnabled"
            shapesData[parent][s]['color'] = 'yellow'
            for obj in [parent, s]:
                if cmds.getAttr(cplug.format(obj)):
                    color = "{0}.overrideColor".format(obj)
                    shapesData[parent][s]['color'] = cmds.getAttr(color)

            cmds.delete(curveInfo)

        pickle.dump(shapesData, the_file, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def loadShapes(cls):
        path = cmds.fileDialog(mode=0, directoryMask="*.shapes")
        success = "Successfuly loaded shape {0} for {1}."
        err = "{0} does not exist, skipping."
        the_file = open(path, 'rb')
        shapesData = pickle.load(the_file)
        print shapesData

        for obj in shapesData.keys():

            if not cmds.objExists(obj):
                print err.format(obj)
                continue

            # parent does exist
            # delete shapes from obj

            cmds.delete(cmds.listRelatives(obj, s=True, type="nurbsCurve"))

            # initialize object as curve
            con = cls(name='L_' + obj)
            con.name = obj

            for shape in shapesData[obj].keys():
                pos = shapesData[obj][shape]['positions']
                dg = shapesData[obj][shape]['degree']
                knots = shapesData[obj][shape]['knots']
                color = shapesData[obj][shape]['color']
                period = shapesData[obj][shape]['period']

                p = True if period > 0 else False
                con.color = color
                curve = cmds.curve(degree=dg, point=pos, knot=knots, per=p)
                con.get_shape_from(curve, destroy=True, replace=False)
                print success.format(shape, obj)

    def getNull(self):
        return self.null

    def pop_control_attributes(self):
        self.align_to = cmds.getAttr("%s.alignTo" % self.name) or 'world'
        self.side = cmds.getAttr("%s.side" % self.name)
        self.color = cmds.getAttr("%s.color" % self.name) or 'yellow'
        parent = cmds.listRelatives(self.name, p=True, type="transform")
        null = [n for n in parent if n.endswith(nameSpace.NULL)]
        self.null = None if not len(null) else null[0]
        self.parent = self.null if self.null else parent[0]

    def create(self):

        if cmds.objExists(self.name + ".isControl"):
            err = "Object with the same name already exists and is a control."
            raise RuntimeWarning(err)
            return self

        self.name = cmds.createNode("transform", n=self.name)
        self.setPosition(self.position)

        # add some non-keyable attributes to the control
        attrs = {'side': self.side, 'alignTo': self.align_to,
                 'color': self.color, 'isControl': 'y'}

        for attr, value in attrs.iteritems():
            cmds.addAttr(self.name, ln=attr, dt='string', k=False)
            cmds.setAttr(".".join([self.name, attr]),
                         value, type='string')

        self.set_shape(self.shape)

        if cmds.objExists(self.align_to):
            cmds.delete(cmds.parentConstraint(
                self.align_to, self.name, mo=False))

        self.zero()

    def set_color(self, color):
        color_map = {"red": 13, "yellow": 17, "blue": 6}
        inv_map = {v: k for k, v in color_map.items()}

        shapes = cmds.listRelatives(self.name, c=True) or []
        col = color_map[color] if isinstance(color, basestring) else color

        if not cmds.objExists("%s.color" % self.name):
            cmds.addAttr(self.name, ln='color', dt='string', k=False)

        for shape in shapes:
            cmds.setAttr("%s.overrideEnabled" % shape, 1)
            if color in color_map.keys():
                cmds.setAttr("%s.overrideColor" % shape, color_map[color])
                cmds.setAttr("%s.color" % self.name, color, type='string')
                self.color = color
            else:
                cmds.setAttr("%s.overrideColor" % shape, col)
                if col in inv_map.keys():
                    clr = inv_map[col]
                    cmds.setAttr("%s.color" % self.name, clr, type='string')
                    self.color = clr

    def set_shape(self, shape):

        self.shape = shape

        for case in Switch(shape):
            if case('circle'):
                circle = cmds.circle(ch=False)[0]
                self.get_shape_from(circle, destroy=True)
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
                        positions, degree, self.name + "_temp")
                    self.get_shape_from(curve, destroy=True)

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

        return Control(name=newName, position=self.position, align_to=align_to, shape=self.shape)

    def set_to_origin(self):

        # pop control to world origin
        if hasattr(self, 'null') and cmds.objExists(self.null):
            target = self.null
        else:
            target = self.name

        cmds.xform(target, cp=True)
        temp_grp = cmds.group(em=True, n='temp_grp_#')
        cmds.delete(cmds.pointConstraint(temp_grp, target))
        cmds.delete(temp_grp)

    def get_shape_from(self, obj, destroy=True, replace=True):

        if not destroy:
            obj = cmds.duplicate(obj, rc=True, n="temp_shape_#")

        if replace:
            oldShapes = cmds.listRelatives(self.name, s=True) or []
            map(lambda s: cmds.delete(s), oldShapes)

        cmds.parent(obj, self.name)
        cmds.xform(obj, os=True, t=(0, 0, 0), ro=(0, 0, 0), s=(1, 1, 1))
        obj_shapes = cmds.listRelatives(obj, s=True)

        for shape in obj_shapes:
            cmds.parent(shape, self.name, r=True, s=True)
            cmds.rename(shape, "%sShape#" % self.name)

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
    def __init__(self, name, position=(0, 0, 0), parent=None, nameType=nameSpace.GUIDE):
        super(Guide, self).__init__(name=name, position=position,
                                    parent=parent, nameType=nameType)

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
