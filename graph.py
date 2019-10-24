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

nodes = []

if (len(sys.argv) < 2) :
    sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

def generateOnTargetShots(G):
    global nodes
    for i in range(problem.getNbOpponents()):
        for j in numpy.arange(0, math.pi*2, problem.theta_step):
            for k in problem.goals:
                if(k.kickResult(problem.getOpponent(i), j) is not None):
                    G.add_node(len(nodes))
                    nodes.append([i,j,k,False])

def generateDefendersPositions(G):
    global nodes
    for i in list(G.nodes()):
        intersect = nodes[i][2].kickResult(problem.getOpponent(nodes[i][0]), nodes[i][1])
        for j in numpy.arange(min(problem.getOpponent(nodes[i][0])[0], intersect[0]), max(problem.getOpponent(nodes[i][0])[0], intersect[0]), problem.pos_step):
            for k in numpy.arange(min(problem.getOpponent(nodes[i][0])[1], intersect[1]), max(problem.getOpponent(nodes[i][0])[1], intersect[1]), problem.pos_step):
                if(segmentCircleIntersection(problem.getOpponent(nodes[i][0]), intersect, [j, k], problem.robot_radius) is not None):
                    G.add_node(len(nodes))
                    G.add_edge(i, len(nodes))
                    nodes.append([-1, j, k, False])

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
    deg_max = 0
    node = None
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
        #if nodes[i][0]==-1:
            #if(isDominant(G, i)==False and isDominated(G, i)==False):
                #return False
    return True

def maxDegreeHeuristic(G):
    global nodes
    nbDefense = 0
    while(dominatingSet(G) == False):
        nodeDegreeMax = getIndexDegreeMax(G)
        nodes[nodeDegreeMax][3] = True
        nbDefense += 1
    return nbDefense

G = nx.Graph()
generateOnTargetShots(G)
generateDefendersPositions(G)
print("nb defenseurs solution :")
print(maxDegreeHeuristic(G))

cpt = 0
for i in nodes:
    if i[0] == -1:
        cpt += 1
print("nb defenseurs possible :")
print(cpt)

nx.draw(G)
plt.show()

sys.exit()
