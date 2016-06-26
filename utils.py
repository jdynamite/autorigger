import maya.cmds as cmds

"""
utilities
note: split l8r into package(s)
"""


def get_skinCluster(mesh):

    if mesh is None:
        raise RuntimeError("Mesh must have a str len.")
        return None

    elif isinstance(mesh, list):
        mesh = mesh[0]

    elif not cmds.objExists(mesh):
        raise RuntimeError("Mesh doesn't exist in this scene.")
        return None

    mesh_type = cmds.nodeType(mesh)
    s = ''

    if mesh_type == "transform":

        shapes = cmds.listRelatives(mesh, s=True, type="mesh")

        for shape in shapes:
            if "Orig" not in shape:
                s = shape
                break

        if not len(s):
            raise RuntimeError("Couldn't find any geo in %s" % mesh)
            return

    elif mesh_type == "mesh" or mesh_type == "nurbsSurface" or mesh_type == "nurbsCurve":
        s = mesh

    else:
        raise NotImplementedError("Mesh is not of proper type.")
        return None

    skin_cluster = ''

    for sc in cmds.ls(type="skinCluster"):
        for geo in cmds.skinCluster(sc, q=True, g=True):
            if geo == s:
                skin_cluster = sc
                break

    if not len(skin_cluster):
        raise RuntimeError(
            "couldnt find any skin cluster with %s as influence" % s)
        return None

    return skin_cluster


def get_influences(skin_cluster):
    """
    get joints from skin_cluster
    """

    if skin_cluster is None:
        return

    if not cmds.objExists(skin_cluster):
        raise RuntimeError("%s is not a skinCluster" % skin_cluster)

    influences = cmds.skinCluster(skin_cluster, q=True, weightedInfluence=True)
    joints = list()

    for i in influences:
        if cmds.nodeType(i) == "joint":
            joints.append(i)

    return joints


def pivot_to_origin(obj):

    # pop control to world origin

    is_parented = False
    old_par = cmds.listRelatives(obj, p=True)

    cmds.parent(obj, w=True)
    cmds.xform(obj, ztp=True, piv=[0.0, 0.0, 0.0])

    if old_par is not None and len(old_par):
        is_parented = True

    cmds.select(cl=True)
    grp = cmds.group(em=True)

    cmds.parent(obj, grp)
    cmds.makeIdentity(obj, apply=True, t=True, s=True, r=True)

    if is_parented:
        cmds.parent(obj, old_par)
    else:
        cmds.parent(obj, w=True)

    cmds.delete(grp)
