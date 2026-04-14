`timescale 1ns / 1ps
// =============================================================================
//  cic_tb_pipelined.v  —  Testbench for cic_filter_pipelined
//  Team Mavericks | 5G/6G RF Front-End
//
//  Stimulus  : ramp  x_in = 0, 1, 2, … 255  (continuous valid_in)
//  Expected  : displays every valid output in the format:
//              VALID #N  x_in=V  y_out=W  valid_out=1
//  Python app parses: VALID #(\d+).*?y_out=(-?\d+)
// =============================================================================
module cic_tb_pipelined;

    // ── DUT parameters (edit to match sidebar selection) ──────────────────
    parameter R    = 4;
    parameter N    = 2;
    parameter M    = 1;
    parameter INW  = 16;
    parameter OUTW = 40;

    // ── Clock ──────────────────────────────────────────────────────────────
    parameter CLK_PERIOD = 10;  // 10 ns → 100 MHz

    reg clk;
    initial  clk = 0;
    always  #(CLK_PERIOD/2) clk = ~clk;

    // ── DUT ports ──────────────────────────────────────────────────────────
    reg                    rst;
    reg                    valid_in;
    reg  signed [INW-1:0]  x_in;
    wire                   valid_out;
    wire signed [OUTW-1:0] y_out;

    // ── DUT instantiation ──────────────────────────────────────────────────
    cic_filter_pipelined #(
        .R(R), .N(N), .M(M), .INW(INW), .OUTW(OUTW)
    ) dut (
        .clk(clk), .rst(rst),
        .valid_in(valid_in), .x_in(x_in),
        .valid_out(valid_out), .y_out(y_out)
    );

    // ── Counters ───────────────────────────────────────────────────────────
    integer i;
    integer valid_cnt;

    // ── Stimulus ───────────────────────────────────────────────────────────
    initial begin
        rst       = 1;
        valid_in  = 0;
        x_in      = 0;
        valid_cnt = 0;

        // Hold reset for 4 cycles
        repeat(4) @(posedge clk);
        @(negedge clk);
        rst = 0;

        // Feed 256 ramp samples back-to-back
        for (i = 0; i < 256; i = i+1) begin
            @(posedge clk);
            #1;                    // slight setup margin
            x_in     = i[INW-1:0];
            valid_in = 1;
        end

        // Deassert valid, flush pipeline
        @(posedge clk);
        #1;
        valid_in = 0;
        x_in     = 0;

        // Wait for remaining outputs to emerge from pipeline
        repeat(2*N + R + 10) @(posedge clk);

        $display("--- Simulation complete: %0d valid outputs captured ---", valid_cnt);
        $finish;
    end

    // ── Output monitor ─────────────────────────────────────────────────────
    always @(posedge clk) begin
        if (!rst && valid_out) begin
            $display("VALID #%0d  x_in=%0d  y_out=%0d  valid_out=1",
                     valid_cnt, $signed(x_in), $signed(y_out));
            valid_cnt = valid_cnt + 1;
        end
    end

    // ── Timeout ────────────────────────────────────────────────────────────
    initial begin
        #5_000_000;
        $display("TIMEOUT: simulation exceeded limit");
        $finish;
    end

endmodule
