#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# the script was written by Erik Blank

'''
This script shows 4 charts
The first three charts show the accelerometer values for x-,y- and z-axis
On the last chart you can see the rotation around the z-Axis
Usage: python3 analyze.py <PORT>

'''

from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.flowchart import Flowchart, Node
from DIPPID_pyqtnode import DIPPIDNode, BufferNode
import pyqtgraph.flowchart.library as fclib
import sys
import numpy as np
import NormalVectorNode
import LogNode

def create_plots(fc, layout):
    # create plot widgets and adjust them on right position
    channels = ["accelX", "accelY", "accelZ"]
    plot_widgets = create_plot_widgets(channels, layout)

    # create PlotWidget node and set associated plot
    pw_nodes = init_plot_nodes(plot_widgets, fc)

    # create dippidNode with 3 outputs
    dippidNode = fc.createNode("DIPPID", pos=(-150, -100))

    # create buffer nodes for each plot widget nodes
    buffer_nodes = create_buffer_nodes(fc, pw_nodes)

    create_normvec_plot(dippidNode)

    connect_dippid_with_buffer(fc, dippidNode, channels, buffer_nodes)

    # connect buffers with plot nodes
    connect_buffer_with_plot(buffer_nodes, pw_nodes)

# create plot widgets for each channel of the dippid node
def create_plot_widgets(channels, layout):
    list = []
    for i in range(len(channels)):
        list.append(create_plot_widget(channels[i], [0, i+1], layout))
    return list

def create_plot_widget(name, pos, layout):
    pw = pg.PlotWidget()
    layout.addWidget(pw, pos[0], pos[1])
    pw.setTitle(name)
    pw.setYRange(-1, 1)
    return pw

# init plot nodes and set according plot
def init_plot_nodes(pws, fc):
    plot_nodes = []
    for i in range(len(pws)):
        plot_nodes.append(init_plot_node(pws[i], (150, -50 - i*50), fc))
    return plot_nodes


def init_plot_node(plot, pos, fc):
    pwNode = fc.createNode('PlotWidget', pos=pos)
    pwNode.setPlot(plot)
    return pwNode

# create as many buffernodes as plotnodes
def create_buffer_nodes(fc, pws):
    buffer_nodes = []
    for i in range(len(pws)):
        buffer_nodes.append(fc.createNode('Buffer', pos=(0, -50 - i*50)))
    return buffer_nodes

# create Normalvector plot widget, plotnode and node and connect terminals
def create_normvec_plot(dippidNode):
    pw = create_normvec_pw()
    plot_node = fc.createNode("PlotWidget", pos=(-200, -50))
    plot_node.setPlot(pw)
    normvec_node = fc.createNode("NormalVector", pos=(-100, -50))
    fc.connectTerminals(dippidNode["accelX"], normvec_node["axisIn1"])
    fc.connectTerminals(dippidNode["accelY"], normvec_node["axisIn2"])
    fc.connectTerminals(normvec_node["dataOut"], plot_node["In"])
    log_node = fc.createNode("LogNode", pos=(1000,1000))
    fc.connectTerminals(normvec_node["dataOut"], log_node["In"])

# create plotwidget of normalvector
def create_normvec_pw():
    pw = pg.PlotWidget()
    layout.addWidget(pw, 1,2)
    pw.setTitle("NormalVector")
    pw.setYRange(-1, 1)
    pw.setXRange(0, 1)
    return pw
        
# connect the dippidNode with the bufferNodes
def connect_dippid_with_buffer(fc, dippidNode, channels, buffer_nodes):
    for i in range(len(channels)):
        fc.connectTerminals(dippidNode[channels[i]], buffer_nodes[i]['dataIn'])

# connect the bufferNodes with the dippidNodes
def connect_buffer_with_plot(buffer_nodes, plot_nodes):
    if len(buffer_nodes) is not len(plot_nodes):
        print("size of buffer_nodes and plot_nodes are not the same")
    else:
        for i in range(len(buffer_nodes)):
            fc.connectTerminals(buffer_nodes[i]['dataOut'], plot_nodes[i]['In'])

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('DIPPIDNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={})

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    create_plots(fc, layout)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())