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

liste1 = []
liste2 = []

if (len(sys.argv) < 2) :
    sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

def generateOnTargetShots(G):
    for i in range(problem.getNbOpponents()):
        for j in numpy.arange(0, math.pi*2, problem.theta_step):
            for k in problem.goals:
                if(k.kickResult(problem.getOpponent(i), j) is not None):
                    G.add_node((i, j, k))
                    liste1.append((i,j,k))

def generateDefendersPositions(G):
    for i in list(G.nodes()):
        intersect = i[2].kickResult(problem.getOpponent(i[0]), i[1])
        for j in numpy.arange(min(problem.getOpponent(i[0])[0], intersect[0]), max(problem.getOpponent(i[0])[0], intersect[0]), problem.pos_step):
            for k in numpy.arange(min(problem.getOpponent(i[0])[1], intersect[1]), max(problem.getOpponent(i[0])[1], intersect[1]), problem.pos_step):
                if(segmentCircleIntersection(problem.getOpponent(i[0]), intersect, [j, k], problem.robot_radius) is not None):
                    G.add_node((j,k))
                    G.add_edge(i, (j,k))
                    liste2.append((j,k))

def generateDegMax(G):
    deg_max = 0
    for i in list(G.nodes()):
        deg = G.degree(i)
        if deg > deg_max :
            deg_max = deg
    print(deg_max)


G = nx.Graph()
generateOnTargetShots(G)
generateDefendersPositions(G)
print(len(liste1))
print(len(liste2))
#print(liste1)
#print(liste2)
nx.draw(G)
plt.show()

sys.exit()
