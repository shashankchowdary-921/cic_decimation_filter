`timescale 1ns / 1ps
// =============================================================================
//  cic_filter_pipelined.v  —  Pipelined CIC Decimation Filter
//  Team Mavericks | 5G/6G RF Front-End
//
//  Architecture:
//    N integrators  → each followed by a pipeline FF (D flip-flop)
//    ↓R decimator
//    N comb stages  → each followed by a pipeline FF
//
//  Properties:
//    Critical path  = 1 adder stage  (maximum Fmax)
//    Pipeline depth = 2*N FFs
//    Latency        = 2*N + 1 clock cycles
//    Throughput     = 1 valid output per R input clocks
//
//  NOTE on comb operation:
//    Each comb stage computes  y[n] = x[n] - x[n-M]
//    For M=1: y[n] = x[n] - x[n-1]   (first difference)
//    For M=2: y[n] = x[n] - x[n-2]   (delay-2 first difference, NOT 2nd order diff)
//
//  NBA (non-blocking assignment) semantics ensure all pipeline stages
//  operate on previous-cycle data → correct parallel pipeline behaviour.
//
//  Parameters:
//    R    – Decimation factor (power of 2 recommended; 2..256)
//    N    – Number of CIC stages (1..6)
//    M    – Differential delay (1 or 2)
//    INW  – Input  word width (signed two's complement)
//    OUTW – Output word width; must satisfy OUTW >= INW + N*ceil(log2(R*M))
// =============================================================================
module cic_filter_pipelined #(
    parameter R    = 4,
    parameter N    = 2,
    parameter M    = 1,
    parameter INW  = 16,
    parameter OUTW = 40
)(
    input  wire                   clk,        // system clock  (Fs_in)
    input  wire                   rst,        // synchronous active-high reset
    input  wire                   valid_in,   // input data valid
    input  wire signed [INW-1:0]  x_in,       // input sample
    output reg                    valid_out,  // output data valid  (Fs_out)
    output reg  signed [OUTW-1:0] y_out       // output sample
);

    // -----------------------------------------------------------------------
    // Sign-extend input to full datapath width
    // -----------------------------------------------------------------------
    wire signed [OUTW-1:0] x_ext = {{(OUTW-INW){x_in[INW-1]}}, x_in};

    // -----------------------------------------------------------------------
    // INTEGRATOR SECTION  (runs at Fs_in)
    //
    //   int_acc[i] : accumulator for integrator stage i
    //   int_ff[i]  : pipeline register – captures int_acc[i], feeds stage i+1
    //   int_vld[i] : valid flag, pipelined one cycle through each FF
    //
    //   Stage 0 : accumulates sign-extended x_in
    //   Stage i : accumulates int_ff[i-1]  (previous stage's pipelined output)
    //
    //   Due to non-blocking assignments, ALL stages update IN PARALLEL each clock
    //   using values from the PREVIOUS cycle → correct N-stage pipeline.
    // -----------------------------------------------------------------------
    reg signed [OUTW-1:0] int_acc [0:N-1];
    reg signed [OUTW-1:0] int_ff  [0:N-1];
    reg                   int_vld [0:N-1];

    always @(posedge clk) begin : INTEG_BLOCK
        integer ii;
        if (rst) begin
            for (ii = 0; ii < N; ii = ii+1) begin
                int_acc[ii] <= {OUTW{1'b0}};
                int_ff[ii]  <= {OUTW{1'b0}};
                int_vld[ii] <= 1'b0;
            end
        end else begin
            // ── Stage 0 ──────────────────────────────────────────────────
            if (valid_in)
                int_acc[0] <= int_acc[0] + x_ext;
            int_ff[0]  <= int_acc[0];   // pipeline FF
            int_vld[0] <= valid_in;     // valid pipeline

            // ── Stages 1..N-1 (NBA → all use previous-cycle values) ─────
            for (ii = 1; ii < N; ii = ii+1) begin
                if (int_vld[ii-1])
                    int_acc[ii] <= int_acc[ii] + int_ff[ii-1];
                int_ff[ii]  <= int_acc[ii];
                int_vld[ii] <= int_vld[ii-1];
            end
        end
    end

    // -----------------------------------------------------------------------
    // DECIMATION  (↓R)
    //   Count R valid samples of int_ff[N-1], then latch and assert dec_valid.
    // -----------------------------------------------------------------------
    reg [7:0]              dec_cnt;   // 8-bit → supports R up to 256
    reg signed [OUTW-1:0]  dec_data;
    reg                    dec_valid;

    always @(posedge clk) begin
        if (rst) begin
            dec_cnt   <= 8'd0;
            dec_data  <= {OUTW{1'b0}};
            dec_valid <= 1'b0;
        end else begin
            dec_valid <= 1'b0;                  // default deassert
            if (int_vld[N-1]) begin
                if (dec_cnt == R-1) begin
                    dec_cnt   <= 8'd0;
                    dec_data  <= int_ff[N-1];
                    dec_valid <= 1'b1;
                end else begin
                    dec_cnt <= dec_cnt + 8'd1;
                end
            end
        end
    end

    // -----------------------------------------------------------------------
    // COMB SECTION  (runs at Fs_out = Fs_in / R)
    //
    //   Each comb stage computes:  y[n] = x[n] - x[n-M]
    //     M=1 → subtract x[n-1]   (stored in comb_dly_a)
    //     M=2 → subtract x[n-2]   (stored in comb_dly_b, shifted from comb_dly_a)
    //
    //   comb_ff[i]    : pipeline register – captures comb output, feeds stage i+1
    //   comb_dly_a[i] : delay-1 register  (x[n-1] for stage i)
    //   comb_dly_b[i] : delay-2 register  (x[n-2] for stage i, used when M=2)
    //   comb_vld[i]   : valid flag, pipelined through FFs
    //
    //   NBA semantics: comb_dly_a/b on RHS = OLD values → correct y[n]-y[n-M].
    //   Synthesis tool optimises away comb_dly_b when M=1 (dead logic removal).
    // -----------------------------------------------------------------------
    reg signed [OUTW-1:0] comb_ff    [0:N-1];
    reg signed [OUTW-1:0] comb_dly_a [0:N-1];
    reg signed [OUTW-1:0] comb_dly_b [0:N-1];
    reg                   comb_vld   [0:N-1];

    always @(posedge clk) begin : COMB_BLOCK
        integer ii;
        if (rst) begin
            for (ii = 0; ii < N; ii = ii+1) begin
                comb_ff[ii]    <= {OUTW{1'b0}};
                comb_dly_a[ii] <= {OUTW{1'b0}};
                comb_dly_b[ii] <= {OUTW{1'b0}};
                comb_vld[ii]   <= 1'b0;
            end
        end else begin
            // ── Stage 0 : input from decimator ───────────────────────────
            if (dec_valid) begin
                comb_dly_b[0] <= comb_dly_a[0];          // shift delay chain
                comb_dly_a[0] <= dec_data;                // store x[n]
                comb_ff[0]    <= dec_data                 // y[n] = x[n] - x[n-M]
                               - ((M == 1) ? comb_dly_a[0] : comb_dly_b[0]);
            end
            comb_vld[0] <= dec_valid;

            // ── Stages 1..N-1 (NBA → all use previous-cycle values) ─────
            for (ii = 1; ii < N; ii = ii+1) begin
                if (comb_vld[ii-1]) begin
                    comb_dly_b[ii] <= comb_dly_a[ii];
                    comb_dly_a[ii] <= comb_ff[ii-1];
                    comb_ff[ii]    <= comb_ff[ii-1]
                                   - ((M == 1) ? comb_dly_a[ii] : comb_dly_b[ii]);
                end
                comb_vld[ii] <= comb_vld[ii-1];
            end
        end
    end

    // -----------------------------------------------------------------------
    // OUTPUT REGISTER
    // -----------------------------------------------------------------------
    always @(posedge clk) begin
        if (rst) begin
            y_out     <= {OUTW{1'b0}};
            valid_out <= 1'b0;
        end else begin
            y_out     <= comb_ff[N-1];
            valid_out <= comb_vld[N-1];
        end
    end

endmodule
