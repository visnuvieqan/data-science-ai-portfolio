#!/usr/bin/env python3
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile

TERMINAL_MAP = {
    "terminal 3": "Terminal 3",
    "t3": "Terminal 3",
}

KNOWN_EVENT_TYPES = {
    "missed_pickup",
    "doc_mismatch",
    "carrier_substitution",
}

TIMESTAMP_FORMATS = [
    ("%Y-%m-%d %H:%M:%S", False),
    ("%m/%d/%Y %H:%M", False),
    ("%Y-%m-%dT%H:%M:%SZ", True),
]

def normalize_terminal(value):
    raw = (value or "").strip()
    if not raw:
        return "", "terminal missing"
    key = raw.lower()
    if key in TERMINAL_MAP:
        return TERMINAL_MAP[key], None
    return raw, f"unrecognized terminal format: {raw}"

def normalize_carrier(value):
    raw = (value or "").strip()
    if not raw:
        return "", "carrier_code missing"
    return raw.upper(), None

def normalize_timestamp(value):
    raw = (value or "").strip()
    if not raw:
        return "", "event_ts missing"

    for fmt, is_utc in TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            if is_utc:
                dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat().replace("+00:00", "Z"), None

            out = dt.strftime("%Y-%m-%dT%H:%M:%S")
            if fmt == "%m/%d/%Y %H:%M" and dt.day <= 12 and dt.day != dt.month:
                return out, "ambiguous slash date (MM/DD vs DD/MM); assumed MM/DD"
            return out, None
        except ValueError:
            pass

    return raw, f"unrecognized timestamp format: {raw}"

def clean_file(input_path):
    input_path = Path(input_path)
    output_path = input_path.with_name("cleaned_exceptions.csv")
    summary_path = input_path.with_name("summary.txt")

    cleaned = []
    notes = []
    counts = Counter()
    seen_ids = set()

    with input_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        required = {"exception_id", "terminal", "event_type", "carrier_code", "event_ts"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for row in reader:
            row_notes = []

            exception_id = (row.get("exception_id") or "").strip()
            if not exception_id:
                row_notes.append("exception_id missing")
            elif exception_id in seen_ids:
                row_notes.append("duplicate exception_id")
            else:
                seen_ids.add(exception_id)

            terminal, note = normalize_terminal(row.get("terminal", ""))
            if note:
                row_notes.append(note)

            carrier, note = normalize_carrier(row.get("carrier_code", ""))
            if note:
                row_notes.append(note)

            timestamp, note = normalize_timestamp(row.get("event_ts", ""))
            if note:
                row_notes.append(note)

            event_type = (row.get("event_type") or "").strip().lower()
            if not event_type:
                row_notes.append("event_type missing")
            elif event_type not in KNOWN_EVENT_TYPES:
                row_notes.append(f"unexpected event_type: {event_type}")

            counts[event_type] += 1

            cleaned.append({
                "exception_id": exception_id,
                "terminal": terminal,
                "event_type": event_type,
                "carrier_code": carrier,
                "event_ts": timestamp,
                "cleaning_note": "; ".join(row_notes),
            })

            if row_notes:
                notes.append(f"{exception_id or '[missing exception_id]'}: " + "; ".join(row_notes))

    utc_rows = [r for r in cleaned if r["event_ts"].endswith("Z")]
    naive_rows = [r for r in cleaned if r["event_ts"] and not r["event_ts"].endswith("Z")]
    if utc_rows and naive_rows:
        msg = "explicit UTC while other rows have no timezone; not converted (terminal local zone not provided)"
        for r in utc_rows:
            r["cleaning_note"] = (r["cleaning_note"] + "; " if r["cleaning_note"] else "") + msg
            notes.append(f"{r['exception_id']}: {msg}")

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "exception_id",
                "terminal",
                "event_type",
                "carrier_code",
                "event_ts",
                "cleaning_note",
            ],
        )
        writer.writeheader()
        writer.writerows(cleaned)

    lines = ["Exception summary by event type:"]
    for event_type, count in sorted(counts.items()):
        lines.append(f"- {event_type}: {count}")

    lines += ["", "Records / source conditions requiring caution:"]
    if notes:
        lines.extend(f"- {note}" for note in notes)
    else:
        lines.append("- None")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path, summary_path, cleaned, counts, notes

def run_tests():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        sample = td / "sample.csv"
        sample.write_text(
            "exception_id,terminal,event_type,carrier_code,event_ts\n"
            "CPX-88213,Terminal 3,missed_pickup,swft,2026-08-14 09:12:00\n"
            "CPX-88214,Terminal 3,doc_mismatch,SWFT,08/14/2026 09:45\n"
            "CPX-88215,T3,missed_pickup,Swft,2026-08-14T10:03:00Z\n"
            "CPX-88216,Terminal 3,doc_mismatch,,2026-08-14 11:47:00\n"
            "CPX-88217,Terminal 3,carrier_substitution,RLCX,08/15/2026 08:02\n",
            encoding="utf-8",
        )

        _, _, rows, counts, notes = clean_file(sample)

        assert counts["missed_pickup"] == 2
        assert counts["doc_mismatch"] == 2
        assert counts["carrier_substitution"] == 1

        by_id = {r["exception_id"]: r for r in rows}
        assert by_id["CPX-88215"]["terminal"] == "Terminal 3"
        assert by_id["CPX-88215"]["carrier_code"] == "SWFT"
        assert by_id["CPX-88214"]["event_ts"] == "2026-08-14T09:45:00"
        assert "explicit UTC while other rows have no timezone" in by_id["CPX-88215"]["cleaning_note"]
        assert "carrier_code missing" in by_id["CPX-88216"]["cleaning_note"]

        ambiguous = td / "ambiguous.csv"
        ambiguous.write_text(
            "exception_id,terminal,event_type,carrier_code,event_ts\n"
            "A1,Terminal 3,missed_pickup,RLCX,03/04/2026 09:00\n",
            encoding="utf-8",
        )
        _, _, rows, _, _ = clean_file(ambiguous)
        assert "ambiguous slash date" in rows[0]["cleaning_note"]

        invalid = td / "invalid.csv"
        invalid.write_text(
            "exception_id,terminal,event_type,carrier_code,event_ts\n"
            "B1,Terminal 3,missed_pickupp,RLCX,2026-13-99 25:99:00\n"
            "B1,Terminal 3,missed_pickup,RLCX,2026-08-14 09:00:00\n",
            encoding="utf-8",
        )
        _, _, rows, _, _ = clean_file(invalid)
        assert "unexpected event_type" in rows[0]["cleaning_note"]
        assert "unrecognized timestamp format" in rows[0]["cleaning_note"]
        assert "duplicate exception_id" in rows[1]["cleaning_note"]

        bom = td / "bom.csv"
        bom.write_text(
            "\ufeffexception_id,terminal,event_type,carrier_code,event_ts\n"
            "C1,Terminal 3,missed_pickup,RLCX,2026-08-14 09:00:00\n",
            encoding="utf-8",
        )
        _, _, rows, _, _ = clean_file(bom)
        assert rows[0]["exception_id"] == "C1"

    print("All tests passed.")

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        run_tests()
        return

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python clean_exceptions.py exceptions.csv")
        print("  python clean_exceptions.py --test")
        sys.exit(1)

    output_path, summary_path, _, _, _ = clean_file(sys.argv[1])
    print(f"Wrote {output_path}")
    print(f"Wrote {summary_path}")
    print()
    print(summary_path.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
