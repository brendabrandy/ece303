#!/usr/bin/env python  

import array
import numpy as np


class TCPsegment:     #have to options then data, in that order. Can call other parameters at any time. Can modify this setup later. 

    def __init__(self):
        self.header = np.zeros(shape=(5,32)).astype(int);
        self.headerlen = 5
        self.header[3,0:4] = map( int, list('{0:04b}'.format(self.headerlen)) )
     
    def SrcPort(self, num):
    	self.header[0,0:16] =  map( int, list('{0:016b}'.format(num)) )                
   
    def DestPort(self, num):
    	self.header[0,16:32] = map( int, list('{0:016b}'.format(num)) )   
 
    def SeqNum(self, num):
    	self.header[1,:] = map( int, list('{0:032b}'.format(num)) )   
  
    def AckNum(self, num):
    	self.header[2,:] = map( int, list('{0:032b}'.format(num)) )      
  
    def URG(self, bit):
    	self.header[3,10] = bit
  
    def ACK(self, bit):
    	self.header[3,11] = bit

    def PSH(self, bit):
    	self.header[3,12] = bit

    def RST(self, bit):
    	self.header[3,13] = bit

    def SYN(self, bit):
    	self.header[3,14] = bit

    def FIN(self, bit):
    	self.header[3,15] = bit

    def RcvWin(self, num):
    	self.header[3,16:32] = map( int, list('{0:016b}'.format(num)) )  

    def Checksum(self, bits):
    	self.header[4,0:16] = bits

    def UrgDataPtr(self, bits):
    	self.header[4,16:32] = bits

    def Options(self, options):
		optionsSize = len(options);
		o1 = ((optionsSize/32)+1)
		o2 = 32*o1
		options = options.ljust(o2, '0')
		options = map(int, list(options))	
		options = np.reshape(options,(o1,32))
		self.header = np.vstack((self.header,options))
		self.headerlen = 5+o1
		self.header[3,0:4] = map( int, list('{0:04b}'.format(self.headerlen)) )

    def Data(self, data):
        dataSize = len(data)
        d1 = ((dataSize/32)+1)
        d2 = 32*d1
        data = data.ljust(d2, '2') #2 represents a NaN
        data = map(int, list(data))
        data = np.reshape(data,(d1,32))
        self.TCPseg = np.vstack((self.header,data))


class TCPsegmentDecode:

	 def __init__(self, inputTCPseg):
	 	self.inTCP = inputTCPseg
	 	self.SrcPort = int((''.join(str(e) for e in (inputTCPseg[0,0:16]))),2) 
	 	self.DestPort = int((''.join(str(e) for e in (inputTCPseg[0,16:32]))),2)
	 	self.SeqNum = int((''.join(str(e) for e in (inputTCPseg[1,:]))),2)
	 	self.AckNum = int((''.join(str(e) for e in (inputTCPseg[2,:]))),2)
		self.URG = inputTCPseg[3,10]
	 	self.ACK = inputTCPseg[3,11]
	 	self.PSH = inputTCPseg[3,12]
	 	self.RST = inputTCPseg[3,13]
	 	self.SYN = inputTCPseg[3,14]
	 	self.FIN = inputTCPseg[3,15]
	 	self.RcvWin = int((''.join(str(e) for e in (inputTCPseg[3,16:32]))),2)
	 	self.Checksum = int((''.join(str(e) for e in (inputTCPseg[4,0:16]))),2)
	 	self.UrgDataPtr = int((''.join(str(e) for e in (inputTCPseg[4,16:32]))),2)
	 	self.headerlen = int((''.join(str(e) for e in (inputTCPseg[3,0:4]))),2)
	 	self.Options = inputTCPseg[5:self.headerlen,:]
		rawData = inputTCPseg[self.headerlen:,:]
		vectData = rawData[rawData!=2] #2 represents a NaN
		self.Data = int((''.join(str(e) for e in vectData)),2)

if __name__ == "__main__":
    #### Testing Encoder ###
    c1 = TCPsegment()
    c1.SrcPort(88)
    c1.DestPort(55)
    c1.RcvWin(20)
    c1.ACK(1)
    print c1.headerlen
    c1.Options('001110101111000111111111111111111111111111110111111100000000') 
    # have to options then data, in that order. Can modify this later.
	# if don't want Options section, don't declare it 
    print c1.headerlen
    c1.Data(bin(31980)[2:])  #payload here
    print c1.header #no data appended yet
    print '-------------------------------------------------------------------------------------'
    print c1.TCPseg  #the final TCP Segment! #Note: 2 represents a NaN


    ### Testing Decoder ###
    print '-------------------------------------------------------------------------------------'
    c2 = TCPsegmentDecode(c1.TCPseg)  #instantiate here
    print c2.SrcPort
    print c2.DestPort
    print c2.RcvWin
    print c2.URG
    print c2.ACK
    print c2.Options
    print c2.Data

