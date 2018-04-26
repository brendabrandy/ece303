import sender
import random
import socket
import states as TCP_STATE
from segGenTest import TCPsegment

# assume sender is server
class NewSender(sender.BogoSender):

    # Constructor, currently using the default constructor
    # from sender
    def __init__(self):
        super(NewSender, self).__init__()
        self.state = TCP_STATE.IDLE
        self.snd_pkt = TCPsegment(0,0,0,0)
        self.rcv_pkt = TCPsegment(0,0,0,0)
        self.seqnum = 0
        # See new_receiver.py for setting isn
        self.acknum = 0
        # Timeout for retransmission. Set arbitrarily to 10
        self.timeout = 10
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
                self.acknum = 0
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum, syn=1)                  
                # Send the TCP Packet
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                self.state = TCP_STATE.SYN_SEND
            
            elif (self.state == TCP_STATE.SYN_SEND):
                # SYN packet is sent, awaiting SYN-ACK from receiver
                while(True):
                    try:
                        self.simulator.log("(Sender) Waiting for SYN-ACK")
                        rcv_seg = self.simulator.u_receive()
                        self.rcv_pkt.unpack(rcv_seg)
                        # if the checksum is correct and the syn bit
                        # and ACK bytes are correct go to the next step
                        if (self.rcv_pkt.check_checksum() and
                            self.rcv_pkt.syn == 1 and
                            self.rcv_pkt.acknum == self.seqnum + 1):
                            break
                        else:
                            self.simulator.log("(Sender) Erroneous packet!")
                    except socket.timeout:
                        self.simulator.log("(Sender) Resend SYN-ACK")
                        self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                # The correct packet is received, go to ESTABLISHED state
                self.seqnum = self.rcv_pkt.acknum
                self.acknum = self.rcv_pkt.seqnum + 1
                curr_data,_ = self.get_data()
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,
                                          data=curr_data)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                self.state = TCP_STATE.ESTABLISHED
            
            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between sender and receiver,
                # can start sending data now
                self.simulator.log("(Sender) Connection Established")
                self.simulator.log("\t Sequence Number: " + str(self.seqnum))
                self.simulator.log("\t Acknowledge Num: " + str(self.acknum))
                while (True):
                    # Waiting for an ACK packet reception
                    try:
                        self.simulator.log("(Sender) Sent ACK waiting for next ACK")
                        rcv_seg = self.simulator.u_receive()
                        self.rcv_pkt.unpack(rcv_seg)
                        if (self.rcv_pkt.check_checksum()): 
                            self.simulator.log("(Sender) Seq Num: " +str(self.seqnum))
                            self.simulator.log("(Sender) Ack Num received: "+str(self.snd_pkt.acknum)) 
                        else:
                            self.simulator.log("(Sender) Checksum Wrong!")
                        if (self.rcv_pkt.check_checksum() and
                            self.rcv_pkt.acknum == self.seqnum):
                                break
                        # checksum is not the same -- treat as a lost packet
                        # just ignore it, same with wrong sequence number
                    
                    except socket.timeout:
                        # Retransmit the packet
                        self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                # all the checks passed, send the next packet
                self.simulator.log("(Sender) ACK successful")
                if (self.data_ind*8 >= len(self.data)):
                    # if all the data is transmitted, go to the final state
                    # note when implementing SR/GBN, make sure that
                    # the previous packets are all transmitted!
                    self.state = TCP_STATE.FIN_WAIT_1
                    break
                else:
                    curr_data, num_bytes = self.get_data()
                    self.seqnum = self.rcv_pkt.acknum
                    self.acknum = self.rcv_pkt.seqnum + num_bytes
                    self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                              self.seqnum, self.acknum,
                                              data = curr_data)
                    bitstr = self.snd_pkt.pack()
                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)

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
        return new_data, len(new_data)/8


if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()

    sndr.send('{0:024b}'.format(5))
