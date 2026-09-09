// SPDX-License-Identifier: GPL-3.0-or-later OR Commercial

module fir16_top (
  input  logic              clk_i,
  input  logic              rst_ni,

  input  logic [16*16-1:0]  coeff_i,

  input  logic signed [15:0] s_axis_tdata_i,
  input  logic               s_axis_tvalid_i,
  output logic               s_axis_tready_o,

  output logic signed [15:0] m_axis_tdata_o,
  output logic               m_axis_tvalid_o,
  input  logic                m_axis_tready_i,
  output logic                m_axis_tuser_o
);

  fir_core #(
    .N_TAPS      (16),
    .DATA_WIDTH  (16),
    .COEFF_WIDTH (16)
  ) u_fir (
    .clk_i           (clk_i),
    .rst_ni          (rst_ni),
    .coeff_i         (coeff_i),

    .s_axis_tdata_i  (s_axis_tdata_i),
    .s_axis_tvalid_i (s_axis_tvalid_i),
    .s_axis_tready_o (s_axis_tready_o),

    .m_axis_tdata_o  (m_axis_tdata_o),
    .m_axis_tvalid_o (m_axis_tvalid_o),
    .m_axis_tready_i (m_axis_tready_i),
    .m_axis_tuser_o  (m_axis_tuser_o)
  );

endmodule
