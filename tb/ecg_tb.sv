// SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
//
// ECG-specific testbench for the 48-tap FIR configuration.

module ecg_tb #(
  parameter int DATA_WIDTH  = 16,
  parameter int COEFF_WIDTH = 16
) (
  input  logic                              clk_i,
  input  logic                              rst_ni,

  input  logic [48*COEFF_WIDTH-1:0]         coeff_i,

  input  logic signed [DATA_WIDTH-1:0]      s_tdata_i,
  input  logic                              s_tvalid_i,
  output logic                              s_tready_o,

  output logic signed [DATA_WIDTH-1:0]      m_tdata_o,
  output logic                              m_tvalid_o,
  input  logic                              m_tready_i,

  output logic                              m_tuser_o
);

  fir_core #(
    .N_TAPS      (48),
    .DATA_WIDTH  (DATA_WIDTH),
    .COEFF_WIDTH (COEFF_WIDTH)
  ) u_dut (
    .clk_i           (clk_i),
    .rst_ni          (rst_ni),

    .coeff_i         (coeff_i),

    .s_axis_tdata_i  (s_tdata_i),
    .s_axis_tvalid_i (s_tvalid_i),
    .s_axis_tready_o (s_tready_o),

    .m_axis_tdata_o  (m_tdata_o),
    .m_axis_tvalid_o (m_tvalid_o),
    .m_axis_tready_i (m_tready_i),

    .m_axis_tuser_o  (m_tuser_o)
  );

endmodule
