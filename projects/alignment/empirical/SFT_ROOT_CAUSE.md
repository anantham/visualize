# SFT failure root cause note

Date: 2026-07-07

## Verdict

The old SFT run most likely died from MPS driver memory pressure, not from a
deterministic dataset example, Python exception, trainer bug, or normal model
context overflow.

The evidence is strong but not a perfect smoking gun: the original process left
no Python traceback, no crash report, and no checkpoint. macOS logs from the
failure window show sustained memory pressure and recurring jetsam telemetry, but
not a clean "Python was killed" line.

## Original failure

Source files:

- `../alignment-spike/sft_train.py`
- `../alignment-spike/sft_train.log`

The script ran:

- model: `HuggingFaceTB/SmolLM2-360M`
- tokenizer: `HuggingFaceTB/SmolLM2-360M-Instruct`
- dataset: 4000 streaming `HuggingFaceTB/smoltalk` examples
- device: MPS
- physical batch: 4
- gradient accumulation: 2
- max length: 1024
- max steps: 400
- save steps: 50

It reached step 27/400 and then exited after:

```text
resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown
```

There was no traceback, no explicit OOM line, no `DONE`, and no checkpoint
because `SAVE_STEPS=50` meant the first checkpoint would only happen at step 50.

The old progress trace also shows a major stall:

- steps 1-21: mostly seconds per step
- step 22: jumped to about 7 minutes
- step 27: another multi-minute delay, then exit

## Diagnostics run

Diagnostic runner:

- `projects/alignment/empirical/sft_diagnostic.py`

Logged runs:

- smoke: `projects/alignment/empirical/sft_diag_runs/20260707-095925/`
- original-shape repro: `projects/alignment/empirical/sft_diag_runs/20260707-100107/`
- smaller-physical-batch repro: `projects/alignment/empirical/sft_diag_runs/20260707-101212/`

The original-shape repro crossed the old death point and completed 35 steps, so
the failure is not deterministic at step 22 or 27.

Final memory for original-shape repro:

```json
{
  "current_allocated": 9484996608,
  "driver_allocated": 60542910464,
  "recommended_max": 55662788608
}
```

Important detail: current tensor allocation stayed around 9.5 GB, but MPS driver
allocation ballooned above the recommended max, reaching about 60.5 GB against a
recommended cap of about 55.7 GB.

The smaller-physical-batch run used the same effective batch size:

- physical batch: 2
- gradient accumulation: 4

It crossed step 28 cleanly with no old-style stall.

Final memory for smaller-physical-batch repro:

```json
{
  "current_allocated": 6813127936,
  "driver_allocated": 42456399872,
  "recommended_max": 55662788608
}
```

That is the clearest mitigation signal: reducing the physical MPS batch lowered
current allocation and kept driver allocation far below the pressure region while
preserving effective batch size.

## Dataset/context check

Length stats from the diagnostic slice:

```json
{
  "min": 49,
  "median": 651,
  "p95": 2152,
  "p99": 3679,
  "max": 23799,
  "gt_max_length": 1521,
  "gt_model_context": 14
}
```

There are very long examples, including 14 above the model context warning
threshold, but this is not the immediate root cause. The trainer used
`max_length=1024`, and both repro runs completed through the old failure zone
with the same data slice.

## macOS evidence

The unified log query over 2026-07-04 22:50-23:10 IST found:

- repeated `Memory Pressure Policy` messages with observed pressure `4.00`
- recurring `com.apple.memory-maintenance.report-jetsam-telemetry`
- no Python crash report in `~/Library/Logs/DiagnosticReports`
- no clear unified-log line saying Python was killed

So the conservative reading is: memory pressure was definitely present; a clean
kill receipt was not found.

## Working hypothesis

The most likely chain is:

1. batch 4 fp32 SFT on MPS had modest live tensor memory but very high driver
   allocation/cache growth.
2. driver allocation approached or exceeded the recommended MPS memory cap.
3. system memory pressure was already high in the old failure window.
4. the run stalled as MPS/OS memory management fought for space.
5. the process exited before its first checkpoint, leaving only the leaked
   semaphore shutdown warning.

## Recommended next SFT run

Use the smaller physical batch and checkpoint earlier:

```bash
N_EXAMPLES=4000 MAX_STEPS=400 SAVE_STEPS=25 BATCH=2 GRAD_ACCUM=4 MAX_LENGTH=1024 \
  ~/.venv-align/bin/python projects/alignment/empirical/sft_diagnostic.py
```

Operationally:

- run when other memory-heavy apps are quiet
- keep the diagnostic logging enabled
- checkpoint before step 50
- treat a completed 400-step run as the actual stability proof

