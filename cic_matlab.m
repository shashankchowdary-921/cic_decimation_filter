clc; clear; close all;

%% ================================================
%  USER INPUT
%% ================================================
R = input('Enter Decimation Factor R (default 8): ');
if isempty(R), R = 8; end
N = input('Enter Number of CIC Stages N (default 3): ');
if isempty(N), N = 3; end
fprintf('\n>>> R = %d, N = %d\n\n', R, N);

%% ================================================
%  SIGNAL GENERATION
%% ================================================
fs      = 200e6;          % Input sampling rate  200 MHz
T       = 1e-4;           % 0.1 ms observation window
t       = 0:1/fs:T;
f1      = 5e6;            % Desired signal  5 MHz

signal  = sin(2*pi*f1*t);
interf1 = 0.6 * sin(2*pi*40e6*t);
interf2 = 0.3 * sin(2*pi*70e6*t);
noise   = 0.2 * randn(size(t));
x       = signal + interf1 + interf2 + noise;
x       = x / max(abs(x));

fs_out  = fs / R;         % Output rate after decimation

%% ================================================
%  PIPELINED CIC FILTER  (sample-by-sample, hardware model)
%% ================================================
L              = length(x);
int_reg        = zeros(1, N);        % Integrator accumulators
comb_prev      = zeros(N, 1);        % Comb delay registers
dec_count      = 0;
out_idx        = 0;
max_out        = ceil(L/R) + 10;

int_stage_out  = zeros(N, L);        % Integrator outputs (high rate)
comb_stage_out = zeros(N, max_out);  % Comb outputs (low rate)
y_pipe         = zeros(1, max_out);  % Final CIC output

fprintf('Running pipelined CIC...\n');

for k = 1:L
    % --- N cascaded integrators (run at full input rate) ---
    int_reg(1) = int_reg(1) + x(k);
    int_stage_out(1, k) = int_reg(1);
    for s = 2:N
        int_reg(s) = int_reg(s) + int_reg(s-1);
        int_stage_out(s, k) = int_reg(s);
    end

    % --- Decimator: pass one sample every R clocks ---
    dec_count = dec_count + 1;
    if dec_count == R
        dec_count = 0;
        out_idx   = out_idx + 1;

        % --- N cascaded comb sections (run at decimated rate) ---
        comb_in = int_reg(N);
        for s = 1:N
            comb_out           = comb_in - comb_prev(s);
            comb_prev(s)       = comb_in;
            comb_in            = comb_out;
            comb_stage_out(s, out_idx) = comb_in;
        end
        y_pipe(out_idx) = comb_in;
    end
end

% Trim to valid output length
y_pipe         = y_pipe(1:out_idx);
comb_stage_out = comb_stage_out(:, 1:out_idx);

% Normalise each stage for display
int_disp  = int_stage_out;
comb_disp = comb_stage_out;
for s = 1:N
    mx = max(abs(int_disp(s,:)));  if mx>0, int_disp(s,:)  = int_disp(s,:)  / mx; end
    mx = max(abs(comb_disp(s,:))); if mx>0, comb_disp(s,:) = comb_disp(s,:) / mx; end
end

% Normalise CIC output
y_cic = y_pipe / (R^N);
if max(abs(y_cic)) > 0, y_cic = y_cic / max(abs(y_cic)); end

fprintf('CIC output samples = %d\n', out_idx);

%% ================================================
%  PIPELINED FIR COMPENSATION FILTER  (no toolbox)
%% ================================================
order = 120;
fc    = 6e6;
Wn    = fc / (fs_out/2);
n_vec = (0:order) - order/2;

h_sinc = sin(pi * Wn * n_vec) ./ (pi * n_vec + eps);
h_sinc(order/2 + 1) = Wn;
win  = 0.54 - 0.46 * cos(2*pi*(0:order)/order);   % Hamming window
b    = h_sinc .* win;
b    = b / sum(b);

fir_reg   = zeros(1, order+1);
y_fir_raw = zeros(1, out_idx);

for k = 1:out_idx
    fir_reg      = [y_cic(k), fir_reg(1:end-1)];
    y_fir_raw(k) = sum(b .* fir_reg);
end

delay = order / 2;
y_fir = [y_fir_raw(delay+1:end), zeros(1, delay)];
if max(abs(y_fir)) > 0, y_fir = y_fir / max(abs(y_fir)); end

t_out   = (0:out_idx-1) / fs_out;
ref_sig = sin(2*pi*f1*t_out);

%% ================================================
%  SHARED PLOT SETTINGS
%% ================================================
C_IN    = [0.30 0.30 0.30];   % Grey    — raw input
C_INT   = [0.85 0.25 0.10];   % Red     — integrators
C_COMB  = [0.10 0.45 0.80];   % Blue    — comb stages
C_CIC   = [0.90 0.50 0.00];   % Orange  — CIC output
C_FIR   = [0.45 0.00 0.80];   % Purple  — FIR output
C_REF   = [0.00 0.00 0.00];   % Black   — reference

set(0,'DefaultAxesFontSize',10,'DefaultAxesFontName','Helvetica Neue');

n_show    = min(400, out_idx);          % Output samples to show
n_show_in = n_show * R;                 % Corresponding input samples
t_in_us   = (0:n_show_in-1) / fs * 1e6;
t_out_us  = (0:n_show-1) / fs_out * 1e6;

%% ================================================
%  FIGURE 1: INPUT SIGNAL  (clean big panel)
%% ================================================
figure('Name','1 — Input Signal','Color','w','Position',[40 600 1100 340]);

subplot(1,2,1);
plot(t_in_us(1:min(500,n_show_in)), x(1:min(500,n_show_in)), ...
    'Color',C_IN,'LineWidth',0.8);
title('Input Signal  (first 500 samples)','FontWeight','bold');
xlabel('Time  (\mus)'); ylabel('Normalised Amplitude');
grid on; box off;
annotation_str = sprintf('f_s = %.0f MHz\nf_{signal} = %.0f MHz\nInterf: 40 & 70 MHz', ...
    fs/1e6, f1/1e6);
text(0.98, 0.95, annotation_str, 'Units','normalized', ...
    'HorizontalAlignment','right','VerticalAlignment','top', ...
    'FontSize',9,'BackgroundColor',[1 1 1 0.7],'EdgeColor',[0.8 0.8 0.8]);

subplot(1,2,2);
Nf    = 4096;
X_fft = fft(x, Nf);
f_in  = linspace(0, fs/2, Nf/2+1) / 1e6;
dB_fn = @(v) 20*log10(abs(v) / (max(abs(v)) + eps) + eps);
plot(f_in, dB_fn(X_fft(1:Nf/2+1)), 'Color',C_IN,'LineWidth',1);
xline(f1/1e6,  'g--','LineWidth',1.5,'DisplayName',sprintf('Signal %.0f MHz',f1/1e6));
xline(40, 'r--','LineWidth',1,'DisplayName','Interf 40 MHz');
xline(70, 'r--','LineWidth',1,'DisplayName','Interf 70 MHz');
title('Input Spectrum','FontWeight','bold');
xlabel('Frequency  (MHz)'); ylabel('Magnitude  (dB)');
xlim([0 fs/2/1e6]); ylim([-80 5]); grid on; box off;
legend('Spectrum','Signal 5 MHz','Interferers','Location','northeast','FontSize',8);

sgtitle(sprintf('STAGE 0 — Raw Input   (f_s = %.0f MHz)', fs/1e6), ...
    'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 2: CIC INTEGRATOR STAGES  (high-rate section)
%% ================================================
figure('Name','2 — CIC Integrators','Color','w','Position',[40 220 1100 560]);

shades_int = [0.95 0.30 0.10; 0.75 0.15 0.05; 0.55 0.05 0.00];

for s = 1:N
    subplot(N, 1, s);
    clr = shades_int(min(s,3), :);
    plot(t_in_us, int_disp(s, 1:n_show_in), 'Color',clr,'LineWidth',0.8);
    title(sprintf('Integrator %d   y[n] = y[n-1] + x[n]   (runs at f_s = %.0f MHz)', ...
        s, fs/1e6),'FontWeight','bold','Color',clr);
    ylabel('Normalised'); grid on; box off;
    if s < N, set(gca,'XTickLabel',[]); end
end
xlabel('Time  (\mus)');
sgtitle(sprintf('STAGE 1 — CIC Integrators (%d cascaded,  high rate)', N), ...
    'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 3: DECIMATION + COMB STAGES  (low-rate section)
%% ================================================
figure('Name','3 — Decimation and Comb','Color','w','Position',[40 220 1100 560]);

shades_comb = [0.15 0.55 0.90; 0.08 0.35 0.70; 0.04 0.18 0.50];

for s = 1:N
    subplot(N, 1, s);
    clr = shades_comb(min(s,3), :);
    stem(t_out_us, comb_disp(s, 1:n_show), ...
        'filled','MarkerSize',3,'Color',clr,'LineWidth',0.9);
    title(sprintf('Comb %d   d[n] = y[n] - y[n-1]   (runs at f_s/%d = %.0f MHz)', ...
        s, R, fs_out/1e6),'FontWeight','bold','Color',clr);
    ylabel('Normalised'); grid on; box off;
    if s < N, set(gca,'XTickLabel',[]); end
end
xlabel('Time  (\mus)');
sgtitle(sprintf('STAGE 2 — Decimation (÷%d)  +  CIC Comb Sections (%d cascaded,  low rate)', ...
    R, N), 'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 4: PIPELINED CIC OUTPUT  (before FIR)
%% ================================================
figure('Name','4 — Pipelined CIC Output','Color','w','Position',[40 220 1100 500]);

subplot(2,1,1);
stem(t_out_us, y_cic(1:n_show), 'filled','MarkerSize',4, ...
    'Color',C_CIC,'LineWidth',1.1);
hold on;
plot(t_out_us, ref_sig(1:n_show), '--','Color',C_REF,'LineWidth',1);
title('Pipelined CIC Output  (normalised,  no FIR yet)','FontWeight','bold');
xlabel('Time  (\mus)'); ylabel('Amplitude');
legend('Pipelined CIC','Clean 5 MHz reference','Location','northeast');
grid on; box off;

subplot(2,1,2);
Y_cic_fft = fft(y_cic, Nf);
f_out = linspace(0, fs_out/2, Nf/2+1) / 1e6;
plot(f_out, dB_fn(Y_cic_fft(1:Nf/2+1)), 'Color',C_CIC,'LineWidth',1.5);
hold on;
xline(f1/1e6, 'g--','LineWidth',1.5,'DisplayName',sprintf('Signal %.0f MHz',f1/1e6));
xline(fc/1e6, 'm--','LineWidth',1,'DisplayName',sprintf('FIR cutoff %.0f MHz',fc/1e6));
title('CIC Output Spectrum  (note droop at signal band)', ...
    'FontWeight','bold');
xlabel('Frequency  (MHz)'); ylabel('Magnitude  (dB)');
xlim([0 fs_out/2/1e6]); ylim([-80 5]); grid on; box off;
legend('CIC spectrum','Signal','FIR cutoff','Location','northeast','FontSize',8);

sgtitle(sprintf('STAGE 3 — Pipelined CIC Output   (f_s out = %.0f MHz,  %dx decimated)', ...
    fs_out/1e6, R), 'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 5: FIR-COMPENSATED FINAL OUTPUT
%% ================================================
figure('Name','5 — FIR Output (Final)','Color','w','Position',[40 220 1100 500]);

subplot(2,1,1);
plot(t_out_us, y_fir(1:n_show), 'Color',C_FIR,'LineWidth',1.5);
hold on;
plot(t_out_us, ref_sig(1:n_show), '--','Color',C_REF,'LineWidth',1);
title('FIR-Compensated Output  (group delay corrected)','FontWeight','bold');
xlabel('Time  (\mus)'); ylabel('Amplitude');
legend('Final pipeline output','Clean 5 MHz reference','Location','northeast');
grid on; box off;

subplot(2,1,2);
Y_fir_fft = fft(y_fir, Nf);
plot(f_out, dB_fn(Y_fir_fft(1:Nf/2+1)), 'Color',C_FIR,'LineWidth',1.5);
hold on;
xline(f1/1e6, 'g--','LineWidth',1.5,'DisplayName',sprintf('Signal %.0f MHz',f1/1e6));
xline(fc/1e6, 'm--','LineWidth',1,'DisplayName',sprintf('Cutoff %.0f MHz',fc/1e6));
title('FIR Output Spectrum  (interferers suppressed, passband flat)', ...
    'FontWeight','bold');
xlabel('Frequency  (MHz)'); ylabel('Magnitude  (dB)');
xlim([0 fs_out/2/1e6]); ylim([-80 5]); grid on; box off;
legend('FIR spectrum','Signal','Cutoff','Location','northeast','FontSize',8);

sgtitle('STAGE 4 — FIR Droop-Correction Filter Output  (final signal)', ...
    'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 6: INPUT vs CIC vs FIR  — SIDE-BY-SIDE COMPARISON
%% ================================================
figure('Name','6 — Full Pipeline Comparison','Color','w','Position',[40 80 1300 650]);

% --- Time domain: 3 rows ---
ax1 = subplot(3,2,1);
plot(t_in_us(1:min(800,n_show_in)), x(1:min(800,n_show_in)), ...
    'Color',C_IN,'LineWidth',0.7);
title('INPUT  (200 MHz,  noisy + interferers)','FontWeight','bold','Color',C_IN);
ylabel('Amplitude'); grid on; box off; set(gca,'XTickLabel',[]);

ax2 = subplot(3,2,3);
stem(t_out_us, y_cic(1:n_show), 'filled','MarkerSize',3, ...
    'Color',C_CIC,'LineWidth',0.9);
hold on;
plot(t_out_us, ref_sig(1:n_show),'--','Color',[0 0 0 0.4],'LineWidth',0.8);
title(sprintf('AFTER PIPELINED CIC  (%.0f MHz,  ÷%d)', fs_out/1e6, R), ...
    'FontWeight','bold','Color',C_CIC);
ylabel('Amplitude'); grid on; box off; set(gca,'XTickLabel',[]);

ax3 = subplot(3,2,5);
plot(t_out_us, y_fir(1:n_show), 'Color',C_FIR,'LineWidth',1.5);
hold on;
plot(t_out_us, ref_sig(1:n_show),'--','Color',C_REF,'LineWidth',0.9);
title('AFTER FIR  (final, droop corrected)','FontWeight','bold','Color',C_FIR);
xlabel('Time  (\mus)'); ylabel('Amplitude'); grid on; box off;

linkaxes([ax2 ax3],'x');

% --- Spectrum: 3 rows ---
subplot(3,2,2);
plot(f_in, dB_fn(X_fft(1:Nf/2+1)), 'Color',C_IN,'LineWidth',1);
xline(f1/1e6,'g--','LineWidth',1.2); xline(40,'r--','LineWidth',1); xline(70,'r--','LineWidth',1);
title('Input Spectrum','FontWeight','bold','Color',C_IN);
ylabel('dB'); xlim([0 fs/2/1e6]); ylim([-80 5]); grid on; box off;
set(gca,'XTickLabel',[]);

subplot(3,2,4);
plot(f_out, dB_fn(Y_cic_fft(1:Nf/2+1)), 'Color',C_CIC,'LineWidth',1.2);
xline(f1/1e6,'g--','LineWidth',1.2); xline(fc/1e6,'m--','LineWidth',1);
title('CIC Output Spectrum','FontWeight','bold','Color',C_CIC);
ylabel('dB'); xlim([0 fs_out/2/1e6]); ylim([-80 5]); grid on; box off;
set(gca,'XTickLabel',[]);

subplot(3,2,6);
plot(f_out, dB_fn(Y_fir_fft(1:Nf/2+1)), 'Color',C_FIR,'LineWidth',1.5);
xline(f1/1e6,'g--','LineWidth',1.2); xline(fc/1e6,'m--','LineWidth',1);
title('FIR Output Spectrum','FontWeight','bold','Color',C_FIR);
xlabel('Frequency  (MHz)'); ylabel('dB');
xlim([0 fs_out/2/1e6]); ylim([-80 5]); grid on; box off;

sgtitle(sprintf('Full Pipeline Comparison:  Input → Pipelined CIC (R=%d, N=%d) → FIR', R, N), ...
    'FontSize',13,'FontWeight','bold');

%% ================================================
%  FIGURE 7: CIC DROOP + FIR RESPONSE
%% ================================================
Nf2     = 2048;
f_droop = linspace(0, fs_out/2, Nf2);
H_cic   = abs(sin(pi*f_droop*R/fs) ./ (R*sin(pi*f_droop/fs) + eps)).^N;
H_cic   = H_cic / H_cic(1);
H_fir_f = abs(fft(b, Nf2));
H_fir_f = H_fir_f(1:Nf2) / H_fir_f(1);
H_total = H_cic .* H_fir_f';
H_total = H_total / H_total(1);

figure('Name','7 — Frequency Response','Color','w','Position',[40 80 950 420]);
plot(f_droop/1e6, H_cic,   'Color',C_CIC,  'LineWidth',2.5,'DisplayName','CIC (has droop)');
hold on;
plot(f_droop/1e6, H_fir_f, 'Color',C_FIR,  'LineWidth',2.0,'DisplayName','FIR (corrects droop)');
plot(f_droop/1e6, H_total,  'Color',[0 0.6 0.2],'LineWidth',2.5,'DisplayName','CIC × FIR (combined)');
yline(0.707,'k--','LineWidth',1,'DisplayName','-3 dB');
xline(f1/1e6,'g--','LineWidth',1.8,'DisplayName',sprintf('Signal %.0f MHz',f1/1e6));
title('Frequency Response: CIC Droop and FIR Correction','FontWeight','bold');
xlabel('Frequency  (MHz)'); ylabel('Normalised Magnitude');
legend('Location','southwest','FontSize',9);
ylim([0 1.2]); xlim([0 fs_out/2/1e6]); grid on; box off;
sgtitle('CIC Droop + FIR Compensation — Passband Should Be Flat Near 1.0', ...
    'FontSize',12,'FontWeight','bold');

%% ================================================
%  FIGURE 8: BATCH VALIDATION  (pipeline must match batch)
%% ================================================
y_b = x;
for i = 1:N, y_b = cumsum(y_b); end
y_b = y_b(R:R:end);
for i = 1:N, y_b = [y_b(1), diff(y_b)]; end
y_b = y_b / (R^N);
if max(abs(y_b)) > 0, y_b = y_b / max(abs(y_b)); end
Lc  = min(length(y_cic), length(y_b));
err = y_cic(1:Lc) - y_b(1:Lc);
t_c = (0:Lc-1) / fs_out * 1e6;

figure('Name','8 — Pipeline vs Batch Validation','Color','w','Position',[40 80 1100 560]);

subplot(3,1,1);
plot(t_c, y_b(1:Lc), 'Color',C_IN,'LineWidth',1.4);
title('Batch CIC  (whole signal at once — reference)','FontWeight','bold');
ylabel('Amplitude'); grid on; box off; set(gca,'XTickLabel',[]);

subplot(3,1,2);
plot(t_c, y_cic(1:Lc), 'Color',C_CIC,'LineWidth',1.4);
title('Pipelined CIC  (sample-by-sample — hardware equivalent)','FontWeight','bold');
ylabel('Amplitude'); grid on; box off; set(gca,'XTickLabel',[]);

subplot(3,1,3);
plot(t_c, err,'Color',[0.8 0 0],'LineWidth',0.9);
yline(0,'k--','LineWidth',1);
title(sprintf('Difference  (max error = %.2e) — should be near zero', max(abs(err))), ...
    'FontWeight','bold');
xlabel('Time  (\mus)'); ylabel('Error'); grid on; box off;

if max(abs(err)) < 1e-6
    match_str = '✓  PIPELINE MATCHES BATCH — Validated';
    match_col = [0 0.55 0.1];
else
    match_str = '✗  MISMATCH DETECTED — Check pipeline logic';
    match_col = [0.8 0 0];
end
sgtitle(match_str,'FontSize',13,'FontWeight','bold','Color',match_col);

%% ================================================
%  CONSOLE REPORT
%% ================================================
pwr = @(v) mean(v.^2);
Lr  = min(length(ref_sig), length(y_cic));
Lf  = min(length(y_fir),   length(ref_sig));
snr_in  = 10*log10(pwr(signal) / max(pwr(x(1:length(signal)) - signal), eps));
snr_cic = 10*log10(pwr(ref_sig(1:Lr)) / max(pwr(y_cic(1:Lr) - ref_sig(1:Lr)), eps));
snr_fir = 10*log10(pwr(ref_sig(1:Lf)) / max(pwr(y_fir(1:Lf) - ref_sig(1:Lf)), eps));

fprintf('\n==========================================\n');
fprintf('         FULL PIPELINE REPORT\n');
fprintf('==========================================\n');
fprintf('Input  sampling rate   : %.0f MHz\n',  fs/1e6);
fprintf('Output sampling rate   : %.0f MHz\n',  fs_out/1e6);
fprintf('Decimation factor R    : %d\n',         R);
fprintf('CIC stages N           : %d\n',         N);
fprintf('FIR filter order       : %d taps\n',    order+1);
fprintf('FIR group delay        : %d samples\n', delay);
fprintf('------------------------------------------\n');
fprintf('SNR at input           : %6.2f dB\n', snr_in);
fprintf('SNR after pipelined CIC: %6.2f dB\n', snr_cic);
fprintf('SNR after FIR          : %6.2f dB\n', snr_fir);
fprintf('Total SNR improvement  : %6.2f dB\n', snr_fir - snr_in);
fprintf('------------------------------------------\n');
fprintf('Pipeline vs batch err  : %.2e\n',      max(abs(err)));
fprintf('Validation             : %s\n',         match_str);
fprintf('==========================================\n');
