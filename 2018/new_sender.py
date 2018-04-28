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
        self.pkt_size = 1000   # maximum segment size per TCP packet
        # Variables for dupack and retransmission
        self.dupack_count = 0
        self.tx_window_size = 4
        self.sendend = 0
    # Should override BogoSender.send() function
    def send(self, data):
        # figure out how many data packets to send
        # 8 is assuming byte alignment
        # 2 is the max segment size
        # this might become an array later because multiple data can be sent
        # through a window
        self.sendbase = 0     # data index to check how many bytes are sent
        self.data = data
        self.sendend = self.sendbase + self.tx_window_size
        self.seqnum = self.isn
        self.dupack_count = 0
        while (True):   
            # initialize curr_base to be send base
            curr_base = self.sendbase * self.pkt_size
            self.sendend = self.sendbase + self.tx_window_size
            self.tx = []
            for i in range(self.tx_window_size):
                # calculate the position of the first byte of the data
                # segment, which is the current base + number of bytes
                curr_data, num_bytes = self.get_data(curr_base)
                # if there is no data to send, break out of the loop
                if (num_bytes == 0):
                    break
                # The new sequence number is the isn + current base
                self.seqnum = self.isn + curr_base 
                self.acknum = self.rcv_pkt.seqnum 
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,
                                          data = curr_data)
                if (curr_base == 0):
                    # add a syn bit to the packet if it is not sent
                    self.snd_pkt.syn = 1
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                self.tx.append((self.isn+curr_base, num_bytes))
                curr_base += num_bytes
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
                            self.sendbase = (self.rcv_pkt.acknum - self.isn)/self.pkt_size
                            self.dupack_count = 0
                            if (self.sendbase >= len(self.data)/self.pkt_size):
                                # last ack is received, return
                                return
                            if (self.sendbase == self.sendend):
                                break
                        else:
                            # a duplicate ACK for already ACKed segment
                            self.dupack_count += 1
                            # if 3 dupacks are received
                            if (self.dupack_count == 3):
                                # Retransmit from where the segment is lost
                                break
                except socket.timeout:
                    # Condition : TIMEOUT
                    # resend packets again
                    break

    def get_data(self, base):
        if (base >= len(self.data)):
            return bytearray(), 0
        elif ((base + self.pkt_size) > len(self.data)):
            # if the last few segments do not meet pkt_size, just send
            # whatever is remaining 
            new_data = self.data[base:]
        else:
            # else send as much as pkt_size allows
            new_data = self.data[base: (base+self.pkt_size)]
            # self.sendbase += self.pkt_size
        return new_data, len(new_data)


if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()
    f = open('bigfile_2MB', 'rb')
    contents = f.read()
    # Start sending
    print ("Start sending")
    start_time = time.time()
    # sndr.send(bytearray([72,101,108,108,111,32,87,111,114,108,100]))
    sndr.send(bytearray(contents))
    stop_time = time.time()
    # Stop sending
    print stop_time - start_time

