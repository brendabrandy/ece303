import receiver
import random
import states as TCP_STATE
from segGenTest import TCPsegment, TCPsegmentDecode

# QUESTION: DO WE NEED TO DEAL WITH MULTIPLE SENDERS AND RECEIVERS OVER THE SAME CHANNEL

# assumes receiver is client
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
        self.state = TCP_STATE.LISTEN
        self.rcv_pkt = None         # received packet
        self.snd_pkt = TCPsegment() # make the segment in initializer
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
                self.rcv_pkt = TCPsegmentDecode(rcv_seg)
                # if syn bit is set, go to SYN_RECEIVED state
                if (self.rcv_pkt.SYN == '1'):
                    print("\t Sender Sequence Number: " +  str(self.rcv_pkt.SeqNum))
                    self.state = TCP_STATE.SYN_RECEIVED
                    self.acknum = self.rcv_pkt.SeqNum + 1

            elif (self.state == TCP_STATE.SYN_RECEIVED):
                self.simulator.log("(Receiver) Receive SYN")
                # A SYN packet is received from the receiver
                # packs a SYNACK packet to the receiver
                self.seqnum = random.randint(0, 5000)
                self.simulator.log("\t Receiver Sequence Number: " + str(self.seqnum))
                # Crafts SYNACK packet
                self.snd_pkt = TCPsegment()
                self.snd_pkt.SYN(1)
                self.snd_pkt.SrcPort(self.inbound_port)
                self.snd_pkt.DestPort(self.outbound_port)
                self.snd_pkt.SeqNum(self.seqnum)
                self.snd_pkt.AckNum(self.acknum)
                self.snd_pkt.Pack()
                # Send SYNACK packet over simulator channel
                self.simulator.u_send(self.snd_pkt.TCPsegBitStr)
                # listens for a confirmation from the receiver
                rcv_seg = self.simulator.u_receive()
                self.rcv_pkt = TCPsegmentDecode(rcv_seg)
                # if sequence number and acknowledge number is correct
                # go to ESTABLISHED state
                if (self.rcv_pkt.SYN == '0' and 
                        self.rcv_pkt.SeqNum == self.acknum
                        and self.rcv_pkt.AckNum == self.seqnum+1):
                    self.seqnum = self.seqnum + 1
                    self.state = TCP_STATE.ESTABLISHED

            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between the sender and receiver
                # can staart sending data now
                self.simulator.log("(Receiver) Connection Established")
                self.simulator.log("\t Sequence Number: " + str(self.seqnum))
                self.simulator.log("\t Acknowledge Num: " + str(self.acknum))
                while (True):
                    # Accepts the data
                    data = self.simulator.u_receive()
                    self.rcv_pkt = TCPsegmentDecode(rcv_seg)
                    # if the sequence number and ack number is corrrect
                    if (self.rcv_pkt.SeqNum == self.ack_num):
                        # send an ACK back
                        self.seq_num = self.rcv_pkt.AckNum
                        self.ack_num = self.rcv_pkt.SeqNum 
                        # Send an ACK back
                        self.snd_pkt = TCPSegment()
                        self.snd_pkt.SrcPort(self.inbound_port)
                        self.snd_pkt.DestPort(self.outbound_port)
                        self.snd_pkt.SeqNum(self.seq_num)
                        self.snd_pkt.AckNum(self.ack_num)

            else:
                pass

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
