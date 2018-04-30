import receiver
import random
import socket
import time
from segGenTest import TCPsegment

class NewReceiver(receiver.BogoReceiver):

    def __init__(self):
        super(NewReceiver, self).__init__()
        self.rcv_pkt = TCPsegment(0,0,0,0)         # received packet
        self.snd_pkt = TCPsegment(0,0,0,0) # make the segment in initializer
        self.seqnum = 0 # receiver sequence number (SEQ Number)
        self.acknum = 0 # sender sequence number (ACK Number)
        # The closing_timeout is for terminating the program, since the 
        # RTT of a normal packet is around 20ms, we set the closing_timeout
        # to a relatively long time -- 10 s
        self.closing_timeout = 10
        # set isn of receiver, which is zero
        self.isn = 0
        self.start = time.time()
    	#initialize
        self.prev_seq = 0
        self.prev_num_bytes = 0
           

    # Should override BogoReceiver.receiver() function
    def receive(self):
        # set starting sequence number to isn
        self.seqnum = self.isn
        # arbitrarily set socket timeout to 500ms
        self.simulator.rcvr_socket.settimeout(0.5)
        # Open file to write data
        f = open("rcv_file", 'wb')
        
        # while loop for general reception of packets
        while(True):
            
            # while loop for receiving ONE packet
            while(True):
                try:
                    rcv_seg = self.simulator.u_receive()
                    # if the checksum and sequence number is correct
                    # send an ACK back
                    if (not self.rcv_pkt.check_checksum(rcv_seg)):
                        # if the checksum is incorrect
                        # restart timer and try to receive another packet
                        self.start = time.time()
                    else:
                        # else unpack the packet
                        self.rcv_pkt.unpack(rcv_seg)
                        
                        if (self.rcv_pkt.destport == self.inbound_port):
                            # if the packet is meant for the port, proceed
                            # break out of the receive loop for processing
                            break
                except socket.timeout:
                    if (len(self.snd_pkt.tcp_seg_bitstr) != 0):
                        # if there is a previously sent packet, 
                        # resend the packet
                        self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                    if (time.time() - self.start > self.closing_timeout) :
                        # Very long timeout -- 10s, terminate
                        # the program
                        print "(Receiver) Receiver closing"
                        f.close()
                        return
            
            # Go Back N
            num_bytes = len(self.rcv_pkt.data)            
            # how to handle case if the first packet is in wrong order (aka not packet 1000) ? 
            expect_seq = self.prev_seq + self.prev_num_bytes 
            # sol: 
            if expect_seq == self.rcv_pkt.seqnum:
                #send ack back
                data = self.rcv_pkt.data
                f.write(data)
                self.acknum = self.rcv_pkt.seqnum + num_bytes 
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(bitstr)
                
                # update previous sequence number
                self.prev_seq = self.rcv_pkt.seqnum
                self.prev_num_bytes = num_bytes
                self.start = time.time()
            else:   
	            # An out of order packet is detected
                # disgard packet i.e. don't unpack or write data to file
	            # send dupack and restart timer again
                self.acknum = expect_seq
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(bitstr)
                self.start = time.time()
           

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
