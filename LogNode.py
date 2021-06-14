#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# the script was written by Erik Blank

from pyqtgraph.flowchart import Node
import pyqtgraph.flowchart.library as fclib
import numpy as np

class LogNode(Node):
    nodeName = "LogNode"

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
        }
        Node.__init__(self, name, terminals=terminals)
    
    def process(self, **kwds):
        print(kwds["In"])

fclib.registerNodeType(LogNode, [('Data',)])