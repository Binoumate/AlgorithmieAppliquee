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

def generateDefendersPositions(G):
    for i in list(G.nodes()):
        intersect = i[2].kickResult(problem.getOpponent(i[0]), i[1])
        for j in numpy.arange(min(problem.getOpponent(i[0])[0], intersect[0]), max(problem.getOpponent(i[0])[0], intersect[0]), problem.pos_step):
            for k in numpy.arange(min(problem.getOpponent(i[1])[1], intersect[1]), max(problem.getOpponent(i[1])[1], intersect[1]), problem.pos_step):
                if(segmentCircleIntersection(problem.getOpponent(i[0]), intersect, [j, k], problem.robot_radius) is not None):
                    G.add_node((j,k))
                    G.add_edge(i, (j,k))

G = nx.Graph()
generateOnTargetShots(G)
generateDefendersPositions(G)
nx.draw(G)
plt.show()

sys.exit()
