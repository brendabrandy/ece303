import sender
import random
import socket
import time
from segGenTest import TCPsegment

# assume sender is server
class NewSender(sender.BogoSender):

    # Constructor, currently using the default constructor
    # from sender
    def __init__(self):
        super(NewSender, self).__init__()
        self.snd_pkt = TCPsegment(0,0,0,0)
        self.rcv_pkt = TCPsegment(0,0,0,0)
        self.seqnum = 0
        self.isn = 1000
        # See new_receiver.py for setting isn
        self.acknum = 0
        # Timeout for retransmission. Set arbitrarily to 10
        self.pkt_size = 1000    # maximum segment size per TCP packet
        
    # Should override BogoSender.send() function
    def send(self, data):
        # figure out how many data packets to send
        # 8 is assuming byte alignment
        # 2 is the max segment size
        # this might become an array later because multiple data can be sent
        # through a window
        self.data_ind = 0                    # data index to check how many bytes are sent
        self.data = data
        self.seqnum = self.isn
        while (True):   
            # A connection is established between sender and receiver,
            # can start sending data now
            # Send a new packet
            if (self.data_ind <= len(self.data)):
                # if there is more data to send, then send more data
                curr_data, num_bytes = self.get_data()
                self.seqnum = self.isn + self.data_ind*8
                self.acknum = self.rcv_pkt.seqnum 
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,
                                          data = curr_data)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
            else:
                # Finished sending all data, return the function
                return
            while(True):
                try:
                    # Wait for an ACK packet
                    rcv_seg = self.simulator.u_receive()
                    if (self.rcv_pkt.check_checksum(rcv_seg)):
                        self.rcv_pkt.unpack(rcv_seg)
                        self.seqnum += self.data_ind
                        self.acknum = self.rcv_pkt.seqnum
                        self.data_ind += self.pkt_size
                        break
                except socket.timeout:
                    # Condition : TIMEOUT
                    # Resend last packet
                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)

    def get_data(self):
        if ((self.data_ind + self.pkt_size) > len(self.data)):
            # if the last few segments do not meet pkt_size, just send
            # whatever is remaining 
            new_data = self.data[self.data_ind:]
        else:
            # else send as much as pkt_size allows
            new_data = self.data[self.data_ind: (self.data_ind+self.pkt_size)]
            # self.data_ind += self.pkt_size
        return new_data, len(new_data)


if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()
    f = open('bigfile_2MB', 'rb')
    contents = f.read()
    # Start sending
    print ("Start sending")
    start_time = time.time()
    sndr.send(bytearray(contents))
    stop_time = time.time()
    # Stop sending
    print stop_time - start_time

