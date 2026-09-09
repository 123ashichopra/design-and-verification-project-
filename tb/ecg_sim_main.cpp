// SPDX-License-Identifier: GPL-3.0-or-later OR Commercial

#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <fstream>

#include "verilated.h"
#include "Vecg_tb.h"

static vluint64_t g_time = 0;
static int g_failures = 0;


// ---------------------------------------------------------------------
// Clock
// ---------------------------------------------------------------------

static void tick_clk(Vecg_tb* dut)
{
    dut->clk_i = 0;
    dut->eval();
    g_time++;

    dut->clk_i = 1;
    dut->eval();
    g_time++;
}


// ---------------------------------------------------------------------
// Reset
// ---------------------------------------------------------------------

static void reset(Vecg_tb* dut)
{
    dut->rst_ni = 0;

    dut->s_tvalid_i = 0;
    dut->s_tdata_i  = 0;
    dut->m_tready_i = 0;

    for (int i = 0; i < 24; i++)
        dut->coeff_i[i] = 0;

    for (int i = 0; i < 4; i++)
        tick_clk(dut);

    dut->rst_ni = 1;

    tick_clk(dut);
}


// ---------------------------------------------------------------------
// Load integer vector from text file
// ---------------------------------------------------------------------

static std::vector<int> load_vector(const char* filename)
{
    std::vector<int> v;

    std::ifstream file(filename);

    if (!file) {
        std::printf("[FAIL] Cannot open %s\n", filename);
        g_failures++;
        return v;
    }

    int x;

    while (file >> x)
        v.push_back(x);

    return v;
}


// ---------------------------------------------------------------------
// Pack 48 signed 16-bit coefficients into Verilator wide signal
// ---------------------------------------------------------------------

static void load_coeffs(Vecg_tb* dut)
{
    std::vector<int> coeff =
        load_vector("data/ecg_fir_48tap_q15.txt");

    if (coeff.size() != 48) {
        std::printf(
            "[FAIL] Expected 48 coefficients, got %zu\n",
            coeff.size()
        );

        g_failures++;
        return;
    }

    for (int i = 0; i < 24; i++)
        dut->coeff_i[i] = 0;

    for (int k = 0; k < 48; k++) {

        int word_idx = k / 2;
        int bit_pos  = (k % 2) * 16;

        uint16_t value = (uint16_t)(int16_t)coeff[k];

        dut->coeff_i[word_idx] |=
            ((uint32_t)value) << bit_pos;
    }
}


// ---------------------------------------------------------------------
// ECG regression
// ---------------------------------------------------------------------

static void test_ecg(Vecg_tb* dut)
{
    std::printf("---- ECG 48-tap fixed-point regression ----\n");

    std::vector<int> input =
        load_vector("data/ecg_input.txt");

    std::vector<int> expected =
        load_vector("data/ecg_golden_output.txt");

    std::vector<int> expected_sat =
        load_vector("data/ecg_golden_saturation.txt");

    if (input.empty() || expected.empty() || expected_sat.empty())
        return;

    if (input.size() != expected.size() ||
        input.size() != expected_sat.size()) {

        std::printf(
            "[FAIL] Vector length mismatch: "
            "input=%zu output=%zu saturation=%zu\n",
            input.size(),
            expected.size(),
            expected_sat.size()
        );

        g_failures++;
        return;
    }

    reset(dut);

    // Coefficients must be loaded AFTER reset because reset
    // clears the coefficient input path in this testbench setup.
    load_coeffs(dut);

    int cycle = 0;

    size_t input_index  = 0;
    size_t output_index = 0;

    int budget = (int)input.size() * 10 + 100;

    // -------------------------------------------------------------
    // AXI output stability tracking
    // -------------------------------------------------------------

    bool stability_pending = false;
    int16_t held_data = 0;
    bool held_user = false;

    int axi_stability_failures = 0;
    int data_failures = 0;
    int saturation_failures = 0;

    while (output_index < expected.size() &&
           budget-- > 0) {

        // ---------------------------------------------------------
        // Output backpressure
        //
        // TREADY pattern:
        //
        // cycle 0 -> 1
        // cycle 1 -> 0
        // cycle 2 -> 0
        // cycle 3 -> 1
        // ...
        // ---------------------------------------------------------

        dut->m_tready_i = ((cycle % 3) == 0);

        // ---------------------------------------------------------
        // Present current input sample
        // ---------------------------------------------------------

        if (input_index < input.size()) {

            dut->s_tdata_i =
                (uint16_t)(int16_t)input[input_index];

            dut->s_tvalid_i = 1;

        } else {

            dut->s_tvalid_i = 0;
        }

        // ---------------------------------------------------------
        // Evaluate combinational logic before clock edge
        // ---------------------------------------------------------

        dut->clk_i = 0;
        dut->eval();
        g_time++;

        bool input_handshake =
            dut->s_tvalid_i &&
            dut->s_tready_o;

        bool output_valid =
            dut->m_tvalid_o;

        bool output_ready =
            dut->m_tready_i;

        bool output_handshake =
            output_valid &&
            output_ready;

        int16_t output =
            (int16_t)dut->m_tdata_o;

        bool saturation =
            dut->m_tuser_o;

        // ---------------------------------------------------------
        // AXI stability check
        //
        // AXI-stream requirement:
        //
        // VALID = 1
        // READY = 0
        //
        // => DATA and USER must remain stable.
        // ---------------------------------------------------------

        if (output_valid && !output_ready) {

            if (!stability_pending) {

                // First cycle of backpressure.
                held_data = output;
                held_user = saturation;

                stability_pending = true;

            } else {

                if (output != held_data ||
                    saturation != held_user) {

                    if (axi_stability_failures < 10) {

                        std::printf(
                            "  [FAIL] AXI stability violation "
                            "at cycle %d: "
                            "data/user changed while stalled\n",
                            cycle
                        );
                    }

                    axi_stability_failures++;
                    g_failures++;
                }
            }

        } else {

            // Once READY is asserted or VALID goes low,
            // the previous stall condition has ended.
            stability_pending = false;
        }

        // ---------------------------------------------------------
        // Clock rising edge
        // ---------------------------------------------------------

        dut->clk_i = 1;
        dut->eval();
        g_time++;

        // ---------------------------------------------------------
        // Input handshake
        // ---------------------------------------------------------

        if (input_handshake)
            input_index++;

        // ---------------------------------------------------------
        // Output handshake
        // ---------------------------------------------------------

        if (output_handshake) {

            int expected_value =
                expected[output_index];

            bool expected_saturation =
                expected_sat[output_index] != 0;

            // -----------------------------------------------------
            // Data comparison
            // -----------------------------------------------------

            if (output != expected_value) {

                if (data_failures < 10) {

                    std::printf(
                        "  [FAIL] sample %zu: "
                        "got %d, expected %d\n",
                        output_index,
                        output,
                        expected_value
                    );
                }

                data_failures++;
                g_failures++;
            }

            // -----------------------------------------------------
            // Saturation flag comparison
            // -----------------------------------------------------

            if (saturation != expected_saturation) {

                if (saturation_failures < 10) {

                    std::printf(
                        "  [FAIL] saturation sample %zu: "
                        "got %d, expected %d\n",
                        output_index,
                        saturation,
                        expected_saturation
                    );
                }

                saturation_failures++;
                g_failures++;
            }

            output_index++;
        }

        cycle++;
    }

    // -------------------------------------------------------------
    // Timeout
    // -------------------------------------------------------------

    if (budget <= 0) {

        std::printf(
            "  [FAIL] Simulation timeout\n"
        );

        g_failures++;

        return;
    }

    // -------------------------------------------------------------
    // Final report
    // -------------------------------------------------------------

    std::printf(
        "  Samples checked       : %zu\n",
        output_index
    );

    std::printf(
        "  Data mismatches       : %d\n",
        data_failures
    );

    std::printf(
        "  Saturation mismatches : %d\n",
        saturation_failures
    );

    std::printf(
        "  AXI stability errors  : %d\n",
        axi_stability_failures
    );

    if (g_failures == 0) {

        std::printf(
            "  [PASS] ECG FIR-48 (%zu/%zu samples)\n",
            output_index,
            expected.size()
        );

    } else {

        std::printf(
            "  [FAIL] ECG FIR-48 regression failed\n"
        );
    }
}

// ---------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------

int main(int argc, char** argv)
{
    Verilated::commandArgs(argc, argv);

    setvbuf(stdout, nullptr, _IOLBF, 0);

    Vecg_tb* dut = new Vecg_tb();

    test_ecg(dut);

    if (g_failures == 0) {

        std::printf(
            "+PASS ECG regression passed\n"
        );

        delete dut;
        return 0;

    } else {

        std::printf(
            "+FAIL ECG regression: %d failures\n",
            g_failures
        );

        delete dut;
        return 1;
    }
}
