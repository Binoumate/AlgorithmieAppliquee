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
from copy import deepcopy

#tuple(pos, goal, theta)
attack = []
#tuple(pos, goal, posAttaquant, done)
defense = []
archive = []

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
		intersect[0] = round(intersect[0], 1)
		intersect[1] = round(intersect[1], 1)
		for j in numpy.arange( min(i[0][0], intersect[0])-problem.robot_radius*2, max(i[0][0], intersect[0])+problem.robot_radius*2, problem.pos_step):
			for k in numpy.arange( min(i[0][1], intersect[1])-problem.robot_radius*2, max(i[0][1], intersect[1])+problem.robot_radius*2, problem.pos_step):
				j = round(j, 1)
				k = round(k, 1)
				if(segmentCircleIntersection(i[0], intersect, [j, k], problem.robot_radius) is not None):
					if(isPossiblePos(j,k)):
						node = [[j,k], i[1], []]
						existant = existantNode(node)
						if(existant > -1):
							defense[existant][2].append(i)
							archive[existant][2].append(deepcopy(i))
						else:
							node[2].append(i)
							defense.append(node)
							archive.append(deepcopy(node))
					
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
	index = -1
	for defe in range(len(defense)):
		i = defense[defe]
		if(len(i[2]) == 0):
			continue
		for j in i[2]:
			if(j[0][0]==a[0][0] and j[0][1]==a[0][1] and j[2]==a[2]):
				if(len(i[2])>degMax):
					index = defe
					degMax = len(i[2])
					break
	return index

def cleanAllBrothersOf(n):
	for i in n[2]:
		for j in defense:
			if(j[0][0]==n[0][0] and j[0][1]==n[0][1]):
				continue
			k = 0
			while k<len(j[2]):
				if(i[0][0]==j[2][k][0][0] and i[0][1]==j[2][k][0][1] and i[1]==j[2][k][1]):
					del j[2][k]
				k = k+1

def cleanAllCollisionsOf(n):
	for i in defense:
		if(n[0][0]==i[0][0] and n[0][1]==i[0][1]):
			continue
		if math.sqrt( (n[0][0]-i[0][0])**2 + (n[0][1]-i[0][1])**2) < problem.robot_radius*2:
			i[2] = []

def replace(ind, sol):
	currentAttacks = archive[ind][2]
	for defe in range(len(sol)):
		defender = sol[defe]
		if(len(currentAttacks) > len(archive[defender[1]][2])):
			check = []
			for i in archive[defender[1]][2]:
				check.append(False)
			for i in range(len(archive[defender[1]][2])):
				for j in currentAttacks:
					if(archive[defender[1]][2][i][0][0]==j[0][0] and archive[defender[1]][2][i][0][1]==j[0][1] and archive[defender[1]][2][i][1]==j[1] and archive[defender[1]][2][i][2]==j[2]):
						check[i] = True
			if(all(check)):
				sol[defe] = [archive[ind][0], ind]
				return

def maxDegreeHeuristic():
	generateOnTargetShots()
	generateDefendersPositions()
	sol = []
	for i in attack:
		maxIndex = findMaxDegNode(i)
		if(maxIndex == -1):
			continue
		print("deg(%i) = %i" % (maxIndex, len(defense[maxIndex][2])))
		print(defense[maxIndex][2])
		sol.append([defense[maxIndex][0], maxIndex])
		cleanAllBrothersOf(defense[maxIndex])
		cleanAllCollisionsOf(defense[maxIndex])
		#replace(maxIndex, sol)
		defense[maxIndex][2] = []
	return sol
		
sol = maxDegreeHeuristic()
print("nb tirs : %i" % (len(attack)))
print("nb pos defense : %i" % (len(defense)))
print("nb sol : %i" % (len(sol)))

print("sol :")
for i in sol:
	print("[%f, %f]," % (i[0][0], i[0][1]))

sys.exit()
