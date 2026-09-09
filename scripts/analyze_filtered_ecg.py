import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Configuration
# ============================================================

FS = 360
NUM_SAMPLES = 3600

INPUT_SCALE = 10000.0

INPUT_FILE = "data/ecg_input.txt"
OUTPUT_FILE = "data/ecg_golden_output.txt"

# ============================================================
# Load input and filtered output
# ============================================================

x_int = np.loadtxt(INPUT_FILE, dtype=np.int64)
y_int = np.loadtxt(OUTPUT_FILE, dtype=np.int64)

x = x_int / INPUT_SCALE
y = y_int / INPUT_SCALE

if len(x) != NUM_SAMPLES:
    raise ValueError(
        f"Expected {NUM_SAMPLES} input samples, got {len(x)}"
    )

if len(y) != NUM_SAMPLES:
    raise ValueError(
        f"Expected {NUM_SAMPLES} output samples, got {len(y)}"
    )

# ============================================================
# Time axis
# ============================================================

t = np.arange(NUM_SAMPLES) / FS

# ============================================================
# Remove startup transient for spectral analysis
#
# The FIR starts with zero state, so the first ~48 samples
# contain startup transient behavior.
# ============================================================

START = 100

x_fft = x[START:]
y_fft = y[START:]

N = len(x_fft)

# ============================================================
# FFT
# ============================================================

X = np.fft.rfft(x_fft)
Y = np.fft.rfft(y_fft)

freq = np.fft.rfftfreq(N, d=1 / FS)

# Magnitude
X_mag = np.abs(X) / N
Y_mag = np.abs(Y) / N

# ============================================================
# 60 Hz measurement
# ============================================================

idx_60 = np.argmin(np.abs(freq - 60))

raw_60 = X_mag[idx_60]
filtered_60 = Y_mag[idx_60]

if raw_60 > 0:
    attenuation_60 = 20 * np.log10(
        filtered_60 / raw_60
    )
else:
    attenuation_60 = float("-inf")

# ============================================================
# RMS
# ============================================================

raw_rms = np.sqrt(np.mean(x_fft ** 2))
filtered_rms = np.sqrt(np.mean(y_fft ** 2))

# ============================================================
# Print results
# ============================================================

print("============================================")
print("ECG FILTER SIGNAL-LEVEL ANALYSIS")
print("============================================")

print(f"Sampling frequency : {FS} Hz")
print(f"Samples analyzed   : {N}")
print(f"Analysis duration  : {N / FS:.3f} s")

print()
print("Amplitude:")
print(f"  Raw RMS           : {raw_rms:.6f} mV")
print(f"  Filtered RMS      : {filtered_rms:.6f} mV")

print()
print("60 Hz component:")
print(f"  Raw magnitude     : {raw_60:.6e} mV")
print(f"  Filtered magnitude: {filtered_60:.6e} mV")
print(f"  Change            : {attenuation_60:.2f} dB")

# ============================================================
# Plot 1: waveform
# ============================================================

plt.figure(figsize=(12, 5))

plt.plot(t, x, label="Raw ECG")
plt.plot(t, y, label="Filtered ECG")

plt.xlabel("Time (s)")
plt.ylabel("Amplitude (mV)")
plt.title("MIT-BIH Record 100 — Raw vs 48-Tap FIR")
plt.grid()
plt.legend()

plt.tight_layout()

plt.savefig(
    "data/ecg_raw_vs_filtered.png",
    dpi=150
)

plt.close()

# ============================================================
# Plot 2: frequency spectrum
# ============================================================

plt.figure(figsize=(12, 5))

plt.plot(freq, X_mag, label="Raw ECG")
plt.plot(freq, Y_mag, label="Filtered ECG")

plt.xlim(0, 120)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("MIT-BIH Record 100 — Frequency Spectrum")
plt.grid()
plt.legend()

plt.tight_layout()

plt.savefig(
    "data/ecg_raw_vs_filtered_fft.png",
    dpi=150
)

plt.close()

print()
print("Saved:")
print("  data/ecg_raw_vs_filtered.png")
print("  data/ecg_raw_vs_filtered_fft.png")
