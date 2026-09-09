# FPGA-Based ECG FIR Filter

A SystemVerilog-based digital FIR filter for real-time ECG signal processing, developed using the MIT-BIH Arrhythmia Database as a representative biomedical signal source.

The project combines digital signal processing, fixed-point arithmetic, parameterized RTL design, and simulation-based verification to implement and evaluate an ECG preprocessing filter.

## Project Overview

The project uses a parameterized transposed-form FIR architecture and configures it as a 48-tap low-pass filter for ECG preprocessing.

### Key specifications

| Parameter | Value |
|---|---|
| Input signal | ECG |
| Dataset | MIT-BIH Arrhythmia Database |
| Sampling frequency | 360 Hz |
| Filter | 48-tap low-pass FIR |
| Passband | 0–40 Hz |
| Stopband begins | 60 Hz |
| Coefficient format | Signed Q1.15 |
| Input/output width | 16-bit |
| Architecture | Transposed direct form |
| Interface | Streaming valid/ready |
| Latency | 2 cycles |

## Architecture

The FIR core uses a transposed direct-form architecture in which the input is broadcast to the parallel tap multipliers and the partial sums are stored in a register chain.

```text
                    ECG Input
                       |
                       v
              +------------------+
              | 48 Parallel      |
              | Multipliers      |
              +------------------+
                 |  |  |  |
                 v  v  v  v
              +------------------+
              | Transposed       |
              | Accumulator Chain|
              +------------------+
                       |
                       v
                 Fixed-Point
                   Scaling
                       |
                       v
                  Saturation
                       |
                       v
                  ECG Output
# FPGA-Based ECG FIR Filter

A SystemVerilog-based digital FIR filter for real-time ECG signal processing, developed using the MIT-BIH Arrhythmia Database as a representative biomedical signal source.

The project combines digital signal processing, fixed-point arithmetic, parameterized RTL design, and simulation-based verification to implement and evaluate an ECG preprocessing filter.

## Project Overview

The project uses a parameterized transposed-form FIR architecture and configures it as a 48-tap low-pass filter for ECG preprocessing.

### Key specifications

| Parameter | Value |
|---|---|
| Input signal | ECG |
| Dataset | MIT-BIH Arrhythmia Database |
| Sampling frequency | 360 Hz |
| Filter | 48-tap low-pass FIR |
| Passband | 0–40 Hz |
| Stopband begins | 60 Hz |
| Coefficient format | Signed Q1.15 |
| Input/output width | 16-bit |
| Architecture | Transposed direct form |
| Interface | Streaming valid/ready |
| Latency | 2 cycles |

## Architecture

The FIR core uses a transposed direct-form architecture in which the input is broadcast to the parallel tap multipliers and the partial sums are stored in a register chain.

```text
                    ECG Input
                       |
                       v
              +------------------+
              | 48 Parallel      |
              | Multipliers      |
              +------------------+
                 |  |  |  |
                 v  v  v  v
              +------------------+
              | Transposed       |
              | Accumulator Chain|
              +------------------+
                       |
                       v
                 Fixed-Point
                   Scaling
                       |
                       v
                  Saturation
                       |
                       v
                  ECG Output
##Filter Design


