# Ajaia TPM Assessment Build

Build artifact for the Ajaia Technical Project Manager assessment.

## Files

- `clean_exceptions.py` — CSV cleaning and validation script
- `exceptions.csv` — assessment sample data

## Run

```bash
python clean_exceptions.py --test
python clean_exceptions.py exceptions.csv
```

The script normalizes terminal names, carrier codes, and timestamp formats; summarizes exceptions by event type; and flags records or source conditions that require caution instead of guessing missing data.
