import wfdb
import numpy as np

# ============================================================
# Configuration
# ============================================================

RECORD = "data/mitdb/100"

FS = 360
NUM_SAMPLES = 3600          # 10 seconds
INPUT_SCALE = 10000         # 10000 counts / mV

COEFF_FRAC = 15
Q_SCALE = 1 << COEFF_FRAC

OUTPUT_MIN = -32768
OUTPUT_MAX = 32767


# ============================================================
# Helper: signed saturation
# ============================================================

def saturate_int16(x):
    if x > OUTPUT_MAX:
        return OUTPUT_MAX
    elif x < OUTPUT_MIN:
        return OUTPUT_MIN
    else:
        return x


# ============================================================
# Load ECG
# ============================================================

record = wfdb.rdrecord(RECORD)

ecg_mv = record.p_signal[:NUM_SAMPLES, 0]

print("ECG record:", RECORD)
print("Sampling frequency:", record.fs)
print("Number of samples:", len(ecg_mv))
print("Channel:", record.sig_name[0])


# ============================================================
# Convert ECG from mV → signed 16-bit integer
# ============================================================

ecg_int = np.round(ecg_mv * INPUT_SCALE).astype(np.int64)

print()
print("Input scaling:", INPUT_SCALE, "counts/mV")
print("Integer input range:",
      np.min(ecg_int), "to", np.max(ecg_int))


# ============================================================
# Load frozen Q1.15 coefficients
# ============================================================

coeff = np.loadtxt(
    "data/ecg_fir_48tap_q15.txt",
    dtype=np.int64
)

N_TAPS = len(coeff)

print("Number of taps:", N_TAPS)
print("Coefficient sum:", np.sum(coeff))


# ============================================================
# Transposed FIR state
#
# RTL:
#
# tap_q[i] <= prod[i] + tap_q[i+1]
# tap_q[N_TAPS-1] <= prod[N_TAPS-1]
# ============================================================

tap_q = np.zeros(N_TAPS, dtype=np.int64)

outputs = []
saturation_flags = []


# ============================================================
# Process ECG samples
# ============================================================

for sample in ecg_int:

    # --------------------------------------------------------
    # Calculate products
    #
    # sample: signed 16-bit
    # coeff : signed Q1.15
    # product mathematically fits in signed 32 bits
    # --------------------------------------------------------

    prod = sample * coeff

    # --------------------------------------------------------
    # Transposed FIR state update
    # --------------------------------------------------------

    new_tap = np.zeros(N_TAPS, dtype=np.int64)

    for i in range(N_TAPS - 1):
        new_tap[i] = prod[i] + tap_q[i + 1]

    new_tap[N_TAPS - 1] = prod[N_TAPS - 1]

    tap_q = new_tap

    # --------------------------------------------------------
    # RTL output:
    #
    # acc_shifted_w = tap_q[0] >>> COEFF_FRAC;
    #
    # Python >> on positive/negative integers performs
    # arithmetic right shift.
    # --------------------------------------------------------

    shifted = tap_q[0] >> COEFF_FRAC

    # --------------------------------------------------------
    # Saturation
    # --------------------------------------------------------

    saturated = (
        shifted > OUTPUT_MAX or
        shifted < OUTPUT_MIN
    )

    output = saturate_int16(shifted)

    outputs.append(output)
    saturation_flags.append(int(saturated))


# ============================================================
# Save results
# ============================================================

outputs = np.array(outputs, dtype=np.int64)
saturation_flags = np.array(saturation_flags, dtype=np.int64)

np.savetxt(
    "data/ecg_golden_output.txt",
    outputs,
    fmt="%d"
)

np.savetxt(
    "data/ecg_golden_saturation.txt",
    saturation_flags,
    fmt="%d"
)


# ============================================================
# Report
# ============================================================

print()
print("Golden model complete.")
print("Output range:",
      np.min(outputs), "to", np.max(outputs))

print("Saturated samples:",
      np.sum(saturation_flags),
      "/",
      NUM_SAMPLES)

print()
print("First 20 input samples:")
print(ecg_int[:20])

print()
print("First 20 output samples:")
print(outputs[:20])

print()
print("Saved:")
print("  data/ecg_golden_output.txt")
print("  data/ecg_golden_saturation.txt")
