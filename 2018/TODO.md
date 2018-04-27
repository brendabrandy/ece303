## Test

1. Open two terminals
2. In first terminal, run `python new_receiver.py`
3. In second terminal, run `python new_sender.py`
4. Receiver should go on forever, while sender will end


## Todo list
* Flow Control
* Go-Back-N in case of packet swap
* Multiple sender multiple receiver
* Congestion Control 

## Notable Stuff
* No initial handshake because the API already handles it
* Timeouts: Both sender and receiver has a timeout of 5 seconds (might be subjected to change)
* Extra timeout for receiver: The receiver also has an extra long timeout which lets it detect when the transmission end 
* Error detection with checksums
* Timeouts for packet drops 
