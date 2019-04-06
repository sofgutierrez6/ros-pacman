#!/usr/bin/python
import rospy
from std_msgs.msg import Float32MultiArray, Float32
from pylab import *
from pynput.keyboard import Key, Listener 
import matplotlib.pyplot as plt
import threading
import time
import sys 

robot = 0

def arrancar():
	rospy.init_node('punto2c', anonymous = True)
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
	crearCuadricula()
	Astar(xfin,yfin)
	try:
		while not rospy.is_shutdown():
			tasa.sleep()
	except rospy.ServiceException as e:
		pass
		
def obstacles(data):
	global obs
	obs = data.data
	
def crearCuadricula():
	global obs, matriz, matNod
	matriz = [[0  for i in range(500)]for j in range(500)]
	matNod = [[Nodo([i , j]) for i in range(500)]for j in range(500)]
	x = [(5+obs[0])/0.1 , (5+obs[1])/0.1 , (5+obs[2])/0.1 , (5+obs[3])/0.1 , (5+obs[4])/0.1]
	y = [(5+obs[5])/0.1 , (5+obs[6])/0.1 , (5+obs[7])/0.1 , (5+obs[8])/0.1 , (5+obs[9])/0.1]
	r = [obs[10]/0.1 , obs[11]/0.1 , obs[12]/0.1 , obs[13]/0.1 , obs[14]/0.1]
	for i in range(len(x)):
		matriz[int(x[i])][int(y[i])] = 1
		for j in range(int(x[i]-r[i]-robot)-1, int(x[i]+r[i]+robot+1)):
			for k in range(int(y[i]-r[i]-robot)-1, int(y[i]+r[i]+robot+1)):
				dist = np.linalg.norm(np.array([x[i],y[i]]) - np.array([j+0.5,k+0.5]))
				if dist <= r[i]+robot:
					matriz[j][k] = 1
					x.append(j)
					y.append(k)
	for nod in matNod:
		listN = nod
		for nod2 in listN:
			posN = nod2.pos
			if (matriz[posN[0]][posN[1]] == 0):
				for i in range(posN[0] - 1, posN[0] + 2 ,1):
					for j in range(posN[1] - 1, posN[1] + 2 ,1):
						if (i >= 0 and i <= 499 and j >= 0 and j <= 499):
							if (matriz[i][j] == 0 and not ((abs(i - posN[0]) + abs(j - posN[1])) == 0)):
								nod2.agregarVecinos(matNod[i][j])
	if (bandera):
		return False
	print 'Mapa'
				
		
def ThreadInputs():
	with Listener(on_press = keypress) as listener:
		listener.join()
		
def keypress(key):
	global bandera
	while True:
		if key == Key.esc:
			bandera = True 	##Se usa la tecla Esc para terminar los diferentes hilos implementados
			return False

class Nodo:
	def __init__(self, pos):
		self.pos = pos
		self.coord = [-5 + (0.1*pos[0]) , -5 + (0.1*pos[1])]
		self.costo = 1000000000
		self.vecinos = []
		self.objetivo = False
		self.actual = False
		
	def defHeu(self, pos_f):
		self.h = math.sqrt((self.coord[0]-pos_f[0])**2 + (self.coord[1]-pos_f[1])**2) 
		return self.h
		
	def asignarPadre(self, padre):
		self.padre = padre
	
	def cambiarCosto(self, costo):
		self.costo = costo
	
	def agregarVecinos(self, vecino):
		self.vecinos.append(vecino)
		
	def esActual(self, actual):
		self.actual = actual
		
	def esObjetivo(self, objetivo):
		self.objetivo = objetivo
		
		
def Astar(xfin,yfin):
	global matNod, bandera
	pos_f = [xfin,yfin]
	goal = buscarNodo(xfin,yfin)
	goal.esObjetivo(True)
	nodos = []
	for fil in matNod:
		for nod in fil:
			nodos.append(nod)
	explorados = []
	actual = buscarNodo(0,0)
	actual.asignarPadre(None)
	actual.cambiarCosto(actual.defHeu(pos_f))
	costos = {actual : actual.costo}
	nodos.remove(actual)
	explorados.append(actual)
	costos[actual] = 0
	while not actual.objetivo and not bandera:
		vecinos = actual.vecinos
		for vecino in vecinos:
			costo = costos[actual] + 0.1
			if vecino not in explorados or costo < costos[vecino]:
				costos[vecino] = costo
				vecino.cambiarCosto(costo + vecino.defHeu(pos_f))
				explorados.append(vecino)
				vecino.asignarPadre(actual)
		actual = buscarMejor(nodos)
		nodos.remove(actual)
	rutax = []
	rutay = []
	
	while actual.padre != None:
		coord2 = actual.coord
		rutax.append(coord2[0])
		rutay.append(coord2[1])
		actual = actual.padre
	
	plt.plot(rutax, rutay)
	plt.show()
def buscarNodo(x,y):
	global matNod
	a = round((5+x)/0.1)
	b = round((5+y)/0.1)
	for fil in matNod:
		for nod in fil:
			if (nod.pos == [a,b]):
				return nod
				
def buscarMejor(nodos):
	cost = 10000000
	best = None
	for nod in nodos:
		if(nod.costo < cost):
			cost = nod.costo
			best = nod
	return best
	
if __name__ == '__main__':
	global obs, bandera
	obs = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	bandera = False
	try:
		threading.Thread(target=ThreadInputs).start()
		arrancar()
	except rospy.ServiceException:
		pass