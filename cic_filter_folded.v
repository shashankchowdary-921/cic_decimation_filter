`timescale 1ns / 1ps
// =============================================================================
//  cic_filter_folded.v  —  Folded CIC Decimation Filter
//  Team Mavericks | 5G/6G RF Front-End
//
//  Architecture  (area-optimised):
//    ONE shared adder/subtractor time-multiplexed across all N stages.
//    Internally sequential state machine; functionally identical to Basic CIC.
//
//  State machine:
//    ST_IDLE  → wait for valid_in, capture x_in
//    ST_INTEG → N clock cycles: integrate stage 0, 1, … N-1 sequentially
//               A CARRY register forwards each stage's new value to the next
//    ST_COMB  → (only on decimation tick) N clock cycles: comb stage 0…N-1
//               carry also forwards comb output through the chain
//    → back to ST_IDLE
//
//  Carry register:
//    Holds adder output at end of each phase cycle.
//    Allows stage[i]'s result (registered after one clock) to feed stage[i+1]
//    in the NEXT clock — so only ONE adder is ever active at a time. ✓
//
//  Comb operation:  y[n] = x[n] - x[n-M]   (same as pipelined / basic)
//    M=1 → subtract delay-1 register
//    M=2 → subtract delay-2 register
//
//  Trade-offs vs Basic/Pipelined:
//    Adder count     : 1  (vs 2*N)
//    Register count  : N integrators + N comb delays (+N for M=2) + 1 carry
//    Throughput      : 1 output per R+N*(N-1) clocks (slower than pipelined)
//    Latency         : N clocks (INTEG) + N clocks (COMB) per decimated sample
//
//  Parameters:
//    R    – Decimation factor (2..256)
//    N    – Number of CIC stages (1..6)
//    M    – Differential delay (1 or 2)
//    INW  – Input  word width (signed)
//    OUTW – Output word width  ≥  INW + N*ceil(log2(R*M))
// =============================================================================
module cic_filter_folded #(
    parameter R    = 4,
    parameter N    = 2,
    parameter M    = 1,
    parameter INW  = 16,
    parameter OUTW = 40
)(
    input  wire                   clk,
    input  wire                   rst,        // synchronous active-high reset
    input  wire                   valid_in,   // one pulse per input sample
    input  wire signed [INW-1:0]  x_in,
    output reg                    valid_out,  // one pulse per decimated output
    output reg  signed [OUTW-1:0] y_out
);

    // -----------------------------------------------------------------------
    // State encoding
    // -----------------------------------------------------------------------
    localparam [1:0]
        ST_IDLE  = 2'd0,
        ST_INTEG = 2'd1,
        ST_COMB  = 2'd2;

    reg [1:0] state;

    // -----------------------------------------------------------------------
    // Control registers
    // -----------------------------------------------------------------------
    reg [2:0] phase;    // 0..N-1  (3 bits → N up to 8)
    reg [7:0] dec_cnt;  // 0..R-1  (8 bits → R up to 256)

    // -----------------------------------------------------------------------
    // Datapath registers
    // -----------------------------------------------------------------------
    // N integrator accumulators (one per stage)
    reg signed [OUTW-1:0] integ_reg [0:N-1];

    // Carry register: holds result of shared adder from previous cycle.
    //   In ST_INTEG: carry = new value of integ_reg[phase] (propagates forward)
    //   In ST_COMB : carry = new comb output (propagates through comb chain)
    reg signed [OUTW-1:0] carry;

    // Captured input (sign-extended)
    reg signed [OUTW-1:0] x_cap;

    // Comb delay registers — one per stage
    //   comb_dly[i]  = x[n-1] for stage i   (always updated)
    //   comb_dly2[i] = x[n-2] for stage i   (only relevant when M=2)
    reg signed [OUTW-1:0] comb_dly  [0:N-1];
    reg signed [OUTW-1:0] comb_dly2 [0:N-1];

    // -----------------------------------------------------------------------
    // Main FSM + shared adder
    // -----------------------------------------------------------------------
    always @(posedge clk) begin : MAIN_FSM
        integer ii;

        if (rst) begin
            state     <= ST_IDLE;
            phase     <= 3'd0;
            dec_cnt   <= 8'd0;
            carry     <= {OUTW{1'b0}};
            x_cap     <= {OUTW{1'b0}};
            valid_out <= 1'b0;
            y_out     <= {OUTW{1'b0}};
            for (ii = 0; ii < N; ii = ii+1) begin
                integ_reg[ii] <= {OUTW{1'b0}};
                comb_dly[ii]  <= {OUTW{1'b0}};
                comb_dly2[ii] <= {OUTW{1'b0}};
            end

        end else begin
            valid_out <= 1'b0;   // default deassert

            case (state)

                // ─────────────────────────────────────────────────────────
                // IDLE: wait for valid_in, capture and sign-extend x_in
                // ─────────────────────────────────────────────────────────
                ST_IDLE: begin
                    if (valid_in) begin
                        x_cap <= {{(OUTW-INW){x_in[INW-1]}}, x_in};
                        phase <= 3'd0;
                        state <= ST_INTEG;
                    end
                end

                // ─────────────────────────────────────────────────────────
                // INTEG: sequentially integrate N stages using shared adder
                //
                //   Phase 0: shared adder = integ_reg[0] + x_cap
                //            → carry carries the NEW integ_reg[0] to phase 1
                //   Phase i: shared adder = integ_reg[i] + carry
                //            → carry carries NEW integ_reg[i] forward
                //
                //   NBA: integ_reg[phase] and carry on the RHS are OLD values.
                //        Both LHS assignments see the same old carry.
                // ─────────────────────────────────────────────────────────
                ST_INTEG: begin
                    if (phase == 3'd0) begin
                        integ_reg[0] <= integ_reg[0] + x_cap;
                        carry        <= integ_reg[0] + x_cap;   // new integ_reg[0]
                    end else begin
                        integ_reg[phase] <= integ_reg[phase] + carry;
                        carry            <= integ_reg[phase] + carry;
                    end

                    if (phase == N-1) begin
                        // All N integrations done
                        // carry (after this clock) = new integ_reg[N-1]
                        if (dec_cnt == R-1) begin
                            dec_cnt <= 8'd0;
                            phase   <= 3'd0;
                            state   <= ST_COMB;   // carry feeds comb chain
                        end else begin
                            dec_cnt <= dec_cnt + 8'd1;
                            state   <= ST_IDLE;
                        end
                    end else begin
                        phase <= phase + 3'd1;
                    end
                end

                // ─────────────────────────────────────────────────────────
                // COMB: sequentially comb N stages using shared subtractor
                //
                //   carry enters as the decimated integrator output.
                //
                //   Each phase i:
                //     new_carry = carry - comb_dly[i]          (M=1)
                //               = carry - comb_dly2[i]         (M=2)
                //     comb_dly[i]  ← carry   (store current input as delay)
                //     comb_dly2[i] ← old comb_dly[i]  (second delay for M=2)
                //
                //   NBA: comb_dly/comb_dly2 on RHS = OLD values ✓
                //     So subtraction uses x[n-1] or x[n-2] correctly.
                //
                //   On last phase (N-1): write output registers directly
                //   from the combinatorial result (same expression, old values).
                // ─────────────────────────────────────────────────────────
                ST_COMB: begin
                    // Update delay line (NBA — old values used in subtraction above)
                    comb_dly2[phase] <= comb_dly[phase];
                    comb_dly[phase]  <= carry;

                    // Shared subtractor: new_carry = carry - delay
                    carry <= carry - ((M == 1) ? comb_dly[phase] : comb_dly2[phase]);

                    if (phase == N-1) begin
                        // Final stage: output the result
                        // (same expression, uses OLD carry and OLD comb_dly due to NBA)
                        y_out     <= carry - ((M == 1) ? comb_dly[phase] : comb_dly2[phase]);
                        valid_out <= 1'b1;
                        state     <= ST_IDLE;
                        phase     <= 3'd0;
                    end else begin
                        phase <= phase + 3'd1;
                    end
                end

                default: state <= ST_IDLE;

            endcase
        end
    end

endmodule
