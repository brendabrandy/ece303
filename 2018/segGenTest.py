#!/usr/bin/env python  

import array
import numpy as np
import struct

class TCPsegment:

    def __init__(self, srcport, destport, seqnum, acknum, headerlen=5,
                 urg=0, ack=0, psh=0,rst=0, syn=0, fin=0, rcvwin= 0,
                 urgdataptr=0, data=""):
        # Initializer, only four parameters are required: srcport, destport,
        # seqnum and acknum, other parameters, if not specified, are initialized 
        # to their default values
        self.header = "" 
        self.tcp_seg_bitstr = bytearray()
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
        self.checksum = 0        # 16 bit string
        self.urgdataptr = urgdataptr              # in bitstring format
        # do not change options directly, call set_options to change
        # options
        self.options = bytearray()          # in bit string format
        self.data = data                # in bit string format

    # Update tcp_seg_bitstr
    def pack(self):
        # First assemble the header
        # NOTE: 256 = 2**8
        # Use little endian in encoding every 32 bits
        mod = 256
        self.header = bytearray()
        # >H represents big endian for 2 bytes
        # >L represents big endian for 4 bytes
        # >c represents big endian for 1 byte
        self.header[0:2]  = struct.pack('>H', self.srcport)         # srcport: 2 bytes
        self.header[2:4]  = struct.pack('>H', self.destport)        # destport: 2 bytes
        self.header[4:8]  = struct.pack('>L', self.seqnum)          # seqnum: 4 bytes
        self.header[8:12] = struct.pack('>L', self.acknum)          # acknum: 4 bytes
        # 4 bit header + 4 bit padding
        self.header.append(struct.pack('>B', (self.headerlen << 4)))
        flags = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + \
                (self.ack << 4) + (self.urg << 5)       
        self.header.append(struct.pack('>B', flags))  # 2 bit padding + 6 bit flags
        self.header[14:16] = struct.pack('>H', self.rcvwin)         # rcvwin: 2 bytes
        self.header[16:18] = struct.pack('>xx')     # checksum : 2 bytes (set to zero)
        self.header[18:20] = struct.pack('>H', self.urgdataptr)     # urgdataptr: 2 bytes
        self.tcp_seg_bitstr = bytearray(self.header+self.options+self.data)
        self._make_checksum()
        return self.tcp_seg_bitstr 
    
    # update options and headerlen
    # previous options will be overwritten 
    def set_options(self, options):
        # TODO: Update this to accept byte arrays!
        option_size = len(options)/8    # option size in bytes
        # 5 is the original header length without any options
        self.headerlen = 5 + option_size
        self.options = options

    # unpacks a string and populates the class 
    # make sure the checksum is correct before you do such a thing
    def unpack(self, seg):
        self.srcport = struct.unpack('>H', seg[0:2])[0]
        self.destport = struct.unpack('>H', seg[2:4])[0]
        self.seqnum = struct.unpack('>L', seg[4:8])[0]
        self.acknum = struct.unpack('>L', seg[8:12]) [0]
        self.headerlen = struct.unpack('>B', chr(seg[12]))[0] >> 4
        flags = struct.unpack('>B', chr(seg[13]))[0] 
        self.urg = (flags >> 5) % 2
        self.ack = (flags >> 4) % 2
        self.psh = (flags >> 3) % 2
        self.rst = (flags >> 2) % 2
        self.syn = (flags >> 1) % 2
        self.fin = flags % 2 
        self.rcvwin = struct.unpack('>H', seg[14:16])[0]
        self.checksum = struct.unpack('>H', seg[16:18])[0]
        self.urgdataptr = struct.unpack('>H', seg[18:20])[0]
        # headerlen is encoded as 32 bit words, hence data is whatever headerlen is
        # times 4 going all the way to the end
        self.data = seg[self.headerlen*4:]

    # generate a checksum for the packet
    # private function: DO NOT CALL OUTSIDE THE CLASS
    # when the checksum is generated, the checksum portion is assumed to be zero
    def _make_checksum(self):
        self.checksum = 0
        # Pad the segment so its 16bit aligned (4 hex numbers)
        num_pad = len(self.tcp_seg_bitstr) % 2
        fmt = 'x'*num_pad
        self.tcp_seg_bitstr += struct.pack(fmt)
        for i in range(0, len(self.tcp_seg_bitstr),2):
            # add 16 bits to the checksum every time
            temp = struct.unpack('>H', self.tcp_seg_bitstr[i:i+2])
            self.checksum += temp[0]
        self.checksum = self.checksum % (2 ** 16)          # wrap around the checksum
        self.checksum = (2 ** 16-1) - self.checksum     # take 1's complement
        # if segment is padded, remove the padding
        self.tcp_seg_bitstr = self.tcp_seg_bitstr[0:len(self.tcp_seg_bitstr)-num_pad]
        # update header and tcp_seg_bitstr
        self.header[16:18] = struct.pack('>H',self.checksum)
        self.tcp_seg_bitstr = bytearray(self.header+self.options+self.data)

    # check checksum string and make sure it is correct
    # if they all add to 1111 1111 1111 1111, then it must be correct
    def check_checksum(self, cs):
        check = 0 
        num_pad = len(cs) % 2
        fmt = 'x'*num_pad
        cs_test = cs + struct.pack(fmt)
        for i in range(0, len(cs_test),2):
            # add 16 bits to the checksum everytime
            temp = struct.unpack('>H', cs_test[i:i+2])
            check += temp[0]
        
        check = check % (2**16)
        if (check == (2**16-1)):
            return True
        else:
            return False

if __name__ == "__main__":
    # Test segment
    # srcport = 1000
    # destport = 2000
    # seqnum = 3000
    # acknum = 400
    # data = ASCII values for 'DATA'
    c1 = TCPsegment(1000,2000,3000,4000, fin=1, syn=1, data=bytearray([68,65,84,65]))
    assert c1.srcport == 1000
    assert c1.destport == 2000
    assert c1.seqnum == 3000
    assert c1.acknum == 4000
    assert c1.syn == 1
    assert c1.fin == 1
    assert c1.psh == 0
    assert c1.rst == 0
    assert c1.ack == 0
    assert c1.urg == 0
    tcp_seg_test = c1.pack()
    c2 = TCPsegment(0,0,0,0)
    assert c2.check_checksum(tcp_seg_test)
    c2.unpack(tcp_seg_test)
    assert c2.srcport == 1000
    assert c2.destport == 2000
    assert c2.seqnum == 3000
    assert c2.acknum == 4000
    assert c2.syn == 1
    assert c2.fin == 1
    assert c2.psh == 0
    assert c2.rst == 0
    assert c2.ack == 0
    assert c2.urg == 0
    assert c2.data == bytearray([68,65,84,65])
