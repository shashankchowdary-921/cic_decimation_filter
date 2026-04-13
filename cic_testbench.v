// ============================================================
// TESTBENCH ? PIPELINED CIC FILTER
// Proves: fast input ? slow output ? valid_out pulses every R clocks
// ============================================================

`timescale 1ns/1ps

module tb_cic_filter;

reg        clk;
reg        rst;
reg  signed [15:0] x_in;
wire signed [31:0] y_out;
wire               valid_out;

// ---- CONNECT DUT ----
cic_filter #(.R(4), .N(2)) uut (
    .clk      (clk),
    .rst      (rst),
    .x_in     (x_in),
    .y_out    (y_out),
    .valid_out(valid_out)
);

// ---- CLOCK 100MHz ----
initial clk = 0;
always  #5 clk = ~clk;

// ---- WAVEFORM DUMP ----
initial begin
    $dumpfile("cic_sim.vcd");
    $dumpvars(0, tb_cic_filter);
end

// ---- TRACK valid_out PULSES ----
integer valid_count;
integer clk_count;
initial valid_count = 0;
initial clk_count   = 0;

always @(posedge clk) begin
    clk_count = clk_count + 1;
    if (valid_out) begin
        valid_count = valid_count + 1;
        $display("[VALID #%0d] time=%0t  y_out=%0d",
                  valid_count, $time, y_out);
    end
end

// ---- MAIN TEST ----
integer i;
initial begin
    rst  = 1;
    x_in = 0;
    $display("====================================");
    $display("   CIC PIPELINED FILTER ? START     ");
    $display("   R=4  N=2  Pipelined 6 stages     ");
    $display("====================================");

    // RESET for 4 clocks
    repeat(4) @(posedge clk);
    rst = 0;
    $display("[RST OFF] @ %0t", $time);

    // TEST 1: RAMP INPUT (0,100,200...1900 repeating)
    $display("--- TEST 1: RAMP INPUT ---");
    for (i = 0; i < 200; i = i + 1) begin
        x_in = (i % 20) * 100;
        @(posedge clk);
    end

    // TEST 2: CONSTANT INPUT
    $display("--- TEST 2: DC INPUT = 500 ---");
    for (i = 0; i < 40; i = i + 1) begin
        x_in = 500;
        @(posedge clk);
    end

    // TEST 3: ZERO INPUT
    $display("--- TEST 3: ZERO INPUT ---");
    for (i = 0; i < 40; i = i + 1) begin
        x_in = 0;
        @(posedge clk);
    end

    // TEST 4: MID-RESET
    $display("--- TEST 4: MID RESET ---");
    x_in = 1000;
    repeat(5) @(posedge clk);
    rst = 1;
    repeat(3) @(posedge clk);
    rst = 0;
    $display("[MID RST DONE] y_out rebuilding...");
    x_in = 300;
    repeat(20) @(posedge clk);

    // FINAL REPORT
    $display("====================================");
    $display("TOTAL CLK CYCLES : %0d", clk_count);
    $display("TOTAL VALID OUTS : %0d", valid_count);
    $display("CLK / VALID RATIO: %0d  (must be 4)",
              clk_count / (valid_count > 0 ? valid_count : 1));
    $display("PIPELINE LATENCY : 2 extra clocks after decimate");
    if (clk_count / (valid_count > 0 ? valid_count : 1) == 4)
        $display("RESULT: DECIMATION = WORKING ?");
    else
        $display("RESULT: CHECK WAVEFORM");
    $display("====================================");

    #50 $stop;
end

endmodule