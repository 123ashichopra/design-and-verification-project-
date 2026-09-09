import wfdb
import numpy as np

RECORD = "data/mitdb/100"
NUM_SAMPLES = 3600
INPUT_SCALE = 10000

record = wfdb.rdrecord(RECORD)

ecg_mv = record.p_signal[:NUM_SAMPLES, 0]

ecg_int = np.round(ecg_mv * INPUT_SCALE).astype(np.int64)

np.savetxt(
    "data/ecg_input.txt",
    ecg_int,
    fmt="%d"
)

print("Exported", len(ecg_int), "ECG samples")
print("Range:", np.min(ecg_int), "to", np.max(ecg_int))
print("File: data/ecg_input.txt")
