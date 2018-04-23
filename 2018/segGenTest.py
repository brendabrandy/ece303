#!/usr/bin/env python  

import array
import numpy as np


class TCPsegment:

    def __init__(self, srcport, destport, seqnum, acknum, headerlen=5,
                 urg=0, ack=0, psh=0,rst=0, syn=0, fin=0, rcvwin= 0,
                 urgdataptr="0"*16, data=""):
        # Initializer, only four parameters are required: srcport, destport,
        # seqnum and acknum, other parameters, if not specified, are initialized 
        # to their default values
        self.header = "" 
        self.tcp_seg_bitstr = ""
        self.srcport = srcport          # 16-bit integer
        self.destport = destport        # 16-bit integer
        self.seqnum = seqnum            # 32-bit integer
        self.acknum = acknum            # 32-bit integer
        self.headerlen = headerlen      # 16-bit integer
        self.urg = urg                  # either 0 or 1
        self.ack = ack                  # either 0 or 1
        self.psh = psh                  # either 0 or 1
        self.rst = rst                  # either 0 or 1
        self.syn = syn                  # either 0 or 1
        self.fin = fin                  # either 0 or 1
        self.rcvwin = rcvwin            # 16-bit integer
        # do not alter checksum directly, call make_checksum to 
        # update the checksum
        self.checksum = "0000000000000000"        # 16 bit string
        self.urgdataptr = urgdataptr              # in bitstring format
        # do not change options directly, call set_options to change
        # options
        self.options = ""          # in bit string format
        self.data = data                # in bit string format

    # Update tcp_seg_bitstr
    def pack(self):
        # First assemble the header
        self.header = ""
        self.header += '{0:016b}'.format(self.srcport)
        self.header += '{0:016b}'.format(self.destport)
        self.header += '{0:032b}'.format(self.seqnum)
        self.header += '{0:032b}'.format(self.acknum)
        self.header += '{0:04b}'.format(self.headerlen)
        self.header += "000000" # unused space
        self.header += str(self.urg)
        self.header += str(self.ack)
        self.header += str(self.psh)
        self.header += str(self.rst)
        self.header += str(self.syn)
        self.header += str(self.fin)
        self.header += '{0:016b}'.format(self.rcvwin)
        self.header += self.checksum
        self.header += self.urgdataptr
        self.tcp_seg_bitstr = "0b"+self.header + self.options + self.data
        return self.tcp_seg_bitstr 
    
    # update options and headerlen
    # previous options will be overwritten 
    def set_options(self, options):
        option_size = len(options)/8    # option size in bytes
        # 5 is the original header length without any options
        self.headerlen = 5 + option_size
        self.options = options

    # unpacks a string and populates the class 
    # make sure the checksum is correct before you do such a thing
    def unpack(self, input_str):
        if (input_str[0:2] == "0b"):
            self.tcp_seg_bitstr = input_str[2:] #Strip away 0b from input_str
        # populates the class
        self.srcport = int(self.tcp_seg_bitstr[0:16],2)
        self.destport = int(self.tcp_seg_bitstr[16:32],2)
        self.seqnum = int(self.tcp_seg_bitstr[32:64],2)
        self.acknum = int(self.tcp_seg_bitstr[64:96],2)
        # TODO: how to set header length
        self.urg = int(self.tcp_seg_bitstr[106],2)
        self.ack = int(self.tcp_seg_bitstr[107],2)
        self.psh = int(self.tcp_seg_bitstr[108],2)
        self.rst = int(self.tcp_seg_bitstr[109],2)
        self.syn = int(self.tcp_seg_bitstr[110],2)
        self.fin = int(self.tcp_seg_bitstr[111],2)
        self.headerlen = int(self.tcp_seg_bitstr[96:100],2)
        self.rcvwin = int(self.tcp_seg_bitstr[112:128],2)
        self.checksum = self.tcp_seg_bitstr[128:144]
        self.urgdataptr = self.tcp_seg_bitstr[144:160]
        if self.headerlen != 5:
            self.options = self.tcp_seg_bitstr[5*32:self.headerlen*32]
        if input_str[self.headerlen*32:] :
            self.data = self.tcp_seg_bitstr[self.headerlen*32:]

"""
class TCPsegmentDecode:

    def __init__(self, inputTCPsegStr):
        inputTCPsegStr = inputTCPsegStr[2:]
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
        if self.headerlen == 5:
            self.Options = None
        else:
            self.Options = inputTCPsegStr[5*32:self.headerlen*32]
        if not inputTCPsegStr[self.headerlen*32:] :
            self.DataBits = None
            self.Data = None
        else:    
            self.DataBits = inputTCPsegStr[self.headerlen*32:]
            self.Data = int(self.DataBits,2)
    
"""
if __name__ == "__main__":
    #### Testing Encoder ###
    c1 = TCPsegment(88,55)
    c1.rcv_win = 20
    c1.ack = 1
    print c1.headerlen
    c1.SetOptions('001110101111000111111111111111111111111111110111111100000000') 
    # have to options then data, in that order. Can modify this later.
    # if don't want Options section, don't declare it 
    print c1.headerlen
    c1.data = bin(31980)[2:]  #payload here
    print '-------------------------------------------------------------------------------------'
    c1.pack()
    print c1.tcp_seg_bitstr

