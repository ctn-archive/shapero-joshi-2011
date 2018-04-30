import nef
from numeric import *
import socket, sys, time
from struct import *
import shelve

fmt_string = '!iI'
stride = 8
y_offset = 8
y_length = 8
x_offset = 1
x_length = 8

HOST = "127.0.0.1"
PORT = str(9000)
BUFFSIZE = 2048
ADDR = (HOST,PORT)


class event:
    def __init__(self,addr,time):
        self.time = time
        self.x = 127 - ((addr>>x_offset)&2**(x_length-1)-1)
        self.y = (addr>>y_offset)&2**(y_length-1)-1
        self.intensity = 1 - (addr & 1)
    def __repr__(self):
        return repr((self.intensity,self.x,self.y,self.time))

# Use the below for command line inputs
#host = sys.argv[1]
#textport = sys.argv[2]

host = HOST
textport = PORT



def sth(x):
        th=.6
	if x>th:
		return (x-th)
	elif x<-th:
		return (x+th)
	else:
		return 0

def sthn(x):
	return [sth(y) for y in x]

def absn(x):
        return [abs(sth(y)) for y in x]

def rect(x):
    if x>0:
        return x
    else:
        return 0

def rectn(x):
    return [rect(y) for y in x]

def zero(m,n):
    # Create zero matrix
    new_matrix = [[0 for row in range(n)] for col in range(m)]
    return new_matrix

def eye(n):
    new_matrix = [[(row == col) for row in range(n)] for col in range(n)]
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

db=shelve.open('data_sal')
if (db.has_key('dict')):
    PHI_pre = db['dict']
    recur_pre = db['recur']
    salrec_pre = db['salrec']
else:
    f = open('thdictionary.txt')

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

    f = open('threcur.txt')

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

    f = open('salrecur.txt')

    salrec_pre = []
    for img in range(num_dict):
        line = f.readline()
	dictpre=[]
	first = 0
	for char in range(len(line)):
		if (line[char] == ' '):
			last = char
			dictpre.append(round(float(line[first:last]),4))
			first = char+1
		
	salrec_pre.append(dictpre)

    f.close()
    
    db['dict']=PHI_pre
    db['recur']=recur_pre
    db['salrec']=salrec_pre

db.close()
	
dict = array(PHI_pre)
recur = array(recur_pre)
salrec = array(salrec_pre)


numNodes = len(dict)
numInputs = len(dict[0])



class MyInput(nef.SimpleNode):
	def origin_value(self):
		out_pre = zero(1,576)
		out = out_pre[0][:]
		compress = 2
		if(self.t_start < .11):
                    logtime = 12
                    self.oldevents = logtime*[[]]
                else:
                    try:
			data, addr = sock.recvfrom(BUFFSIZE)
		    except socket.error:
                        self.oldevents[1:]=self.oldevents[:-1]
                        self.oldevents[0]=[]
                    else:
    			#print addr
		        #print "sanity check:", addr[1]/4, (len(data)-4)/8, (len(data)-4)%8
    			#if (((len(data)-4)%8 != 0)or ((len(data)-4)/8 ==0 )):
                        #print "There is an error in the format of the packets sent"
                        #sys.exit(1)
    			tind = unpack("!i",data[0:4])
    			# print tind
    			event_list = []    
    			for iter in range(4,len(data)-4,stride):
                                message = unpack(fmt_string,data[iter:(iter+stride)]) 
                                #print message
                                event_list.append(event(message[0],message[1]))
                                
        			self.oldevents[1:]=self.oldevents[:-1]
                        self.oldevents[0]=event_list
        			
                for evlist in self.oldevents:
                    for events in evlist:
                        x = int(events.x/compress)
                        y = int(events.y/compress)
                        outind = int(x+24*(24-y-1))
                        #print x, y, outind
                        if (x < 24 and y < 24 and x > -1 and y > -1):
                                #print events.time
                                out[outind] = 2*int(events.intensity)-1
		return out


lif = array(eye(numInputs))*0.5

net=nef.Network('LCA',quick=True)
#net.add_to(world)

#input=net.make_input('input',clippre[15])
myinput=MyInput('input')
net.add(myinput)
#infilter=net.make('infilter',1,numInputs,mode='direct')
neuron=net.make_array('neurons',20,numNodes,intercept=(0,1))
decoders=net.make('decoders',1,numInputs,mode='direct')
neuron_value=net.make('neuron_value',1,numNodes,mode='direct')
salience=net.make_array('salience',20,numNodes,intercept=(0,1))
sal_decode=net.make('sal_decoder',1,numInputs,mode='direct')

#net.connect(input,neuron,transform=dict)
#net.connect(myinput.getOrigin('value'),infilter,pstc=.0005)
#net.connect(infilter,infilter,transform=lif,pstc=.0005)
net.connect(myinput.getOrigin('value'),neuron,transform=dict,pstc=.002)
net.connect(neuron,neuron,transform=recur,func=sthn,pstc=.002)
net.connect(neuron,decoders,transform=dict.T,func=sthn,pstc=.0005)
net.connect(neuron,neuron_value,func=sthn,pstc=.0005)
net.connect(neuron,salience,func=absn,pstc=.0005)
net.connect(salience,salience,transform=salrec,func=rectn,pstc=.0005)
net.connect(salience,sal_decode,transform=dict.T,func=rectn,pstc=.0002)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST,int(PORT) ))
sock.settimeout(.001)

net.view(play=0.1)

#sim=net.network.simulator
#sim.run(0,1,0.001)

#print neuron_value.getOrigin('X').getValues().getValues()
#print outs.getOrigin('X').getValues().getValues()
