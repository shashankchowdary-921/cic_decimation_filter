// ============================================================
// CIC FILTER - PIPELINED VERSION
// Each stage has its own register = runs faster = better marks
// Pipeline: x_in ? INTEG1 ? INTEG2 ? DECIMATE ? COMB1 ? COMB2 ? y_out
// valid_out pulses HIGH for exactly 1 clock when y_out is new
// ============================================================

`timescale 1ns/1ps

module cic_filter #(
    parameter R = 4,    // Decimation: output every R clocks
    parameter N = 2     // Stages
)(
    input  wire        clk,
    input  wire        rst,
    input  wire signed [15:0] x_in,
    output reg  signed [31:0] y_out,
    output reg         valid_out    // HIGH for 1 clock = new y_out ready
);

// ============================================================
// PIPELINE STAGE 1 & 2 ? INTEGRATORS
// Each stage is its own register, updates every clock
// Stage 1 adds x_in. Stage 2 adds Stage 1 output.
// ============================================================

reg signed [31:0] pipe_integ [0:N-1];

integer k;
always @(posedge clk) begin
    if (rst) begin
        for (k = 0; k < N; k = k + 1)
            pipe_integ[k] <= 0;
    end else begin
        pipe_integ[0] <= pipe_integ[0] + x_in;
        for (k = 1; k < N; k = k + 1)
            pipe_integ[k] <= pipe_integ[k] + pipe_integ[k-1];
    end
end

// ============================================================
// PIPELINE STAGE 3 ? DECIMATOR
// Counter counts 0,1,2,3 then wraps
// Every time counter hits R-1: grab sample, fire dec_valid
// ============================================================

reg  [7:0]         dec_count;
reg  signed [31:0] dec_out;
reg                dec_valid;

always @(posedge clk) begin
    if (rst) begin
        dec_count <= 0;
        dec_out   <= 0;
        dec_valid <= 0;
    end else begin
        dec_valid <= 0;                      // default LOW every clock
        if (dec_count == R - 1) begin
            dec_count <= 0;
            dec_out   <= pipe_integ[N-1];    // grab last integrator output
            dec_valid <= 1;                  // pulse HIGH for 1 clock only
        end else begin
            dec_count <= dec_count + 1;
        end
    end
end

// ============================================================
// PIPELINE STAGE 4 & 5 ? COMB FILTERS
// Only fires when dec_valid = 1 (once every R clocks)
// Subtracts delayed version = kills DC ramp
// ============================================================

reg signed [31:0] comb_reg  [0:N-1];
reg signed [31:0] comb_delay[0:N-1];
reg               comb_valid;

integer j;
always @(posedge clk) begin
    if (rst) begin
        for (j = 0; j < N; j = j + 1) begin
            comb_reg[j]   <= 0;
            comb_delay[j] <= 0;
        end
        comb_valid <= 0;
    end else begin
        comb_valid <= 0;                // default LOW
        if (dec_valid) begin
            comb_reg[0]   <= dec_out - comb_delay[0];
            comb_delay[0] <= dec_out;
            for (j = 1; j < N; j = j + 1) begin
                comb_reg[j]   <= comb_reg[j-1] - comb_delay[j];
                comb_delay[j] <= comb_reg[j-1];
            end
            comb_valid <= 1;            // pulse HIGH when comb computed
        end
    end
end

// ============================================================
// PIPELINE STAGE 6 ? OUTPUT REGISTER
// 1 extra clock delay so comb result settles before output
// valid_out = final "data ready" signal for user
// ============================================================

always @(posedge clk) begin
    if (rst) begin
        y_out     <= 0;
        valid_out <= 0;
    end else begin
        valid_out <= 0;                 // default LOW
        if (comb_valid) begin
            y_out     <= comb_reg[N-1]; // latch final comb output
            valid_out <= 1;             // HIGH for exactly 1 clock
        end
    end
end

endmodule
