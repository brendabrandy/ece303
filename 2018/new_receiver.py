import receiver
import states as TCP_STATE

# assumes NewReceiver to be server
class NewReceiver(receiver.BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
        self.state = TCP_STATE.LISTEN

    # Should override BogoReceiver.receiver() function
    def receive(self):
        while(True):
            if (self.state == TCP_STATE.LISTEN):
                print ("State: TCP_STATE.LISTEN")
                rcv_pkt = self.simulator.u_receive()
                print rcv_pkt
            else:
                pass

if __name__ == "__main__":
    # Test NewReceiver
    rcvr = NewReceiver()
    rcvr.receive()
