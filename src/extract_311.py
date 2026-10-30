import argparse
import os
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
AGENCY = "HPD"
PAGE_SIZE = 50_000
OUT_DIR = Path("data/raw")

COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "due_date",
    "resolution_action_updated_date",
    "agency",
    "complaint_type",
    "descriptor",
    "location_type",
    "incident_zip",
    "borough",
    "community_board",
    "status",
    "open_data_channel_type",
    "latitude",
    "longitude",
]
DATE_COLS = ["created_date", "closed_date", "due_date", "resolution_action_updated_date"]


def month_range(start: str, end: str):
    """Hasilkan pasangan (awal_bulan, awal_bulan_berikutnya) dari start s/d end (format YYYY-MM)."""
    months = pd.period_range(start=start, end=end, freq="M")
    for m in months:
        yield m.start_time, (m + 1).start_time
        
def fetch_page(session: requests.Session, params: dict, retries: int = 5) -> list:
    """Ambil satu halaman hasil API, dengan retry + backoff kalau gagal."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(BASE_URL, params=params, timeout=120)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as err:
            wait = 2 ** attempt
            print(f"    gagal (percobaan {attempt}/{retries}): {err} -> tunggu {wait}s")
            time.sleep(wait)
    raise RuntimeError("API tetap gagal setelah beberapa kali percobaan")

def fetch_month(session: requests.Session, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Tarik semua baris HPD untuk satu bulan, halaman demi halaman."""
    where = (
        f"agency = '{AGENCY}' "
        f"AND created_date >= '{start:%Y-%m-%dT%H:%M:%S}' "
        f"AND created_date < '{end:%Y-%m-%dT%H:%M:%S}'"
    )
    print("    filter:", where)
    rows, offset = [], 0
    while True:
        params = {
            "$select": ",".join(COLUMNS),
            "$where": where,
            "$order":"unique_key",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }
        page = fetch_page(session, params)
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        
    df = pd.DataFrame(rows, columns=COLUMNS)
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["unique_key"] = pd.to_numeric(df["unique_key"], errors="coerce")
    return df

def main():
    parser = argparse.ArgumentParser(description="Ekstrak NYC 311 (HPD) ke Parquet per bulan")
    parser.add_argument("--start", required=True, help="Bulan awal, format YYYY-MM")
    parser.add_argument("--end", required=True,  help="Bulan akhir, format YYYY-MM")
    parser.add_argument("--overwrite", action="store_true", help="Tarik ulang bulan yang filenya sudah ada")
    args = parser.parse_args()
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    token = os.getenv("NYC_APP_TOKEN")
    if token:
        session.headers["X-App-Token"] = token
        
    total = 0
    for start, end in month_range(args.start, args.end):
        out_file = OUT_DIR / f"hpd_{start:%Y_%m}.parquet"
        if out_file.exists() and not args.overwrite:
            print(f"{start:%Y-%m}: sudah ada, dilewati")
            continue
        
        print(f"{start:%Y-%m}: menarik data..")
        df = fetch_month(session, start, end)
        df.to_parquet(out_file, index=False)
        total += len(df)
        print(f"{start:%Y-%m}: {len(df):,} baris -> {out_file}")
        
    print(f"Selesai. Total baris baru: {total:,}")
    
if __name__ == "__main__":
    main()