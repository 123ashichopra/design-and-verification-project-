import wfdb
import matplotlib.pyplot as plt

record_path = "data/mitdb/100"

record = wfdb.rdrecord(record_path)

print("Sampling frequency:", record.fs)
print("Number of samples:", record.sig_len)
print("Number of channels:", record.n_sig)
print("Channel names:", record.sig_name)

ecg = record.p_signal[:, 0]

print("First 10 samples:")
print(ecg[:10])

plt.figure(figsize=(12, 4))
plt.plot(ecg[:3600])

plt.xlabel("Sample")
plt.ylabel("Amplitude (mV)")
plt.title("MIT-BIH Record 100 - Channel 1")
plt.grid()
plt.show()
