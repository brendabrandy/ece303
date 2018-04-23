from segGenTest import TCPsegment, TCPsegmentDecode


# make a TCP checksum for the checksum field
# due to the nature of TCPsegment class, this function should be called
# after segment.Pack() is called
# during checksum calculation, the checksum field itself is filled with zeros
# @param tcp_seg: A TCPsegment class
# returns a 16bit checksum string
def make_checksum(tcp_seg):
    checksum_string = "0000000000000000"    
    tcp_bitstring = tcp_seg.tcp_seg_bitstr
    return checksum_string

# Check TCP checksum to make sure the checksum field is correct
def check_checksum(tcp_seg):

