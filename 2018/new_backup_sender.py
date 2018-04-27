import sender
import random
import socket
import time
from segGenTest import TCPsegment
# In this setup, the sender has a buffer

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
        self.pkt_size = 1000    # maximum segment size per TCP packet
        # Variables for dupack and retransmission
        self.dupack_count = 0
        self.dupack_seqnum = self.isn
        # dictionary for all sent TCP segments
        # Can reference TCP segment with dictionary
        # something needs to be controlling the size of the window
        self.tx_window_max_size = 4
        self.tx_window_size = 0
        self.tx_window = new dict()     # list for all the sent TCP segments

    # Should override BogoSender.send() function
    def send(self, data):
        # figure out how many data packets to send
        # 8 is assuming byte alignment
        # 2 is the max segment size
        # this might become an array later because multiple data can be sent
        # through a window
        self.sendbase = 0                    # data index to check how many bytes are sent
        self.data = data
        self.seqnum = self.isn
        self.dupack_count = 0
        self.tx_window = new dict()
        self.tx_window_size = 0
        self.dupack_seqnum = self.isn
        while (True):   
            # A connection is established between sender and receiver,
            # can start sending data now
            # Send a new packet
            if (self.sendbase <= len(self.data)):
                # if there is more data to send, then send more data
                # calculate how much data I can send per burst
                burst_size = self.tx_window_max_size - self.tx_window_size
                curr_base = self.sendbase
                for i in range(burst_size):
                    curr_data, num_bytes = self.get_data()
                    curr_base += num_bytes
                    self.seqnum = self.isn + curr_base # CHANGE THIS
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
                        # if ack field of rcv_pkt is greater than sendbase
                        if (self.rcv_pkt.acknum > self.sendbase):
                            # set sendbase to acknum
                            # This indicates that all packets up to byte acknum has been
                            # received
                            self.sendbase = self.rcv_pkt.acknum
                            self.dupack_count = 0
                            self.dupack_seqnum = 0
                            # Remove all the elements before ACK that is in the dictionary
                            # i.e. remove all the elements that are smaller than acknum 
                            for key in self.tx_window:
                                if (key <= self.rcv_pkt.acknum):
                                    del(self.tx_window[key])
                                    self.tx_window_size -= 1
                        else:
                            # a duplicate ACK for already ACKed segment
                            # increase number of duplicate ACKs received for y
                            if (self.dupack_seqnum == self.rcv_pkt.acknum):
                                self.dupack_count += 1
                                # if number of duplicate ACKs received for y == 3
                                if (self.dupack_count == 3):
                                    # Retransmit segment with sequence number rcv_pkt.acknum
                                    self.snd_pkt = self.tx_window[self.rcv_pkt.acknum]
                                    self.dupack_count = 0
                                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                                    
                        break
                except socket.timeout:
                    # Condition : TIMEOUT
                    # Resend last packet
                    self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)

    def get_data(self):
        if ((self.sendbase + self.pkt_size) > len(self.data)):
            # if the last few segments do not meet pkt_size, just send
            # whatever is remaining 
            new_data = self.data[self.sendbase:]
        else:
            # else send as much as pkt_size allows
            new_data = self.data[self.sendbase: (self.sendbase+self.pkt_size)]
            # self.sendbase += self.pkt_size
        return new_data, len(new_data)


if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()
    # f = open('bigfile_2MB', 'rb')
    # contents = f.read()
    # Start sending
    # print ("Start sending")
    # start_time = time.time()
    sndr.send(bytearray([68,65,84,65]))
    # sndr.send(bytearray(contents))
    # stop_time = time.time()
    # Stop sending
    # print stop_time - start_time

