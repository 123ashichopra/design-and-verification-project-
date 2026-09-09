import wfdb
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Load MIT-BIH record 100
# ---------------------------------------------------------
record = wfdb.rdrecord("data/mitdb/100")

fs = record.fs
ecg = record.p_signal[:, 0]       # MLII channel

print("Sampling frequency:", fs)
print("Total samples:", len(ecg))
print("Duration:", len(ecg) / fs, "seconds")

# ---------------------------------------------------------
# Take first 10 seconds
# ---------------------------------------------------------
N = int(10 * fs)
segment = ecg[:N]

# Remove DC component before FFT
segment_ac = segment - np.mean(segment)

# ---------------------------------------------------------
# FFT
# ---------------------------------------------------------
fft_values = np.fft.rfft(segment_ac)
frequencies = np.fft.rfftfreq(N, d=1/fs)

magnitude = np.abs(fft_values) / N

# ---------------------------------------------------------
# Plot ECG waveform
# ---------------------------------------------------------
plt.figure(figsize=(12, 4))

time = np.arange(N) / fs

plt.plot(time, segment)

plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude (mV)")
plt.title("MIT-BIH Record 100 - MLII")
plt.grid()

# ---------------------------------------------------------
# Plot frequency spectrum
# ---------------------------------------------------------
plt.figure(figsize=(12, 4))

plt.plot(frequencies, magnitude)

plt.xlim(0, 100)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("ECG Frequency Spectrum")
plt.grid()

plt.savefig("data/ecg_analysis.png", dpi=150, bbox_inches="tight")
print("Saved plot to data/ecg_analysis.png")
