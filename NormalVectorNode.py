#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# the script was written by Erik Blank

from pyqtgraph.flowchart import Node
import pyqtgraph.flowchart.library as fclib
import numpy as np

# NormalVectorNode gets two values as input and gives a 2-D vector as output
class NormalVectorNode(Node):

    nodeName = "NormalVector"

    AXIS_1 = "axisIn1"
    AXIS_2 = "axisIn2"

    def __init__(self, name):
        terminals = {
            self.AXIS_1: dict(io='in'),
            self.AXIS_2: dict(io='in'),
            'dataOut': dict(io='out'),
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        normal_vector = np.array([kwds[self.AXIS_1][0], kwds[self.AXIS_2][0]])
        return {"dataOut": normal_vector}

fclib.registerNodeType(NormalVectorNode, [('Data',)])
