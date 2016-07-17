'''

Utility nodes

'''

import maya.cmds as cmds

# returns grp if it exists, otherwise creates the grp and returns it


def getGroup(grp):

    if not isinstance(grp, basestring):
        raise RuntimeError("Pass a string puhleeze.")
        return grp

    return grp if cmds.objExists(grp) else cmds.createNode("transform", n=grp)


# checks if a plugin is loaded. If not it will attempt to load it
def isPluginLoaded(plugin):

    checker = cmds.pluginInfo(plugin, query=True, l=True)
    if not checker:
        cmds.loadPlugin(plugin)


# pops and orients object's pivot to world origin without moving it


def pivotToOrigin(obj):

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
