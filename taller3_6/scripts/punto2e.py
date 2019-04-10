#!/usr/bin/python

"""
Path Planning Sample Code with Randamized Rapidly-Exploring Random Trees (RRT)
@author: AtsushiSakai(@Atsushi_twi)
"""

""" librerias algoritmo"""
import matplotlib.pyplot as plt
import random
import math
import copy
import numpy as np

""" librerias usadas"""

import rospy
from std_msgs.msg import Float32MultiArray, Float32
from pylab import *
from pynput.keyboard import Key, Listener 
import matplotlib.pyplot as plt
import threading
import time
import sys 


show_animation = True

robot = 2

def arrancar():
	rospy.init_node('punto2e', anonymous = True)
	rospy.Subscriber('/obstacles', Float32MultiArray ,obstacles)

	tasa = rospy.Rate(10)
	rospy.myargv(argv=sys.argv)
	try:
		xfin = float(sys.argv[1])
		yfin = float(sys.argv[2])
		thetafin = float(sys.argv[3])
	except:    								##Tratamiento de los argumentos ingresador por el usuario
		xfin = 40
		yfin = 40
		thetafin = math.pi/2
         
       obstacleList = [[obs[0],obs[5],obs[10]],[obs[1],obs[6],obs[11]],[obs[2],obs[7],obs[12]],[obs[3],obs[8],obs[13]],[obs[4],obs[9],obs[14]]]

	   rrt = RRT(start=[0, 0], goal=[xfin, yfin],
              randArea=[-5, 45], obstacleList=obstacleList)

        path = rrt.Planning(animation=show_animation)


        maxIter = 1000
        smoothedPath = PathSmoothing(path, maxIter, obstacleList)


       # Draw final path
        if show_animation:
        rrt.DrawGraph()
        plt.plot([x for (x, y) in path], [y for (x, y) in path], '-r')

        plt.plot([x for (x, y) in smoothedPath], [
            y for (x, y) in smoothedPath], '-b')


	try:
		while not rospy.is_shutdown():
			tasa.sleep()
	except rospy.ServiceException as e:
		pass



		
def obstacles(data):
	global obs
	obs = data.data




		
def ThreadInputs():
	with Listener(on_press = keypress) as listener:
		listener.join()
		
def keypress(key):
	global bandera
	while True:
		if key == Key.esc:
			bandera = True 	##Se usa la tecla Esc para terminar los diferentes hilos implementados
			return False


class Node():
    
    RRT Node
    

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None



"""class Nodo:
	def __init__(self, pos):
		self.pos = pos
		self.coord = [-5 + (0.25*pos[0]) , -5 + (0.25*pos[1])]
		self.padre = None
		"""
	
	def agregarVecinos(self, vecino):
		self.vecinos.append(vecino)
		
	
		
	


""" Algoritmo RRT"""


class RRT():
    """
    Class for RRT Planning
    """

    def __init__(self, start, goal, obstacleList, randArea, expandDis=1.0, goalSampleRate=5, maxIter=500):
        """
        Setting Parameter
        start:Start Position [x,y]
        goal:Goal Position [x,y]
        obstacleList:obstacle Positions [[x,y,size],...]
        randArea:Ramdom Samping Area [min,max]
        """
        self.start = [0,0]
        self.end = [xfin,yfin]
        self.minrand = randArea[0]
        self.maxrand = randArea[1]
        self.expandDis = expandDis
        self.goalSampleRate = goalSampleRate
        self.maxIter = maxIter
        self.obstacleList = obstacleList

    def Planning(self, animation=True):
        """
        Pathplanning
        animation: flag for animation on or off
        """

        self.nodeList = [self.start]
        while True:
            # Random Sampling
            if random.randint(0, 100) > self.goalSampleRate:
                rnd = [random.uniform(self.minrand, self.maxrand), random.uniform(
                    self.minrand, self.maxrand)]
            else:
                rnd = [self.end.x, self.end.y]

            # Find nearest node
            nind = self.GetNearestListIndex(self.nodeList, rnd)
            # print(nind)

            # expand tree
            nearestNode = self.nodeList[nind]
            theta = math.atan2(rnd[1] - nearestNode.y, rnd[0] - nearestNode.x)

            newNode = copy.deepcopy(nearestNode)
            newNode.x += self.expandDis * math.cos(theta)
            newNode.y += self.expandDis * math.sin(theta)
            newNode.parent = nind

            if not self.__CollisionCheck(newNode, self.obstacleList):
                continue

            self.nodeList.append(newNode)

            # check goal
            dx = newNode.x - self.end.x
            dy = newNode.y - self.end.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= self.expandDis:
                print("Goal!!")
                break

            if animation:
                self.DrawGraph(rnd)

        path = [[self.end.x, self.end.y]]
        lastIndex = len(self.nodeList) - 1
        while self.nodeList[lastIndex].parent is not None:
            node = self.nodeList[lastIndex]
            path.append([node.x, node.y])
            lastIndex = node.parent
        path.append([self.start.x, self.start.y])

        return path






    def DrawGraph(self, rnd=None):
        plt.clf()
        if rnd is not None:
            plt.plot(rnd[0], rnd[1], "^k")
        for node in self.nodeList:
            if node.parent is not None:
                plt.plot([node.x, self.nodeList[node.parent].x], [
                         node.y, self.nodeList[node.parent].y], "-g")
        for (x, y, size) in self.obstacleList:
            self.PlotCircle(x, y, size)

        plt.plot(self.start.x, self.start.y, "xr")
        plt.plot(self.end.x, self.end.y, "xr")
        plt.axis([-2, 15, -2, 15])
        plt.grid(True)
        plt.pause(0.01)




    def PlotCircle(self, x, y, size):
        deg = list(range(0, 360, 5))
        deg.append(0)
        xl = [x + size * math.cos(np.deg2rad(d)) for d in deg]
        yl = [y + size * math.sin(np.deg2rad(d)) for d in deg]
        plt.plot(xl, yl, "-k")



    def GetNearestListIndex(self, nodeList, rnd):
        dlist = [(node.x - rnd[0]) ** 2 + (node.y - rnd[1])
                 ** 2 for node in nodeList]
        minind = dlist.index(min(dlist))
        return minind

    def __CollisionCheck(self, node, obstacleList):

        for (ox, oy, size) in obstacleList:
            dx = ox - node.x
            dy = oy - node.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= size:
                return False  # collision

        return True  # safe





def GetPathLength(path):
    le = 0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        d = math.sqrt(dx * dx + dy * dy)
        le += d

    return le




def GetTargetPoint(path, targetL):
    le = 0
    ti = 0
    lastPairLen = 0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        d = math.sqrt(dx * dx + dy * dy)
        le += d
        if le >= targetL:
            ti = i - 1
            lastPairLen = d
            break

    partRatio = (le - targetL) / lastPairLen
    #  print(partRatio)
    #  print((ti,len(path),path[ti],path[ti+1]))

    x = path[ti][0] + (path[ti + 1][0] - path[ti][0]) * partRatio
    y = path[ti][1] + (path[ti + 1][1] - path[ti][1]) * partRatio
    #  print((x,y))

    return [x, y, ti]





def LineCollisionCheck(first, second, obstacleList):
    # Line Equation

    x1 = first[0]
    y1 = first[1]
    x2 = second[0]
    y2 = second[1]

    try:
        a = y2 - y1
        b = -(x2 - x1)
        c = y2 * (x2 - x1) - x2 * (y2 - y1)
    except ZeroDivisionError:
        return False

    for (ox, oy, size) in obstacleList:
        d = abs(a * ox + b * oy + c) / (math.sqrt(a * a + b * b))
        if d <= (size):
            return False

    #  print("OK")

    return True  # OK




def PathSmoothing(path, maxIter, obstacleList):
    #  print("PathSmoothing")

    le = GetPathLength(path)

    for i in range(maxIter):
        # Sample two points
        pickPoints = [random.uniform(0, le), random.uniform(0, le)]
        pickPoints.sort()
        #  print(pickPoints)
        first = GetTargetPoint(path, pickPoints[0])
        #  print(first)
        second = GetTargetPoint(path, pickPoints[1])
        #  print(second)

        if first[2] <= 0 or second[2] <= 0:
            continue

        if (second[2] + 1) > len(path):
            continue

        if second[2] == first[2]:
            continue

        # collision check
        if not LineCollisionCheck(first, second, obstacleList):
            continue

        # Create New path
        newPath = []
        newPath.extend(path[:first[2] + 1])
        newPath.append([first[0], first[1]])
        newPath.append([second[0], second[1]])
        newPath.extend(path[second[2] + 1:])
        path = newPath
        le = GetPathLength(path)

    return path






if __name__ == '__main__':
	global obs, bandera
	obs = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	bandera = False
	try:
		threading.Thread(target=ThreadInputs).start()
		arrancar()
	except rospy.ServiceException:
pass