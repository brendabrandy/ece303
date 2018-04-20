import sender
import rand
import states as TCP_STATE

class NewSender(BogoSender):

    # Constructor, currently using the default constructor
    # from sender
    def __init__(self):
        super(NewSender, self).__init__()
        self.state = TCP_STATE.IDLE
        self.snd_pkt = None
        self.rcv_pkt = None
        self.client_isn = 0
        self.server_isn = rand.randint(0,10000)

    # Should override BogoSender.send() function
    def send(self, data):
        while (True):
            if (self.state == TCP_STATE.IDLE):
                # Sender is idle, need to initiate TCP connection
                # with receiver
                # Craft SYN TCP Packet
                print ("State: TCP_STATE.IDLE")
                self.snd_pkt = packed_bits()
                self.u_send(self.snd_pkt)
                self.state = TCP_STATE.SYN_SEND
            
            elif (self.state == TCP_STATE.SYN_SEND):
                # TODO: What if SYN_SEND is corrupted?
                # SYN packet is sent, awaiting SYN-ACK from receiver
                print ("State: TCP_STATE.SYN_SEND")
                self.rcv_pkt = self.simulator.u_receive()
                # unpack the packet
                # if sequence number, SYN bit and acknowledgement
                # number is correct
                # go to ESTABLISHED state
                if (True):
                    self.state = TCP_STATE.ESTABLISHED

            elif (self.state == TCP_STATE.ESTABLISHED)
                # A connection is established between sender and receiver,
                # can start sending data now
                pass
            else:
                pass

           
if __name__ == "__main__":
    # Test NewSender
    sndr = NewSender()
    sndr.send(bin(5678))
