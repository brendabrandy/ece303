import sender

class NewSender(BogoSender):

    # Constructor, currently using the default constructor
    # from sender
    def __init__(self):
        super(NewSender, self).__init__()
    
    # Should override BogoSender.send() function
    def send(self, data):
        pass

