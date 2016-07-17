'''

Utility nodes

'''

import maya.cmds as cmds

# checks if a plugin is loaded. If not it will attempt to load it
def isPluginLoaded(plugin):

    checker = cmds.pluginInfo(plugin, query=True, l=True)
    if not checker:
        cmds.loadPlugin(plugin)