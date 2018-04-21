import receiver
import rand
import states as TCP_STATE
from segGenTest import TCPsegment, TCPsegmentDecode

# QUESTION: DO WE NEED TO DEAL WITH MULTIPLE SENDERS AND RECEIVERS OVER THE SAME CHANNEL

# assumes receiver is client
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__(debug=True)
        self.state = TCP_STATE.LISTEN
        self.rcv_pkt = None
        self.snd_pkt = TCPsegment() # make the segment in initializer
        # choose receiver isn. 5000 is an arbitrary number, can be subjected to 
        # change. NOTE: need to deal with this overflowing
        self.rcv_seqnum = 0 
        self.snd_seqnum = 0

    # Should override BogoReceiver.receiver() function
    def receive(self):
        while(True):
            if (self.state == TCP_STATE.LISTEN):
                # Receiver listening the channel for new packets
                self.simulator.log("(Receiver) Listening for data")
                rcv_seg = self.simulator.u_receive()
                self.rcv_pkt = TCPSegmentDecode(rcv_seg)
                # disassemble the packet 
                # if syn bit is set, go to SYN_RECEIVED state
                if (self.rcv_pkt.SYN == 1):
                    self.snd_seqnum = self.rcv_pkt.SeqNum
                    self.simulator.log("\t Sender Sequence Number: %d\n")
                    self.state = TCP_STATE.SYN_RECEIVED

            elif (self.state == TCP_STATE.SYN_RECEIVED):
                self.simulator.log("(Receiver) Receive SYN")
                # A SYN packet is received from the receiver
                # packs a SYNACK packet to the receiver
                self.rcv_seqnum = rand.randint(0, 5000)
                # make necessary changes
                # listens for a confirmation from the receiver
                self.rcv_pkt = self.simulator.u_receive()
                # unpack the bits
                # if sequence number and acknowledge number is correct
                # go to ESTABLISHED state
                if (True):
                    self.state = TCP_STATE.ESTABLISHED

            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between the sender and receiver
                # can staart sending data now
                self.simulator.log("(Receiver) Connection Established")
                pass

            else:
                pass

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
