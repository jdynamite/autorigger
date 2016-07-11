import cPickle as pickle
from functools import partial
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaAnim as omanim
import maya.cmds as cmds

from control import Control
from rig import Rig, Switch, Module
import utils

from PySide import QtGui, QtCore
from shiboken import wrapInstance
