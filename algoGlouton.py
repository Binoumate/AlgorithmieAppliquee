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
from networkx.drawing.layout import *

#tuple(pos, goal, theta)
attack = []
#tuple(pos, goal, posAttaquant, done)
defense = []

if (len(sys.argv) < 2) :
	sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]

with open(problem_path) as problem_file:
	problem = Problem(json.load(problem_file))

def generateOnTargetShots():
	for i in range(problem.getNbOpponents()):
		for j in numpy.arange(0, math.pi*2, problem.theta_step):
			for k in problem.goals:
				if(k.kickResult(problem.getOpponent(i), j) is not None):
					attack.append([problem.getOpponent(i), k, j])
		
def generateDefendersPositions():
	for i in attack:
		intersect = i[1].kickResult(i[0], i[2])
		for j in numpy.arange( min(i[0][0], intersect[0]), max(i[0][0], intersect[0]), problem.pos_step):
			for k in numpy.arange( min(i[0][1], intersect[1]), max(i[0][1], intersect[1]), problem.pos_step):
				if(segmentCircleIntersection(i[0], intersect, [j, k], problem.robot_radius) is not None):
					if(isPossiblePos(j,k)):
						node = [[j,k], i[1], []]
						existant = existantNode(node)
						if(existant > -1):
							defense[existant][2].append(i)
						else:
							node[2].append(i)
							defense.append(node)
					
def existantNode(n):
	for i in range(len(defense)):
		if(n[0][0]==defense[i][0][0] and n[0][1]==defense[i][0][1]):
			return i
	return -1

def isPossiblePos(x, y):
	#Pas d'intersection avec les attaquants
	for ind in range(problem.getNbOpponents()):
		i = problem.getOpponent(ind)
		if math.sqrt( (x-i[0])**2 + (y-i[1])**2) < problem.robot_radius*2:
			return False
	#Pas d'intersection avec les poteaux
	for i in problem.goals:
		for j in i.posts:
			if math.sqrt( (x-j[0])**2 + (y-j[1])**2) < problem.robot_radius*2:	
				return False
	return True


def findMaxDegNode(a):
	degMax = 0
	node = None
	for i in defense:
		if(len(i[2]) == 0):
			continue
		for j in i[2]:
			if(j[0][0]==a[0][0] and j[0][1]==a[0][1] and j[2]==a[2]):
				if(len(j)>degMax):
					node = i
					degMax = len(j)
					break
	return node

def cleanAllBrothersOf(n):
	for i in n[2]:
		for j in defense:
			if(j[0][0]==n[0][0] and j[0][1]==n[0][1]):
				continue
			k = 0
			while k<len(j[2]):
				if(i[0][0]==j[2][k][0][0] and i[0][1]==j[2][k][0][1]):
					del j[2][k]
				k = k+1

def cleanAllCollisionsOf(n):
	for i in defense:
		if(n[0][0]==i[0][0] and n[0][1]==i[0][1]):
			continue
		if math.sqrt( (n[0][0]-i[0][0])**2 + (n[0][1]-i[0][1])**2) < problem.robot_radius*2:
			i[2] = []

def maxDegreeHeuristic():
	generateOnTargetShots()
	generateDefendersPositions()
	sol = []
	for i in attack:
		maxNode = findMaxDegNode(i)
		if(maxNode is None):
			continue
		print("current attack : [%f, %f], theta(%f)" % (i[0][0], i[0][1], i[2]))
		print("maxdeg : [%f, %f]" % (maxNode[0][0], maxNode[0][1]))
		sol.append(maxNode[0])
		cleanAllBrothersOf(maxNode)
		cleanAllCollisionsOf(maxNode)
		maxNode[2] = []
	return sol
		
sol = maxDegreeHeuristic()
print("nb tirs : %i" % (len(attack)))
print("nb pos defense : %i" % (len(defense)))
print("nb sol : %i" % (len(sol)))

print("sol :")
for i in sol:
	print("[%f, %f]," % (i[0], i[1]))

sys.exit()
