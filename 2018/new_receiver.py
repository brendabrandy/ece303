import receiver
import random
import socket
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
        self.timeout = 10
        self.isn = 2000
    # Should override BogoReceiver.receiver() function
    def receive(self):
        # TODO: How will the sender know that the ACK number of the receiver
        # We need some syn thingies
        # TODO: How will the receiver know that the sender stops sending?
        self.acknum = self.isn
        while(True):
                
            # A connection is established between the sender and receiver
            # can start sending data now
            print ("SEQ: " + str(self.seqnum))
            print ("ACK: " + str(self.acknum))
            while(True):
                try:
                    rcv_seg = self.simulator.u_receive()
                    # if the checksum and sequence number is correct
                    # send an ACK back
                    if (not self.rcv_pkt.check_checksum(str(rcv_seg))):
                        print ("(Receiver) Checksum Wrong!")
                    else:
                        self.rcv_pkt.unpack(rcv_seg)
                        break
                except socket.timeout:
                    print ("(Receiver) Timeout! Resend ACK")
                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                    
            # send an ACK back
            num_bytes = len(self.rcv_pkt.data)/8
            data = self.rcv_pkt.data
            self.seqnum = self.isn
            self.acknum = self.rcv_pkt.seqnum + num_bytes 
            self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                      self.seqnum, self.acknum)
            bitstr = self.snd_pkt.pack()
            print bitstr
            self.simulator.u_send(bitstr)

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
