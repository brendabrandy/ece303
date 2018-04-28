import sender
import random
import socket
import time
import matplotlib.pyplot as plt
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
        self.isn = 0
        # See new_receiver.py for setting isn
        self.acknum = 0
        self.pkt_size = 1000   # maximum segment size per TCP packet
        # Variables for dupack and retransmission
        self.dupack_count = 0
        self.tx_window_size = 4
        self.sendend = 0
        # Variables for estimating timeouts
        self.estimated_rtt = 0.002             # estimated RTT
        self.dev_rtt = 0.0005                  # deviant RTT, used to calculate timeout
        self.sample_rtt = 0.002                # sample RTT, used to calculate RTTs
        self.is_measuring_rtt = False   # check whether I am currently measuring RTT
        self.sample_acknum = 0      # track which acknum TCP is measuring
        self.sample_rtt_start = 0   # Sample RTT measurement start time
        self.alpha = 0.1  # decay factor of EVMA of estimated_rtt
        self.beta = 0.25    # decay factor of EWMA of dev_rtt
        self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt
        self.sendbase = 0 
        
        # Variables for Congestion control
        self.is_congested = False
        
        # for data collection and data viz
        self.transmission_rounds = 0
        self.sample_rtt_collected = [self.sample_rtt]
        self.sample_pt = [self.sendbase]
        self.estimated_rtt_collected = [self.estimated_rtt]
        self.tx_size_collected = [self.tx_window_size]
        self.sample_tx_pt = [self.transmission_rounds]

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
        self.seqnum = 0
        self.dupack_count = 0
        self.simulator.sndr_socket.settimeout(self.timeout_interval)
        self.is_measuring_rtt = False
        self.is_congested = False
        self.transmission_rounds = 0

        while (True):   
            
            # initialize curr_base to be send base
            curr_base = self.sendbase * self.pkt_size
            self.sendend = self.sendbase + self.tx_window_size
            self.tx = []
            # print "(Sender) curr_base: " + str(curr_base)
            if (self.is_congested):
                # Multiplicative decrease
                if (self.tx_window_size > 1):
                    self.tx_window_size /= 2
            else:
                # Additive increase
                self.tx_window_size += 1
            self.tx_size_collected.append(self.tx_window_size)
            self.sample_tx_pt.append(self.transmission_rounds)
            self.dupack_count = 0
            self.transmission_rounds += 1
            self.is_measuring_rtt = False 
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
                # print "(Sender) Sent seqnum " + str(self.seqnum)
                self.snd_pkt = TCPsegment(self.inbound_port, self.outbound_port,
                                          self.seqnum, self.acknum,
                                          data = curr_data)
                bitstr = self.snd_pkt.pack()
                self.simulator.u_send(self.snd_pkt.tcp_seg_bitstr)
                
                self.tx.append((self.isn+curr_base, num_bytes))
                curr_base += num_bytes
            if not self.is_measuring_rtt:
                self.is_measuring_rtt = True
                self.sample_rtt_start = time.time()
                self.sample_acknum = curr_base
            # self.sendbase = self.sendbase + 1
            while(True):
                try:
                    # Wait for an ACK packet
                    # print "(Sender) Trying to receive packets"
                    rcv_seg = self.simulator.u_receive()
                    if (self.rcv_pkt.check_checksum(rcv_seg)):
                        # print "(Sender) Checksum correct"
                        self.rcv_pkt.unpack(rcv_seg)
                        # print "(Sender) Expect Greater than" + str(self.sendbase) + "\t Got ACK" + str(self.rcv_pkt.acknum)
                        # print "(Sender) Ending at " + str(self.sendend)
                        # if ack field of rcv_pkt is greater than sendbase
                        if (self.rcv_pkt.acknum/1000 > self.sendbase):
                            self.sendbase = self.rcv_pkt.acknum /self.pkt_size
                            if (self.rcv_pkt.acknum == self.sample_acknum and 
                                self.is_measuring_rtt):
                                # if I am measuring the RTT
                                # Update corresponding RTT values and timeout intervals
                                self.sample_rtt = time.time() - self.sample_rtt_start
                                self.estimated_rtt = (1 - self.alpha) * self.estimated_rtt \
                                                     + self.alpha * self.sample_rtt
                                self.dev_rtt = (1 - self.beta) *self.dev_rtt + \
                                               self.beta * abs(self.sample_rtt - self.estimated_rtt)
                                self.is_measuring_rtt = False
                                self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt
                                self.simulator.rcvr_socket.settimeout(self.timeout_interval)
                                # print "New timeout : " + str(self.timeout_interval)
                                # for data collection and data viz
                                self.is_measuring_rtt = False
                                self.sample_rtt_collected.append(self.sample_rtt)
                                self.sample_pt.append(self.sample_acknum)
                                self.estimated_rtt_collected.append(self.estimated_rtt)
                            # set sendbase to acknum
                            # This indicates that all packets up to byte acknum has been
                            # received
                            self.dupack_count = 0
                            if (self.sendbase >= len(self.data)/self.pkt_size):
                                # last ack is received, return
                                self.is_measuring_rtt = False
                                return
                            if (self.sendbase == self.sendend):
                                self.is_congested = False
                                self.is_measuring_rtt = False
                                break
                        else:
                            # a duplicate ACK for already ACKed segment
                            self.dupack_count += 1
                            # print "(Sender) Got Dupack" + str(self.dupack_count) 
                            # if 3 dupacks are received
                            if (self.dupack_count >= 3):
                                self.is_congested = True
                                # Retransmit from where the segment is lost
                                self.is_measuring_rtt = False
                                break
                    else:
                        self.is_measuring_rtt = False
                        self.is_congested = True
                except socket.timeout:
                    # Condition : TIMEOUT
                    # resend packets again
                    self.is_congested = True
                    # recalculate estimated and dev_rtt
                    self.is_measuring_rtt = False
                    """
                    self.sample_rtt = time.time() - self.sample_rtt_start
                    self.estimated_rtt  = (1 - self.alpha) * self.estimated_rtt \
                                            + self.alpha * self.sample_rtt
                    self.dev_rtt = (1 - self.beta) * self.dev_rtt + \
                                    self.beta * abs(self.sample_rtt - self.estimated_rtt)
                    self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt
                    
                    print "(Sender) New timeout after timeout: " + str(self.timeout_interval)
                    self.simulator.rcvr_socket.settimeout(self.timeout_interval)
                    self.sample_rtt_collected.append(self.timeout_interval)
                    self.sample_pt.append(self.sample_acknum)
                    self.estimated_rtt_collected.append(self.estimated_rtt)
                    """
                    break

    def plot_stats(self):
        plt.figure()
        plt.title("RTT Estimations")
        plt.xlabel("Byte location")
        plt.ylabel("RTT (s)")
        plt.plot(self.sample_pt, self.sample_rtt_collected,'o-',label="Sample RTT")
        plt.plot(self.sample_pt, self.estimated_rtt_collected, 'o-', label="Estimated RTT")
        plt.legend()
         
        plt.figure()
        plt.title("Congestion Window size")
        plt.xlabel("Transmission Round")
        plt.ylabel("Number of Segments")
        plt.plot(self.sample_tx_pt, self.tx_size_collected, 'o-')
        plt.show()

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
    f = open('mediumFile.txt', 'rb')
    contents = f.read()
    # print "Sending " + str(len(contents)) + " bytes of data"
    # Start sending
    # print ("Start sending")
    start_time = time.time()
    # sndr.send(bytearray([72,101,108,108,111,32,87,111,114,108,100]))
    sndr.send(bytearray(contents))
    stop_time = time.time()
    # Stop sending
    # sndr.plot_stats()
    mytime = stop_time - start_time
    # print mytime
    f.close()
    print str(len(contents)/mytime)
