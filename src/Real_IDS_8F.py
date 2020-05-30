#cmd = "ra  -M noman -c, -M dsrs='-arg' -L -1 -S 127.0.0.1 -s"
#cmdshell = "rabins -B 0.25s -M time 0.25s noman -c, -m matrix proto -S localhost -L -1 -s \"-stime +0rank -sport -dport -flgs -dir -pkts -bytes -state +4seq +7state  +stddev +min +mean +drate +srate +max\""
cmdshell = "ra -M noman -c, -S 127.0.0.1 -L -1 -s rank ltime proto saddr sport daddr dport state mean min max srate drate"
#arglist2 = cmd.split()
#arglist = arglist2 +['"-stime +0rank -flgs -dir -pkts -bytes -state +7seq +10state  +stddev +min +mean +drate +srate +max"']

import sys
from subprocess import PIPE, Popen, run
from threading  import Thread
from collections import deque, defaultdict
import time
import datetime
import joblib
import numpy as np

import atexit

from tensorflow.keras.models import load_model
model = load_model('./keras_model/UNSW_BoT-IoT_8F/Scan_Keras_8F_9L.h5')
# For some reason, Service scan model is also **somewhat** work to detect Dos model, but not vice versa.
scaler = joblib.load('./keras_model/UNSW_BoT-IoT_8F/minmax_KerasF1-8F.jlb')

THRESHOLD = 0.5

bl_IP = set()

srcipq = deque(maxlen = 100)
destipq = deque(maxlen = 100)
srciph = 0
destiph = 0

conf_mat = np.zeros((2,2),dtype=np.uint32)
attack_ip = "192.168.255.174" # Change to actual attacking IP for correct Confusion matrix.

FP_ELM_TH = 10
LastIP = "0.0.0.0"
Count = 0
blkinit = 0

try:
    from queue import Queue, Empty, Full
except ImportError:
    from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def exithand():
	run(["util/resetyml.py"])
	print(conf_mat)
	print("blocking_initate:")
	print(blkinit)

def count(ip,result):
	#count Ip
	rc = 1 if ip == attack_ip else 0
	conf_mat[int(rc)][int(result)] += 1

def check_IP(ip):
	global LastIP
	global Count
	global blkinit
	if ip == LastIP:
		Count += 1
		print("Count: "+str(Count))
		if Count > FP_ELM_TH:
			if(ip not in bl_IP):
				bl_IP.add(ip)
				blkinit = datetime.datetime.now()
				print("Blocking: " + ip)
				run(["util/yml.py",ip])
	else:
		LastIP = ip
		Count = 1
		

def listpreprocess(inlist):
	#State int encoding
	statenum = defaultdict(lambda:0,{'RST':1,'CON':2,'REQ':3,'INT':4,'URP':5,'FIN':6,'ACC':7,'NRS':8,'ECO':9,'TST':10,'MAS':11})
	inlist[7] = statenum[inlist[7]]

	#Time truncate
	inlist[1] = inlist[1][:-6]

	inlist.append(None)
	inlist.append(None)
	srciph = hash(inlist[1]+inlist[3])
	destiph = hash(inlist[1]+inlist[5])
	srcipq.appendleft(srciph)
	destipq.appendleft(destiph)
	inlist[-2] = str(srcipq.count(srciph))
	inlist[-1] = str(destipq.count(destiph))
	#print(inlist)

def process(inlist):
	key = inlist[0:7]
	value = list(map(float,inlist[7:]))
	#print(str(key)+str(value))
	np_x = np.array(value).reshape(1,8)
	np_x = scaler.transform(np_x)
	#print(np_x)
	#result = model.predict_classes(np_x)[0][0]
	result = model.predict_proba(np_x)[0][0]
	resultint = 1 if result >= THRESHOLD else 0
	count(key[3],resultint)
	print(key[3],end=" ")
	print("Predicted: "+"{:.2f}".format(result))
	if resultint: check_IP(key[3])
	else: Count = 0


def enqueue_output(out, queue):
    for line in iter(out.readline,''):
        try: queue.put_nowait(line)
        except Full:
            drop = queue.get()
            pass
    out.close()	

p = Popen(cmdshell, stdout=PIPE,shell=True, bufsize=1, close_fds=ON_POSIX,universal_newlines=True)
q = Queue(maxsize=10)
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()
atexit.register(exithand)

while(True):
# read line without blocking
	#time.sleep(0.002)
	try:  line = q.get(timeout = 1) # or q.get(timeout=.1)
	except Empty:
		pass
	else: # got line
		aflow = line.strip().split(',')
		#startt = time.time()
		listpreprocess(aflow)
		#mid = time.time()
		process(aflow)
		#end = time.time()
		#print('time:'+str(mid-startt)+','+str(end-mid))