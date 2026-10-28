# Nakuru Dairy Co-op: Monthly Zone Report

A small Python and pandas project that combines milk collection records with farmer details and prints a clean monthly summary by zone.

## What the script does

1. Reads the two Excel input files.
2. Matches records using farmer name (ignoring capitalization and surrounding spaces).
3. Filters collection records to the current calendar month.
4. Calculates each collection's payout using `litres × payment_rate_per_litre`.
5. Uses a pandas pivot table to calculate total litres and total payout per zone.
6. Identifies the top farmer in each zone by total litres collected during the month.
7. Prints a client-ready summary in the terminal.

## Input files required

Keep these two files in the same folder as `dairy_zone_report.py`.

### 1. `milk_collection.xlsx`

One row per farmer collection event, with these columns:

| Column | Meaning | Example |
|---|---|---|
| `farmer_name` | Farmer's name | Peter Kiptoo |
| `date` | Collection date | 2026-10-10 |
| `litres` | Litres collected | 32 |

### 2. `farmer_details.xlsx`

One row per farmer, with these columns:

| Column | Meaning | Example |
|---|---|---|
| `farmer_name` | Farmer's name; must match the collection file | Peter Kiptoo |
| `zone` | Farmer's zone | North |
| `payment_rate_per_litre` | Amount paid per litre in KES | 50.00 |

Sample input files with 12 farmers across North, Central, and South zones are included. The sample collection dates are in October 2026.

## Requirements

- Python 3.10 or newer
- pandas
- openpyxl

Install the dependencies:

```bash
python -m pip install pandas openpyxl
```

## Run the report

Place the two Excel files beside the script, open a terminal in that folder, and run:

```bash
python dairy_zone_report.py
```

The script automatically uses the current calendar month. If no collection rows exist for the current month, it reports that clearly. For a historical report, change the month-filter logic in `build_zone_summary()` or adapt it to accept a month as an argument.

## Example output

The exact totals are calculated from the included sample files when you run the script. The table contains:

- `Zone`
- `Total litres`
- `Total payout (KES)`
- `Top farmer (by litres)`

## Important assumptions

- A farmer has one zone and one payment rate in the farmer details file.
- The top farmer means the farmer with the highest total litres in that zone for the month.
- Payout is calculated from the farmer's rate multiplied by collected litres.
- This is a sample project; verify real farmer names, rates, dates, and payment rules before using it for actual payments.
