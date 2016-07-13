import cPickle as pickle
from functools import partial
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaAnim as omanim
import maya.cmds as cmds

from PySide import QtGui, QtCore
from shiboken import wrapInstance

from lib import nameSpace

def show():
    dialog = SkinDialog(parent=get_maya_win())
    dialog.show()


def get_maya_win():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QMainWindow)


class SkinDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(SkinDialog, self).__init__(parent)
        self.setWindowTitle("Skin import/export")
        self.setObjectName("skinUI")
        self.setModal(False)
        self.setFixedSize(200, 80)

        vbox = QtGui.QVBoxLayout(self)

        btn = QtGui.QPushButton("Import")
        btn.released.connect(SkinCluster.create_and_import)
        vbox.addWidget(btn)

        btn = QtGui.QPushButton("Export")
        btn.released.connect(SkinCluster.export)
        vbox.addWidget(btn)


class WeightsRemapDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(WeightsRemapDialog, self).__init__(parent)
        self.setWindowTitle("Remap weights")
        self.setObjectName("remapWeightsUI")
        self.setModal(True)
        self.resize(600, 400)
        self.mapping = {}

        mainVBox = QtGui.QVBoxLayout(self)

        label = QtGui.QLabel(
            "The following influences have no match with import file")
        label.setWordWrap(True)

        mainVBox.addWidget(label)

        hbox = QtGui.QHBoxLayout()
        mainVBox.addLayout(hbox)

        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addWidget(QtGui.QLabel("Unmapped influences"))
        self.existing_influences = QtGui.QListWidget()
        vbox.addWidget(self.existing_influences)

        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addWidget(QtGui.QLabel("Available imported influences"))
        scrollArea = QtGui.QScrollArea()
        widget = QtGui.QScrollArea()
        self.imported_influence_layout = QtGui.QVBoxLayout(widget)
        vbox.addWidget(widget)

        hbox = QtGui.QHBoxLayout()
        mainVBox.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Ok")
        btn.released.connect(self.accept)
        hbox.addWidget(btn)

    def set_infl(self, imported_influences, existing_influences):
        infs = list(existing_influences)
        infs.sort()
        self.existing_influences.addItems(infs)
        width = 200

        for infl in imported_influences:
            row = QtGui.QHBoxLayout()
            self.imported_influence_layout.addLayout(row)

            label = QtGui.QLabel(infl)

            row.addWidget(label)

            toggle_btn = QtGui.QPushButton(">")
            toggle_btn.setMaximumWidth(30)
            row.addWidget(toggle_btn)

            label = QtGui.QLabel('')
            label.setMaximumWidth(width)
            label.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                QtGui.QSizePolicy.Fixed)
            row.addWidget(label)

            toggle_btn.released.connect(
                partial(self.set_influence_mapping, src=infl, label=label))

        self.imported_influence_layout.addStretch()

    def set_influence_mapping(self, src, label):
        selected_infl = self.existing_influences.selectedItems()

        if not selected_infl:
            return

        dst = selected_infl[0].text()
        label.setText(dst)
        self.mapping[src] = dst

        # Remove from the list
        index = self.existing_influences.indexFromItem(selected_infl[0])
        item = self.existing_influences.takeItem(index.row())

        del item


class SkinCluster(object):
    kFileExtension = nameSpace.WEIGHTSEXTENSION
    kWeightsFolder = nameSpace.WEIGHTSFOLDER
    kMeshSuffix = ["_REN", "_GEO", "_MESH", "_ren", "_geo", "_mesh"]

    @classmethod
    def pretty_name(cls, mesh, skin):

        for suffix in cls.kMeshSuffix:
            if mesh.endswith(suffix):
                cmds.rename(skin, mesh.replace(suffix, "_sC"))
                return

        cmds.rename(skin, mesh + "_sC")

    @classmethod
    def get_joints(cls, skin_cluster):
        if skin_cluster is None:
            return None

        if not cmds.objExists(skin_cluster):
            raise RuntimeError("%s is not a skinCluster" % skin_cluster)

        influences = cmds.skinCluster(
            skin_cluster, q=True, weightedInfluence=True)
        joints = list()

        for i in influences:
            if cmds.nodeType(i) == "joint":
                joints.append(i)

        return joints

    @classmethod
    def remap_joints(cls, data):
        joints = data['weights'].keys()

        unused_imports = []
        no_match = set([cls.remove_namespace_from(x)
                        for x in cmds.ls(type='joint')])

        for j in joints:
            if j in no_match:
                no_match.remove(j)
            else:
                unused_imports.append(j)

        if unused_imports and no_match:
            dialog = WeightsRemapDialog(get_maya_win())
            dialog.set_infl(unused_imports, no_match)
            dialog.exec_()

            for src, dst in dialog.mapping.items():
                data['weights'][dst] = data['weights'][src]
                del data['weights'][src]

        return data

    @classmethod
    def export(cls, mesh=None, path=None):
        skin = SkinCluster(mesh, path)
        skin.export_weights(path)

    @classmethod
    def create_and_import(cls, mesh=None, path=None):
        skin_cluster = None

        if mesh is None:
            try:
                mesh = cmds.ls(sl=True)[0]
            except:
                raise RuntimeError("No mesh selected or passed in.")

        if path is None:
            path = cls.get_default_path()
            path += mesh + cls.kFileExtension

        elif not path.endswith(cls.kFileExtension):
            path += cls.kFileExtension

        the_file = open(path, 'rb')
        data = pickle.load(the_file)
        the_file.close()

        imported_vtx = len(data['blendWeights'])
        mesh_count = cmds.polyEvaluate(mesh, vertex=True)

        if mesh_count != imported_vtx:
            raise RuntimeError(
                "Imported vtx count did not match that of {}.".format(mesh))

        if SkinCluster.get_skin(mesh):
            skin_cluster = SkinCluster(mesh)
            data = cls.remap_joints(data)

        else:
            data = cls.remap_joints(data)
            joints = data['weights'].keys()
            cmds.skinCluster(joints, mesh, tsb=True, nw=2, n=data['name'])
            skin_cluster = SkinCluster(mesh)

        skin_cluster.set_data(data)
        print("Imported weights successfully from {}.".format(path))

    @classmethod
    def get_default_path(cls):
        wd = cmds.workspace(q=True, dir=True)
        return wd + cls.kWeightsFolder + '/'

    @classmethod
    def get_skin(cls, mesh_shape):
        mesh_shape = cls.get_shape(mesh_shape)
        skins = cmds.ls(type="skinCluster")
        for skin in skins:
            try:
                if mesh_shape in cmds.skinCluster(skin, q=True, g=True):
                    return skin
            except:
                return None
        return None

    @classmethod
    def remove_namespace_from(cls, string):
        if ':' in string and '|' in string:
            tokens = string.split('|')
            result = [s.split(':')[-1] for s in tokens]

            return '|'.join(result)

        elif ':' in string:
            return string.split(':')[-1]

        else:
            return string

    @classmethod
    def get_shape(cls, mesh, intermediate=False):
        mesh_type = cmds.nodeType(mesh)

        if mesh_type == 'transform':
            shapes = cmds.listRelatives(mesh, shapes=True, path=True) or []

            for shape in shapes:
                is_interm = cmds.getAttr("{}.intermediateObject".format(shape))

                if intermediate and is_interm and cmds.listConnections(shape, source=False):
                    return shape

                elif not intermediate and not is_interm:
                    return shape

            if len(shapes):
                return shapes[0]

        elif mesh_type in ['nurbsCurve', 'mesh', 'nurbsSurface']:
            return mesh

        return None

    def import_weights(self, path=None):
        self.get_data()

        if path is None:
            path = SkinCluster.get_default_path()
            path += self.mesh
            path += SkinCluster.kFileExtension

        elif not path.endswith(SkinCluster.kFileExtension):
            path += SkinCluster.kFileExtension

        the_file = open(path, 'rb')
        data = pickle.load(the_file)
        the_file.close()

        imported_vtx = len(data['blendWeights'])
        mesh_count = cmds.polyEvaluate(self.mesh_shape, vertex=True)

        if mesh_count != imported_vtx:
            raise RuntimeError(
                "Imported vtx count did not match that of {}.".format(mesh))

        self.data = SkinCluster.remap_joints(data)
        self.set_data(self.data)

    def export_weights(self, path=None):
        if path is None:
            path = self.weights_path
            path = ''.join([path, self.mesh, SkinCluster.kFileExtension])

        if not path.endswith(SkinCluster.kFileExtension):
            path += SkinCluster.kFileExtension

        self.get_data()

        the_file = open(path, 'wb')
        pickle.dump(self.data, the_file, pickle.HIGHEST_PROTOCOL)
        the_file.close()

        print "Exported skin weights to {} successfully.".format(path)

    def set_data(self, data):
        self.data = data

        dag_path, components = self._get_components()
        self.set_weights(dag_path, components)
        self.set_blend_weights(dag_path, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            cmds.setAttr("{}.{}".format(
                self.skin_cluster, attr), self.data[attr])

    def get_data(self):
        dag_path, components = self._get_components()
        self.get_influence_weights(dag_path, components)
        self.get_blend_weights(dag_path, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            self.data[attr] = cmds.getAttr(
                "{}.{}".format(self.skin_cluster, attr))

        self.data["name"] = self.skin_cluster

    def _get_components(self):
        """
        Looks up deformer set of skin cluster to find which components
        are being affected by self.skin_cluster
        """

        fn_set = om.MFnSet(self.fn.deformerSet())
        members = om.MSelectionList()
        fn_set.getMembers(members, False)

        dag_path = om.MDagPath()
        components = om.MObject()

        members.getDagPath(0, dag_path, components)

        return dag_path, components

    def _get_current_weights(self, dag_path, components):
        weights = om.MDoubleArray()
        util = om.MScriptUtil()
        util.createFromInt(0)
        uint_ptr = util.asUintPtr()
        self.fn.getWeights(dag_path, components, weights, uint_ptr)
        return weights

    def set_weights(self, dag_path, components):
        weights = self._get_current_weights(dag_path, components)

        infl_paths = om.MDagPathArray()
        n_infl = self.fn.influenceObjects(infl_paths)

        infl_per_vtx = weights.length() / n_infl

        for imported_infl, imported_weights in self.data['weights'].items():
            for ii in xrange(infl_paths.length()):
                infl = infl_paths[ii].partialPathName()
                infl = SkinCluster.remove_namespace_from(infl)

                if infl == imported_infl:
                    for jj in xrange(infl_per_vtx):
                        weights.set(imported_weights[jj], jj * n_infl + ii)

                    break

        infl_indices = om.MIntArray(n_infl)

        for ii in xrange(n_infl):
            infl_indices.set(ii, ii)

        self.fn.setWeights(dag_path, components, infl_indices, weights, False)

    def set_blend_weights(self, dag_path, components):
        blend_weights = om.MDoubleArray(len(self.data['blendWeights']))
        for i, w in enumerate(self.data['blendWeights']):
            blend_weights.set(w, i)
        self.fn.setBlendWeights(dag_path, components, blend_weights)

    def get_influence_weights(self, dag_path, components):
        weights = self._get_current_weights(dag_path, components)
        infl_paths = om.MDagPathArray()

        n_infl = self.fn.influenceObjects(infl_paths)
        infl_per_vtx = weights.length() / n_infl

        for idx in xrange(infl_paths.length()):
            infl = infl_paths[idx].partialPathName()
            infl = SkinCluster.remove_namespace_from(infl)
            self.data['weights'][infl] = \
                [weights[jj * n_infl + idx] for jj in range(infl_per_vtx)]

    def get_blend_weights(self, dag_path, components):
        weights = om.MDoubleArray()
        self.fn.getBlendWeights(dag_path, components, weights)
        self.data['blendWeights'] = [weights[i]
                                     for i in xrange(weights.length())]

    def __init__(self, mesh=None, weights_path=None):
        self.skin_cluster = None
        self.mesh_shape = None
        self.mesh = mesh
        self.weights_path = weights_path
        self.mobject = om.MObject()

        if self.weights_path is None:
            self.weights_path = SkinCluster.get_default_path()

        if self.mesh is None:
            try:
                self.mesh = cmds.ls(sl=True)[0]
            except:
                raise RuntimeError("No mesh found.")

        elif not cmds.objExists(self.mesh):
            raise RuntimeError("{} doesn't seem to exist.".format(self.mesh))

        self.mesh_shape = SkinCluster.get_shape(self.mesh)

        if self.mesh_shape is None:
            raise RuntimeError(
                "Could not find a shape attached to {}".format(self.mesh))

        self.skin_cluster = SkinCluster.get_skin(self.mesh_shape)

        if self.skin_cluster is None:
            raise ValueError("No skin attached to {}.".format(self.mesh))

        # Get skinCluster MObject and attach to MFnSkinCluster
        # store into data member dictionary

        msel = om.MSelectionList()
        msel.add(self.skin_cluster)
        msel.getDependNode(0, self.mobject)

        self.fn = omanim.MFnSkinCluster(self.mobject)
        self.data = {'weights': {}, 'blendWeights': [],
                     'name': self.skin_cluster}
        self.get_data()
