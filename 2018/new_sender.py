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
        self.seqnum = 0
        # See new_receiver.py for setting isn
        self.acknum = 0
        self.mss = 2    # maximum segment size per TCP packet
       
    # Should override BogoSender.send() function
    def send(self, data):
        # figure out how many data packets to send
        # 8 is assuming byte alignment
        # 2 is the max segment size
        # this might become an array later because multiple data can be sent
        # through a window
        self.data_ind = 0                    # data index to check how many bytes are sent
        self.data = data
        while (True):
            if (self.state == TCP_STATE.IDLE):
                # Sender is idle, need to initiate TCP connection
                # with receiver
                self.simulator.log("(Sender) Sending SYN to Receiver")
                self.seqnum = random.randint(0, 5000)
                self.simulator.log("\tSender Sequence Number: " + str(self.seqnum))
                # Craft SYN TCP Packet
                self.snd_pkt.SYN(1)                         
                self.snd_pkt.SrcPort(self.inbound_port)
                self.snd_pkt.DestPort(self.outbound_port)
                self.snd_pkt.SeqNum(self.seqnum)     # Set ISN
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
                if (self.rcv_pkt.SYN == '1' and
                       self.rcv_pkt.AckNum == self.seqnum+1):
                    self.seqnum = self.rcv_pkt.AckNum
                    self.acknum = self.rcv_pkt.SeqNum + 1
                    self.snd_pkt = TCPsegment()
                    self.snd_pkt.SrcPort(self.inbound_port)
                    self.snd_pkt.DestPort(self.outbound_port)
                    self.snd_pkt.SeqNum(self.seqnum)
                    self.snd_pkt.AckNum(self.acknum)
                    curr_data_packet = self.get_data()
                    self.snd_pkt.SetData(curr_data_packet)
                    self.snd_pkt.Pack()
                    self.simulator.u_send(self.snd_pkt.TCPsegBitStr)
                    self.state = TCP_STATE.ESTABLISHED
            
            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between sender and receiver,
                # can start sending data now
                self.simulator.log("(Sender) Connection Established")
                self.simulator.log("\t Sequence Number: " + str(self.seqnum))
                self.simulator.log("\t Acknowledge Num: " + str(self.acknum))
                while (True):
                    # Waiting for an ACK packet reception
                    rcv_seg = self.simulator.u_receive()
                    self.rcv_pkt = TCPsegmentDecode(rcv_seg)
                    if (self.rcv_pkt.SeqNum == self.acknum):
                        # if ACK is successful
                        self.simulator.log("(Sender) ACK Successful!")
                        if (self.data_ind*8 >= len(self.data)):
                           # if all data is transmitted, go to final state
                           # note, when implementing SR/GBN, make sure that
                           # the previous packets are all transmitted!
                           self.state = TCP_STATE.FIN_WAIT_1
                           break
                        else: 
                            curr_data_packet = self.get_data()
                            num_bytes = len(curr_data_packet)/8
                            self.seqnum = self.rcv_pkt.AckNum
                            self.acknum = self.rcv_pkt.SeqNum + num_bytes
                            self.snd_pkt = TCPsegment()
                            self.snd_pkt.SrcPort(self.inbound_port)
                            self.snd_pkt.DestPort(self.outbound_port)
                            self.snd_pkt.SeqNum(self.seqnum)
                            self.snd_pkt.AckNum(self.acknum)
                            self.snd_pkt.SetData(curr_data_packet)
                            self.snd_pkt.Pack()
                            self.simulator.u_send(self.snd_pkt.TCPsegBitStr)
            
                    # Need to do something if they are not the same
            elif (self.state == TCP_STATE.FIN_WAIT_1):
                self.simulator.log("(Sender) In final waiting state")
                while(True):
                    pass

            else:
                pass

    def get_data(self):
        if ((self.data_ind + self.mss) > len(self.data) / 8):
            # if the last few segments do not meet mss, just send
            # whatever is remaining 
            new_data = self.data[self.data_ind*8:]
            self.data_ind = len(self.data)/8
        else:
            # else send as much as mss allows
            new_data = self.data[self.data_ind*8: (self.data_ind+self.mss) * 8]
            self.data_ind += self.mss
        return new_data

if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()

    sndr.send('{0:024b}'.format(5))
