import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz

# ============================================================
# ECG FIR - Q1.15 Quantization
# ============================================================

FS = 360.0
NUM_TAPS = 48
Q_FRAC = 15

FLOAT_FILE = "data/ecg_fir_48tap_float.txt"

# ============================================================
# Load floating-point coefficients
# ============================================================

coefficients = np.loadtxt(FLOAT_FILE)

print("\n========================================")
print("Q1.15 COEFFICIENT QUANTIZATION")
print("========================================")

print(f"Number of coefficients : {len(coefficients)}")
print(f"Fractional bits        : {Q_FRAC}")

# ============================================================
# Quantize
# ============================================================

scale = 2 ** Q_FRAC

quantized = np.round(
    coefficients * scale
).astype(np.int16)

# ============================================================
# Dequantize
# ============================================================

quantized_float = quantized.astype(np.float64) / scale

# ============================================================
# Print coefficients
# ============================================================

print("\nCoefficient comparison:")
print("Index       Float          Q1.15       Dequantized")

for i in range(NUM_TAPS):

    print(
        f"{i:2d}     "
        f"{coefficients[i]:+.10f}    "
        f"{quantized[i]:6d}       "
        f"{quantized_float[i]:+.10f}"
    )

# ============================================================
# Quantization error
# ============================================================

error = quantized_float - coefficients

print("\n========================================")
print("QUANTIZATION ERROR")
print("========================================")

print(f"Maximum error : {np.max(np.abs(error)):.10e}")
print(f"RMS error     : {np.sqrt(np.mean(error**2)):.10e}")

# ============================================================
# Frequency response of quantized filter
# ============================================================

frequencies, response = freqz(
    quantized_float,
    worN=8192,
    fs=FS
)

magnitude_db = 20 * np.log10(
    np.maximum(np.abs(response), 1e-12)
)

# ============================================================
# Measure performance
# ============================================================

passband_mask = frequencies <= 40
stopband_mask = frequencies >= 60

passband_db = magnitude_db[passband_mask]
stopband_db = magnitude_db[stopband_mask]

passband_ripple = (
    np.max(passband_db) -
    np.min(passband_db)
)

stopband_max = np.max(stopband_db)

stopband_attenuation = -stopband_max

print("\n========================================")
print("QUANTIZED FILTER PERFORMANCE")
print("========================================")

print(f"Passband ripple      : {passband_ripple:.3f} dB")
print(f"Worst stopband level : {stopband_max:.3f} dB")
print(f"Stopband attenuation : {stopband_attenuation:.3f} dB")

# ============================================================
# Save integer coefficients
# ============================================================

INTEGER_FILE = "data/ecg_fir_48tap_q15.txt"

with open(INTEGER_FILE, "w") as f:

    for coeff in quantized:
        f.write(f"{coeff}\n")

print("\nSaved Q1.15 coefficients to:")
print(INTEGER_FILE)

# ============================================================
# Plot
# ============================================================

plt.figure(figsize=(12, 5))

plt.plot(
    frequencies,
    magnitude_db
)

plt.axvline(
    40,
    linestyle="--",
    label="40 Hz passband edge"
)

plt.axvline(
    60,
    linestyle="--",
    label="60 Hz stopband edge"
)

plt.xlim(0, 180)
plt.ylim(-100, 5)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.title("48-Tap ECG FIR — Q1.15 Frequency Response")

plt.grid()
plt.legend()

plt.tight_layout()

PLOT_FILE = "data/ecg_fir_48tap_q15_response.png"

plt.savefig(
    PLOT_FILE,
    dpi=150
)

print("\nSaved response plot to:")
print(PLOT_FILE)
