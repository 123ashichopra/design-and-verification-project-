import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import remez, freqz

# ============================================================
# ECG FIR FILTER
# ============================================================

FS = 360.0

NUM_TAPS = 48

PASSBAND_END = 40.0
STOPBAND_START = 60.0

# ============================================================
# Design
# ============================================================

coefficients = remez(
    NUM_TAPS,
    [0, PASSBAND_END, STOPBAND_START, FS / 2],
    [1, 0],
    fs=FS
)

# ============================================================
# Print design information
# ============================================================

print("\n========================================")
print("48-TAP ECG FIR FILTER")
print("========================================")

print(f"Sampling frequency : {FS} Hz")
print(f"Number of taps     : {NUM_TAPS}")
print(f"Passband           : 0 - {PASSBAND_END} Hz")
print(f"Stopband           : {STOPBAND_START} - {FS/2} Hz")

# ============================================================
# Floating-point coefficients
# ============================================================

print("\nFloating-point coefficients:")

for i, coeff in enumerate(coefficients):
    print(f"h[{i:2d}] = {coeff:+.10f}")

# ============================================================
# Frequency response
# ============================================================

frequencies, response = freqz(
    coefficients,
    worN=8192,
    fs=FS
)

magnitude_db = 20 * np.log10(
    np.maximum(np.abs(response), 1e-12)
)

# ============================================================
# Measure performance
# ============================================================

passband_mask = frequencies <= PASSBAND_END
stopband_mask = frequencies >= STOPBAND_START

passband_db = magnitude_db[passband_mask]
stopband_db = magnitude_db[stopband_mask]

passband_ripple = (
    np.max(passband_db) -
    np.min(passband_db)
)

stopband_max = np.max(stopband_db)
stopband_attenuation = -stopband_max

print("\n========================================")
print("FILTER PERFORMANCE")
print("========================================")

print(f"Passband ripple      : {passband_ripple:.3f} dB")
print(f"Worst stopband level : {stopband_max:.3f} dB")
print(f"Stopband attenuation : {stopband_attenuation:.3f} dB")

# ============================================================
# Check symmetry
# ============================================================

symmetry_error = np.max(
    np.abs(coefficients - coefficients[::-1])
)

print(f"Symmetry error       : {symmetry_error:.3e}")

# ============================================================
# Save floating-point coefficients
# ============================================================

coeff_file = "data/ecg_fir_48tap_float.txt"

with open(coeff_file, "w") as f:

    for coeff in coefficients:
        f.write(f"{coeff:.12f}\n")

print(f"\nSaved coefficients to:")
print(coeff_file)

# ============================================================
# Plot
# ============================================================

plt.figure(figsize=(12, 5))

plt.plot(
    frequencies,
    magnitude_db,
    label="48-tap ECG FIR"
)

plt.axvline(
    PASSBAND_END,
    linestyle="--",
    label="40 Hz passband edge"
)

plt.axvline(
    STOPBAND_START,
    linestyle="--",
    label="60 Hz stopband edge"
)

plt.xlim(0, 180)
plt.ylim(-100, 5)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.title("48-Tap ECG FIR Filter Frequency Response")

plt.grid()
plt.legend()

plt.tight_layout()

plot_file = "data/ecg_fir_48tap_response.png"

plt.savefig(
    plot_file,
    dpi=150
)

print(f"Saved frequency response to:")
print(plot_file)
