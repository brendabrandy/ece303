import receiver

class NewReceiver(BogoReceiver):

    # Constructor, currently using the default constructor
    # from receiver
    def __init__(self):
        super(NewReceiver, self).__init__()
    
    # Should override BogoReceiver.receiver() function
    def receive(self):
        pass
