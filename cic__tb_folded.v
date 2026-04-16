`timescale 1ns / 1ps

module cic_tb_folded;

    // ── DUT parameters ────────────────────────────────────────────────────
    parameter R    = 4;
    parameter N    = 2;
    parameter M    = 1;
    parameter INW  = 16;
    parameter OUTW = 40;

    // ── Clock ─────────────────────────────────────────────────────────────
    parameter CLK_PERIOD = 10;  // 10 ns → 100 MHz

    reg clk;
    initial  clk = 0;
    always  #(CLK_PERIOD/2) clk = ~clk;

    // ── DUT ports ─────────────────────────────────────────────────────────
    reg                    rst;
    reg                    valid_in;
    reg  signed [INW-1:0]  x_in;
    wire                   valid_out;
    wire signed [OUTW-1:0] y_out;

    // ── DUT instantiation ─────────────────────────────────────────────────
    cic_filter_folded #(
        .R(R), .N(N), .M(M), .INW(INW), .OUTW(OUTW)
    ) dut (
        .clk(clk), .rst(rst),
        .valid_in(valid_in), .x_in(x_in),
        .valid_out(valid_out), .y_out(y_out)
    );

    // ── Counters ──────────────────────────────────────────────────────────
    integer i;
    integer valid_cnt;

    // ── Cycles to wait between samples ────────────────────────────────────
    // Minimum: N cycles (INTEG) + 1 (return to IDLE)
    // On decimation tick: +N cycles (COMB)
    // Use 2*N + R + 4 to be safe for any combination
    localparam INTER_SAMPLE_WAIT = 2*N + R + 4;

    // ── Stimulus ──────────────────────────────────────────────────────────
    initial begin
        rst       = 1;
        valid_in  = 0;
        x_in      = 0;
        valid_cnt = 0;

        // Reset for 4 cycles
        repeat(4) @(posedge clk);
        @(negedge clk);
        rst = 0;
        repeat(2) @(posedge clk);

        // Feed 128 ramp samples, one per INTER_SAMPLE_WAIT clocks
        for (i = 0; i < 128; i = i+1) begin
            // Assert valid_in for exactly 1 cycle
            @(posedge clk);
            #1;
            x_in     = i[INW-1:0];
            valid_in = 1;

            @(posedge clk);
            #1;
            valid_in = 0;

            // Wait for state machine to finish and return to ST_IDLE
            repeat(INTER_SAMPLE_WAIT) @(posedge clk);
        end

        // Flush any last pending output
        repeat(2*N + 10) @(posedge clk);

        $display("--- Simulation complete: %0d valid outputs captured ---", valid_cnt);
        $finish;
    end

    // ── Output monitor ────────────────────────────────────────────────────
    always @(posedge clk) begin
        if (!rst && valid_out) begin
            $display("VALID #%0d  x_in=%0d  y_out=%0d  valid_out=1",
                     valid_cnt, $signed(x_in), $signed(y_out));
            valid_cnt = valid_cnt + 1;
        end
    end

    // ── Timeout ───────────────────────────────────────────────────────────
    initial begin
        #50_000_000;
        $display("TIMEOUT: simulation exceeded limit");
        $finish;
    end

endmodule
