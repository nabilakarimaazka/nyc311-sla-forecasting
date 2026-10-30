# NYC 311: Forecasting Demand & Predicting SLA Breaches

Proyek data engineering + data science menggunakan data publik NYC 311 Service Requests (agency HPD).

## Tujuan
1. Memprediksi volume keluhan harian per jenis layanan
2. Memprediksi tiket mana yang berisiko melanggar SLA

## Status
- [x] Step 1: Ekstraksi data dari Socrata API ke Parquet
- [ ] Step 2: Cleaning & definisi SLA
- [ ] Step 3: EDA
- [ ] Step 4: Forecasting
- [ ] Step 5: Prediksi SLA breach
- [ ] Step 6: Pipeline & dashboard

## Cara menjalankan
pip install -r requirements.txt
python src/extract_311.py --start 2022-01 --end 2026-09