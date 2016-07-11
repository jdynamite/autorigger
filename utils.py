"""
utilities
note: split l8r into package(s)
"""
import maya.cmds as cmds


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
