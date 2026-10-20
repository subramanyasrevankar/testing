# CodeTrace Large-File Bug Test

This repository tests CodeTrace's ability to investigate a bug in a relatively large Python source file.

## Files

- `pricing.py`: Pricing service containing an intentional bug.
- `BUG_REPORT.txt`: Bug description to submit to CodeTrace.

## Run

Requires Python 3.10 or newer. No third-party packages are required to run `pricing.py`.

```bash
python pricing.py
```

## Testing objective

CodeTrace should identify the incorrect percentage calculation, locate the exact source line, explain the root cause, and generate a minimal unified diff.

The fix must preserve input validation and unrelated functionality. Sandbox verification must execute meaningful behavioral tests before approval and pull-request creation are enabled.
