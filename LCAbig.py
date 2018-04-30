import nef
from numeric import *

def sth(x):
	if x>0.1:
		return (x-.05)
	elif x<-0.1:
		return (x+.05)
	else:
		return 0

def sthn(x):
	return [sth(y) for y in x]

def zero(m,n):
    # Create zero matrix
    new_matrix = [[0 for row in range(n)] for col in range(m)]
    return new_matrix


def multmin(matrix1):
	# Matrix multiplication
	new_matrix = zero(len(matrix1),len(matrix1))
	for i in range(len(matrix1)):
		for j in range(len(matrix1)):
			if(i != j):
				for k in range(len(matrix1[0])):
					new_matrix[i][j] -= matrix1[i][k]*matrix1[j][k]

	return new_matrix


def transpose(matrix1):
	new_matrix = zero(len(matrix1[0]),len(matrix1))
	for i in range(len(matrix1)):
		for j in range(len(matrix1[0])):
			new_matrix[j][i] = matrix1[i][j]

	return new_matrix

f = open('smclips.txt')

num_images = 200
clippre = []
for img in range(num_images):
        line = f.readline()
	imgpre=[]
	first = 0
	for char in range(len(line)):
		if (line[char] == ' '):
			last = char
			imgpre.append(round(float(line[first:last]),4))
			first = char+1
		
	clippre.append(imgpre)
		
f.close()


f = open('smdictionary.txt')

num_dict = 128*8
PHI_pre = []
for img in range(num_dict):
        line = f.readline()
	dictpre=[]
	first = 0
	for char in range(len(line)):
		if (line[char] == ' '):
			last = char
			dictpre.append(round(float(line[first:last]),4))
			first = char+1
	#print img	
	PHI_pre.append(dictpre)	
f.close()

f = open('smrecur.txt')

recur_pre = []
for img in range(num_dict):
        line = f.readline()
	dictpre=[]
	first = 0
	for char in range(len(line)):
		if (line[char] == ' '):
			last = char
			dictpre.append(round(float(line[first:last]),4))
			first = char+1
		
	recur_pre.append(dictpre)	
f.close()


class MyInput(nef.SimpleNode):
	def origin_value(self):
		t=int(self.t_start/.1)
		return clippre[t]



dict = array(PHI_pre)
numNodes = len(dict)
numInputs = len(dict[0])

recur = array(recur_pre)

net=nef.Network('LCA',quick=True)
#net.add_to(world)

#input=net.make_input('input',clippre[15])
myinput=MyInput('input')
net.add(myinput)
neuron=net.make_array('neurons',30,numNodes,intercept=(0,1))
outs=net.make('decoders',1,numInputs,mode='direct')
neuron_value=net.make('neuron_value',1,numNodes,mode='direct')

#net.connect(input,neuron,transform=dict)
net.connect(myinput.getOrigin('value'),neuron,transform=dict)
net.connect(neuron,neuron,transform=recur,func=sthn)
net.connect(neuron,outs,transform=dict.T,func=sthn,pstc=.001)
net.connect(neuron,neuron_value,func=sthn,pstc=.001)


net.view(play=.2)


#sim=net.network.simulator
#sim.run(0,1,0.001)

#print neuron_value.getOrigin('X').getValues().getValues()
#print outs.getOrigin('X').getValues().getValues()
