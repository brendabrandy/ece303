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
        self.header += "0"*16
        self.header += '{0:016b}'.format(self.rcvwin)
        self.header += self.urgdataptr
        if (len(self.data) % 16 != 0):
            # zero pad data if data is not 16-bit aligned
            self.data += "0"*(16-(len(self.data)%16))
        self.tcp_seg_bitstr = self.header + self.options + self.data
        self._make_checksum()
        self.tcp_seg_bitstr = bytearray(self.tcp_seg_bitstr)
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

    # generate a checksum for the packet
    # when the checksum is generated, the checksum portion is assumed to be zero
    def _make_checksum(self):
        for i in range(0,len(self.tcp_seg_bitstr),16):
            # add every 16bit word with wrap around
            self.checksum = self.bin_add_1(self.checksum, self.tcp_seg_bitstr[i:i+16])
        self.tcp_seg_bitstr = self.tcp_seg_bitstr[0:128] + self.ones_comp(self.checksum) \
                                + self.tcp_seg_bitstr[144:]
        self.header = self.header[0:128] + self.ones_comp(self.checksum)\
                            + self.tcp_seg_bitstr[144:]

    # check checksum string and make sure it is correct
    # if they all add to 1111 1111 1111 1111, then it must be correct
    def check_checksum(self):
        temp_checksum = "0"*16
        for i in range(0, len(self.tcp_seg_bitstr),16):
            temp_checksum = self.bin_add_1(temp_checksum, self.tcp_seg_bitstr[i:i+16])
        print temp_checksum
        if (temp_checksum == "1"*16):
            return True
        else:
            return False

    # function for converting ones complement
    # @param n1 is the string for conversion
    def ones_comp(self, n1):
        final = ""
        for i in n1:
            if (i == '1'):
                final += '0'
            else:
                final += '1'
        return final

    # function for binary addition
    # @param n1 is first string
    # @param n2 is second string
    def bin_add_1(self, n1, n2):
        mod_val = 2**16
        res = int(n1,2) + int(n2,2)
        fin_str = '{0:016b}'.format(res % mod_val)
        return fin_str

if __name__ == "__main__":
    c1 = TCPsegment(0,0,0,0)
    # TEST: CHECKSUM with example in book
    # add1 = 1011101110110101
    # add2 = 0100101011000010 
    add1 = c1.bin_add_1("0110011001100000","0101010101010101")
    add2 = c1.bin_add_1(add1, "1000111100001100")
    if (add1 == "1011101110110101" and add2 == "0100101011000001"):
        print "Test: bin_add_1 pass"
    else:
        print "Test: bin_add_1 fails"
