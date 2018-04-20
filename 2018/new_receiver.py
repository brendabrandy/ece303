import receiver
import states as TCP_STATE

# assumes NewReceiver to be server
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
        self.state = TCP_STATE.LISTEN
        self.rcv_pkt = None
        self.snd_pkt = None

    # Should override BogoReceiver.receiver() function
    def receive(self):
        while(True):
            if (self.state == TCP_STATE.LISTEN):
                # Receiver listening the channel for new packets
                print ("State: TCP_STATE.LISTEN")
                self.rcv_pkt = self.simulator.u_receive()
                print self.rcv_pkt
                # disassemble the packet 
                # if syn bit is set, go to SYN_RECEIVED state
                if (True):
                    self.state = TCP_STATE.SYN_RECEIVED

            elif (self.state == TCP_STATE.SYN_RECEIVED):
                print ("State: TCP_STATE.SYN_RECEIVED")
                # A SYN packet is received from the receiver
                # packs a SYNACK packet to the receiver
                
                # make necessary changes
                # listens for a confirmation from the receiver
                self.rcv_pkt = self.simulator.u_receive()
                # unpack the bits
                # if sequence number and acknowledge number is correct
                # go to ESTABLISHED state
                if (True):
                    self.state = TCP_STATE.ESTABLISHED

            elif (self.state == TCP_STATE.ESTABLISHED):
                # A connection is established between the sender and receiver
                # can staart sending data now
                pass

            else:
                pass

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
