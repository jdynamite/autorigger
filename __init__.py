import cPickle as pickle
import maya.OpenMaya as om
import maya.OpenMayaAnim as omanim
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide import QtGui, QtCore
from functools import partial
from shiboken import wrapInstance

import utils
from lib.control import Control
from rig import Rig, Switch, Module

from lib import nameSpace