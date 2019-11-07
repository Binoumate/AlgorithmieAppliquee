#!/usr/bin/python3
import pygame
import sys
import json
import networkx as nx
import math
import matplotlib.pyplot as plt
import numpy

from board import *
from geometry import *
from networkx.drawing.layout import planar_layout

nodes = []

if (len(sys.argv) < 2) :
    sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

def generateOnTargetShots(G, Sol):
    global nodes
    for i in range(problem.getNbOpponents()):
        for j in numpy.arange(0, math.pi*2, problem.theta_step):
            for k in problem.goals:
                if(k.kickResult(problem.getOpponent(i), j) is not None):
                    G.add_node(len(nodes))
                    Sol.add_node(len(nodes))
                    nodes.append([i,j,k,False])

def isPossiblePos(x, y):
    for i in range(problem.getNbOpponents()):
        opponent = problem.getOpponent(i)
        if math.sqrt( (x-opponent[0])**2 + (y-opponent[1])**2) < problem.robot_radius*2:
            return False
    for i in problem.goals:
        for j in i.posts:
            if math.sqrt( (x-j[0])**2 + (y-j[1])**2) < problem.robot_radius*2:
                return False
    return True

def generateDefendersPositions(G):
    global nodes
    for i in list(G.nodes()):
        intersect = nodes[i][2].kickResult(problem.getOpponent(nodes[i][0]), nodes[i][1])
        for j in numpy.arange(min(problem.getOpponent(nodes[i][0])[0], intersect[0]), max(problem.getOpponent(nodes[i][0])[0], intersect[0]), problem.pos_step):
            for k in numpy.arange(min(problem.getOpponent(nodes[i][0])[1], intersect[1]), max(problem.getOpponent(nodes[i][0])[1], intersect[1]), problem.pos_step):
                if(segmentCircleIntersection(problem.getOpponent(nodes[i][0]), intersect, [j, k], problem.robot_radius) is not None):
                    if isPossiblePos(j, k)==False:
                        continue
                    curNode = len(nodes)
                    if [-1, j, k, False] not in nodes:
                        G.add_node(len(nodes))
                        nodes.append([-1, j, k, False])
                    else:
                        curNode = nodes.index([-1, j, k, False])
                    G.add_edge(i, curNode)

def generateDegMax(G):
    global nodes
    deg_max = 0
    for i in list(G.nodes()):
        if nodes[i][0] == -1:
            deg = G.degree(i)
            if deg > deg_max :
                deg_max = deg
    print(deg_max)

def getIndexDegreeMax(G):
    global nodes
    deg_max = -1
    node = -1
    for i in list(G.nodes()):
        if nodes[i][0] == -1:
            deg = G.degree(i)
            if deg > deg_max and nodes[i][3]==False:
                deg_max = deg
                node = i
    return node

def isDominated(G, n):
    global nodes
    for i in G.neighbors(n):
        if(nodes[i][0]==-1 and nodes[i][3]==True):
            return True
    return False

def isDominant(G, n):
    global nodes
    return nodes[n][3]==True

def dominatingSet(G):
    global nodes
    for i in list(G.nodes()):
        if nodes[i][0] != -1:
            if isDominated(G, i) == False:
                return False
    return True

def isCompatiblePos(n):
    global nodes
    for i in nodes:
        if i[3]==True:
            if math.sqrt((i[1]-nodes[n][1])**2 + (i[2]-nodes[n][2])**2) < problem.robot_radius*2:
                return False
    return True

def maxDegreeHeuristic(G, Sol):
    global nodes
    nbDefense = 0
    while(dominatingSet(G) == False):
        nodeDegreeMax = getIndexDegreeMax(G)
        if isCompatiblePos(nodeDegreeMax)==False:
            G.remove_node(nodeDegreeMax)
            continue
        nodes[nodeDegreeMax][3] = True
        Sol.add_node(nodeDegreeMax)
        for i in G.neighbors(nodeDegreeMax):
            Sol.add_edge(nodeDegreeMax, i)
        removeAttackers(G, nodeDegreeMax)
        nbDefense += 1
    return nbDefense

def removeAttackers(G, n):
    for i in G.neighbors(n):
        if nodes[i][0] != -1:
            G.remove_node(i)

G = nx.Graph()
Sol = nx.Graph()
generateOnTargetShots(G, Sol)
generateDefendersPositions(G)
print("nb defenseurs solution :")
print(maxDegreeHeuristic(G, Sol))

cpt = 0
for i in nodes:
    if i[0] == -1:
        cpt += 1
print("nb defenseurs possible :")
print(cpt)

cpt = 0
for i in nodes:
    if i[0] != -1:
        cpt += 1
print("nb tirs possible :")
print(cpt)

attack = []
defense = []
for i in nodes:
    if i[0]==-1:
        defense.append(i)
    else:
        attack.append(i)

nx.draw_networkx_nodes(G, nx.planar_layout(G), nodelist=attack, node_color='#ff0000')
nx.draw_networkx_nodes(G, nx.planar_layout(G), nodelist=defense, node_color='#0000ff')
nx.draw_networkx_edges(G, nx.planar_layout(G))

plt.show()

sys.exit()
