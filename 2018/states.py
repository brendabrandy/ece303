# Represent States as integers, add more states if necessary

IDLE = 0            # Sender is waiting for info from application layer
LISTEN = 1          # Receiver listening for new data in the channel
SYN_SEND = 2        # Sender sent SYN packet to receiver, waiting for response
SYN_RECEIVED = 3    # Receiver received the SYN packet, sends SYNACK packet back
ESTABLISHED = 4     # Sender and Receiver establishes the connection

