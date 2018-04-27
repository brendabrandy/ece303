import receiver
import random
import socket
import time
from segGenTest import TCPsegment

# QUESTION: DO WE NEED TO DEAL WITH MULTIPLE SENDERS AND RECEIVERS OVER THE SAME CHANNEL

# assumes receiver is client
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
        self.rcv_pkt = TCPsegment(0,0,0,0)         # received packet
        self.snd_pkt = TCPsegment(0,0,0,0) # make the segment in initializer
        # choose receiver isn. 5000 is an arbitrary number, can be subjected to 
        # change. NOTE: need to deal with this overflowing
        self.seqnum = 0 # receiver sequence number (SEQ Number)
        self.acknum = 0 # sender sequence number (ACK Number)
        self.closing_timeout = 180      # arbitrarily set to 3 minutes
        self.isn = 2000
        self.start = time.time()
    	#initialize
        prev_seq = 999
        prev_num_bytes = 1
           

    # Should override BogoReceiver.receiver() function
    def receive(self):
        # TODO: How will the sender know that the ACK number of the receiver
        # We need some syn thingies
        # TODO: How will the receiver know that the sender stops sending?
        self.seqnum = self.isn
        # f = open("rcv_file", 'wb')
        while(True):
                
            # A connection is established between the sender and receiver
            # can start sending data now
            while(True):
                try:
                    rcv_seg = self.simulator.u_receive()
                    # if the checksum and sequence number is correct
                    # send an ACK back
                    if (not self.rcv_pkt.check_checksum(rcv_seg)):
                        self.start = time.time()
                    else:
                        self.rcv_pkt.unpack(rcv_seg)
                        break
                except socket.timeout:
                    if (len(self.snd_pkt.tcp_seg_bitstr) != 0):
                        self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                    if (time.time() - self.start > self.closing_timeout) :
                        # Very long timeout -- 3 minutes
                        return
            # send an ACK back
            num_bytes = len(self.rcv_pkt.data)
            data = self.rcv_pkt.data
            f.write(data)
            self.seqnum = self.isn
            self.acknum = self.rcv_pkt.seqnum + num_bytes 
            self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
            bitstr = self.snd_pkt.pack()
            self.simulator.u_send(bitstr)
            self.start = time.time()
            
            #---------------NEW CODE ---------------------------------------------------  
            #Initialize: see lines 26, 27
            #Go Back N
            num_bytes = len(self.rcv_pkt.data)            
            expect_seq = prev_seq + prev_num_bytes; #how to handle case if the first packet is in wrong order (aka not packet 0)? 
                                                    #sol: make init prev_seq 999 and init prev_num_bytes +1 so first expected_seq
                                                    #is 1000, but first prev_seq is not.                                                  
            if expect_seq == rcv_pkt.seqnum:
                #send ack back
                data = self.rcv_pkt.data
                f.write(data)
                self.seqnum = self.isn
                self.acknum = self.rcv_pkt.seqnum  
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(bitstr)
                self.start = time.time()
                #update  
                prev_seq = self.rcv_pkt.seqnum
                prev_num_bytes = num_bytes
            else
	            #disgard packet i.e. don't unpack or write data to file
	            #send dupack
	            self.seqnum = self.isn
                self.acknum = prev_seq
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(bitstr)
                self.start = time.time()
            #----------------------------------------------------------------------
          
           

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
    for w in rolling_window(xrange(6), 3):
        print w