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
        self.seqnum = 1000
        while (True):   
            # A connection is established between sender and receiver,
            # can start sending data now
            print ("\t Sequence Number: " + str(self.seqnum))
            print ("\t Acknowledge Num: " + str(self.acknum))

            # Send a new packet
            if (self.data_ind*8 < len(self.data)):
                # if there is more data to send, then send more data
                curr_data, num_bytes = self.get_data()
                self.seqnum = self.rcv_pkt.acknum
                self.acknum = self.rcv_pkt.seqnum + num_bytes
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,
                                          data = curr_data)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
            
            else:
                return
            while(True):
                try:
                    # Wait for an ACK packet
                    print("(Sender) Wait for ACK packet")
                    rcv_seg = self.simulator.u_receive()
                    self.rcv_pkt.unpack(rcv_seg)
                    if (not self.rcv_pkt.check_checksum()):
                        print("(Sender) Checksum incorrect! Drop packet")
                    
                    if (self.rcv_pkt.check_checksum()):
                        break
                except socket.timeout:
                    # Condition : TIMEOUT
                    # Resend last packet
                    print("(Sender) TIMEOUT! Resend data packet")
                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
            

    def get_data(self):
        if ((self.data_ind + self.mss) > len(self.data) / 8):
            # if the last few segments do not meet mss, just send
            # whatever is remaining 
            new_data = self.data[self.data_ind*8:]
        else:
            # else send as much as mss allows
            new_data = self.data[self.data_ind*8: (self.data_ind+self.mss) * 8]
            # self.data_ind += self.mss
        return new_data, len(new_data)/8


if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()

    sndr.send('{0:024b}'.format(5))
