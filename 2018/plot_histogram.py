import matplotlib.pyplot as plt

f = open("sim_data_collected.txt", "r")
arr = []
for line in f:
    arr.append(float(line))

plt.figure()
plt.title("Throughput of TCP Simulation")
plt.xlabel("Throughput (bytes/second)")
plt.ylabel("Frequency")
plt.hist(arr, 20, edgecolor='black', facecolor='green')
plt.show()
