import sender
import random
import states as TCP_STATE
from segGenTest import TCPsegment, TCPsegmentDecode

# assume sender is server
class NewSender(sender.BogoSender):

    # Constructor, currently using the default constructor
    # from sender
    def __init__(self):
        super(NewSender, self).__init__()
        self.state = TCP_STATE.IDLE
        self.snd_pkt = TCPsegment()
        self.rcv_pkt = None
        self.rcv_seqnum = 0
        # See new_receiver.py for setting isn
        self.snd_seqnum = 0

    # Should override BogoSender.send() function
    def send(self, data):
        while (True):
            if (self.state == TCP_STATE.IDLE):
                # Sender is idle, need to initiate TCP connection
                # with receiver
                self.simulator.log("(Sender) Sending SYN to Receiver")
                self.snd_seqnum = random.randint(0, 5000)
                self.simulator.log("\tSender Sequence Number: " + str(self.snd_seqnum))
                # Craft SYN TCP Packet
                self.snd_pkt.SYN(1)                         
                self.snd_pkt.SrcPort(self.inbound_port)
                self.snd_pkt.DestPort(self.outbound_port)
                self.snd_pkt.SeqNum(self.snd_seqnum)     # Set ISN
                self.snd_pkt.AckNum(0)
                # Send the TCP Packet
                self.snd_pkt.Pack()
                self.simulator.u_send(self.snd_pkt.TCPsegBitStr)
                self.state = TCP_STATE.SYN_SEND
            
            elif (self.state == TCP_STATE.SYN_SEND):
                # SYN packet is sent, awaiting SYN-ACK from receiver
                self.simulator.log("(Sender) Waiting for SYN-ACK")
                rcv_seg = self.simulator.u_receive()
                self.rcv_pkt = TCPsegmentDecode(rcv_seg)
                # if sequence number, SYN bit and acknowledgement
                # number is correct, return an ACK packet
                # go to ESTABLISHED state
                if (self.rcv_pkt.SYN == 1 and
                       self.rcv_pkt.AckNum == self.seqnum+1):
                    self.seqnum = self.rcv_pkt.AckNum
                    self.acknum = self.rcv_pkt.SeqNum + 1
                    self.snd_pkt = TCPSegment()
                    self.snd_pkt.SrcPort(self.inbound_port)
                    self.snd_pkt.DestPort(self.outbound_port)
                    self.snd_pkt.SeqNum(self.seqnum)
                    self.snd_pkt.AckNum(self.acknum)
                    self.simulator.u_send(self.snd_pkt.Data(None))
                    self.state = TCP_STATE.ESTABLISHED
            
            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between sender and receiver,
                # can start sending data now
                self.simulator.log("(Sender) Connection Established")
                self.simulator.log("\t Sequence Number: " + str(self.seqnum))
                self.simulator.log("\t Acknowledge Num: " + str(self.acknum))
                while(True):
                    pass
            else:
                pass

           
if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()
    sndr.send(bin(5678))
