from pathlib import Path
import pandas as pd

COLLECTIONS_FILE = Path("milk_collection.xlsx")
FARMERS_FILE = Path("farmer_details.xlsx")


def build_zone_summary(collections_file=COLLECTIONS_FILE, farmers_file=FARMERS_FILE):
    """Return monthly total litres, payout, and top farmer for each zone."""
    collections = pd.read_excel(collections_file)
    farmers = pd.read_excel(farmers_file)

    # Preserve display names, but match using a normalized helper column.
    collections["farmer_name_key"] = (
        collections["farmer_name"].astype(str).str.strip().str.casefold()
    )
    farmers["farmer_name_key"] = (
        farmers["farmer_name"].astype(str).str.strip().str.casefold()
    )

    collections["date"] = pd.to_datetime(collections["date"], errors="coerce")
    collections["litres"] = pd.to_numeric(collections["litres"], errors="coerce")
    farmers["payment_rate_per_litre"] = pd.to_numeric(
        farmers["payment_rate_per_litre"], errors="coerce"
    )

    # Keep records from the current calendar month.
    today = pd.Timestamp.today()
    this_month = collections[
        (collections["date"].dt.year == today.year)
        & (collections["date"].dt.month == today.month)
    ].copy()

    if this_month.empty:
        raise ValueError(
            f"No milk collection records found for {today.strftime('%B %Y')}. "
            "Check the dates in milk_collection.xlsx."
        )

    merged = this_month.merge(
        farmers[["farmer_name_key", "farmer_name", "zone", "payment_rate_per_litre"]],
        on="farmer_name_key",
        how="left",
        validate="many_to_one",
        indicator=True,
        suffixes=("_collection", "_details"),
    )

    unmatched = merged.loc[merged["_merge"] != "both", "farmer_name_collection"].unique()
    if len(unmatched):
        raise ValueError(
            "These collection records have no matching farmer details: "
            + ", ".join(unmatched)
        )
    merged = merged.drop(columns=["_merge", "farmer_name_key"])

    if merged[["litres", "payment_rate_per_litre"]].isna().any().any():
        raise ValueError(
            "Some litres or payment rates are missing or invalid. "
            "Check both input spreadsheets."
        )

    merged["payout"] = merged["litres"] * merged["payment_rate_per_litre"]

    # Pivot to get monthly totals by zone.
    zone_totals = merged.pivot_table(
        index="zone",
        values=["litres", "payout"],
        aggfunc="sum",
        fill_value=0,
    )

    # Top farmer is the farmer with the most litres in each zone.
    farmer_totals = (
        merged.groupby(["zone", "farmer_name_details"], as_index=False)["litres"]
        .sum()
        .sort_values(["zone", "litres", "farmer_name_details"],
                     ascending=[True, False, True])
    )
    top_farmers = farmer_totals.drop_duplicates("zone").set_index("zone")[
        "farmer_name_details"
    ]

    summary = pd.DataFrame(index=zone_totals.index)
    summary["Total litres"] = zone_totals["litres"]
    summary["Total payout (KES)"] = zone_totals["payout"]
    summary["Top farmer (by litres)"] = top_farmers
    summary["Total litres"] = summary["Total litres"].round(1)
    summary["Total payout (KES)"] = summary["Total payout (KES)"].round(2)

    return summary.reset_index().rename(columns={"zone": "Zone"})



if __name__ == "__main__":
    try:
        report = build_zone_summary()

        print()
        print(
            f"NAKURU DAIRY CO-OP — ZONE SUMMARY "
            f"({pd.Timestamp.today():%B %Y})"
        )
        print("=" * 78)

        print(
            report.to_string(
                index=False,
                formatters={
                    "Total litres": lambda value: f"{value:,.1f}",
                    "Total payout (KES)": lambda value: f"KES {value:,.2f}",
                },
            )
        )

        print()
        print("Top farmer is ranked by total litres collected in the month.")

    except (FileNotFoundError, ValueError, KeyError, pd.errors.MergeError) as error:
        print()
        print(f"Could not create the report: {error}")
        print()
        print("Expected columns:")
        print("  milk_collection.xlsx: farmer_name, date, litres")
        print(
            "  farmer_details.xlsx: "
            "farmer_name, zone, payment_rate_per_litre"
        )
        raise SystemExit(1)
