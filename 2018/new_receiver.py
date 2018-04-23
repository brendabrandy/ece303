import receiver
import random
import states as TCP_STATE
from segGenTest import TCPsegment

# QUESTION: DO WE NEED TO DEAL WITH MULTIPLE SENDERS AND RECEIVERS OVER THE SAME CHANNEL

# assumes receiver is client
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
        self.state = TCP_STATE.LISTEN
        self.rcv_pkt = TCPsegment(0,0,0,0)         # received packet
        self.snd_pkt = TCPsegment(0,0,0,0) # make the segment in initializer
        # choose receiver isn. 5000 is an arbitrary number, can be subjected to 
        # change. NOTE: need to deal with this overflowing
        self.seqnum = 0 # receiver sequence number (SEQ Number)
        self.acknum = 0 # sender sequence number (ACK Number)

    # Should override BogoReceiver.receiver() function
    def receive(self):
        while(True):
            if (self.state == TCP_STATE.LISTEN):
                # Receiver listening the channel for new packets
                self.simulator.log("(Receiver) Listening for data")
                rcv_seg = self.simulator.u_receive()
                self.rcv_pkt.unpack(rcv_seg)
                # if syn bit is set, go to SYN_RECEIVED state
                if (self.rcv_pkt.syn == 1):
                    self.simulator.log("\t Sender Sequence Number: " +  str(self.rcv_pkt.seqnum))
                    self.state = TCP_STATE.SYN_RECEIVED
                    self.acknum = self.rcv_pkt.seqnum + 1

            elif (self.state == TCP_STATE.SYN_RECEIVED):
                self.simulator.log("(Receiver) Receive SYN")
                # A SYN packet is received from the receiver
                # packs a SYNACK packet to the receiver
                self.seqnum = random.randint(0, 5000)
                self.simulator.log("\t Receiver Sequence Number: " + str(self.seqnum))
                # Crafts SYNACK packet
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,syn=1)
                
                bitstr = self.snd_pkt.pack()
                # Send SYNACK packet over simulator channel
                self.simulator.u_send(bitstr)
                # listens for a confirmation from the receiver
                rcv_seg = self.simulator.u_receive()
                self.rcv_pkt.unpack(rcv_seg)
                # if sequence number and acknowledge number is correct
                # go to ESTABLISHED state
                if (self.rcv_pkt.syn == 0 and 
                        self.rcv_pkt.seqnum == self.acknum
                        and self.rcv_pkt.acknum == self.seqnum+1):
                    self.seqnum = self.seqnum + 1
                    self.state = TCP_STATE.ESTABLISHED

            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between the sender and receiver
                # can staart sending data now
                self.simulator.log("(Receiver) Connection Established")
                self.simulator.log("\t Sequence Number: " + str(self.seqnum))
                self.simulator.log("\t Acknowledge Num: " + str(self.acknum))
                while (True):
                    # if the sequence number and ack number is corrrect
                    if (self.rcv_pkt.seqnum == self.acknum):
                        # send an ACK back
                        num_bytes = len(self.rcv_pkt.data)/8
                        data = self.rcv_pkt.data
                        self.simulator.log("(Receiver) Received " +str(num_bytes) + " bytes")
                        self.seqnum = self.rcv_pkt.acknum
                        self.acknum = self.rcv_pkt.seqnum + num_bytes 
                        self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                                  self.seqnum, self.acknum)
                        bitstr = self.snd_pkt.pack()
                        self.simulator.u_send(bitstr)
                    # Accepts the data
                    rcv_seg = self.simulator.u_receive()
                    self.rcv_pkt.unpack(rcv_seg)
                   
            else:
                pass

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
