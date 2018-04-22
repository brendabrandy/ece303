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
        self.TCPseg = self.header
   
    def Data(self, data):
        dataSize = len(data);
        d1 = ((dataSize/32)+1)
        d2 = 32*d1
        data = data.ljust(d2, '2') #2 represents a NaN
        data = map(int, list(data))
        data = np.reshape(data,(d1,32))
        self.TCPseg = np.vstack((self.header,data))

    def Pack(self, inputmatrix):
        flat = inputmatrix.flatten()
        flat = flat[flat!=2]
        self.TCPsegBitStr  = "".join(str(e) for e in flat)
        self.TCPsegBitStr = "0b" + self.TCPsegBitStr

class TCPsegmentDecode:

     def __init__(self, inputTCPsegStr):
        self.inTCP = inputTCPsegStr
        self.SrcPort = int(inputTCPsegStr[0:16],2) 
        self.DestPort = int(inputTCPsegStr[16:32],2)
        self.SeqNum = int(inputTCPsegStr[33:64],2)
        self.AckNum = int(inputTCPsegStr[64:96],2)
        self.headerlen = int(inputTCPsegStr[96:100],2)
        self.URG = inputTCPsegStr[106]
        self.ACK = inputTCPsegStr[107]
        self.PSH = inputTCPsegStr[108]
        self.RST = inputTCPsegStr[109]
        self.SYN = inputTCPsegStr[110]
        self.FIN = inputTCPsegStr[111]
        self.RcvWin = int(inputTCPsegStr[112:128],2)
        self.Checksum = int(inputTCPsegStr[128:144],2)
        self.UrgDataPtr = int(inputTCPsegStr[144:160],2)
        self.Options = inputTCPsegStr[5*32:self.headerlen*32]
        self.DataBits = inputTCPsegStr[self.headerlen*32:]
        self.Data = int(self.DataBits,2)
    

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
    c1.Pack(c1.TCPseg)
    print c1.TCPsegBitStr

    ### Testing Decoder ###
    print '-------------------------------------------------------------------------------------'  
    c2 = TCPsegmentDecode(c1.TCPsegBitStr[2:])  #instantiate here
    print c2.SrcPort
    print c2.DestPort
    print c2.RcvWin
    print c2.URG
    print c2.ACK
    print c2.Options
    print c2.DataBits
    print c2.Data
