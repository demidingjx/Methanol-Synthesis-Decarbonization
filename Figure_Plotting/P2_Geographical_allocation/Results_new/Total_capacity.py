import pandas as pd
from pathlib import Path

                               
BASE = Path(r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new")
runs_map = {
    "PEM": [
        {"year": "2040", "ed": "25"},
        {"year": "2040", "ed": "50"},
        {"year": "2040", "ed": "55"},
        {"year": "2040", "ed": "75"},
        {"year": "2040", "ed": "100"},
        {"year": "2050", "ed": "25"},
        {"year": "2050", "ed": "50"},
        {"year": "2050", "ed": "76"},
        {"year": "2050", "ed": "75"},
        {"year": "2050", "ed": "100"},
    ],
    "SOE": [
        {"year": "2040", "ed": "21"},
        {"year": "2040", "ed": "50"},
        {"year": "2040", "ed": "25"},
        {"year": "2040", "ed": "75"},
        {"year": "2040", "ed": "100"},
        {"year": "2050", "ed": "25"},
        {"year": "2050", "ed": "50"},
        {"year": "2050", "ed": "59"},
        {"year": "2050", "ed": "75"},
        {"year": "2050", "ed": "100"},
    ],
}

            
rows = []
for el, runs in runs_map.items():
    storage_col = "HST" if el == "PEM" else "SST"
    for r in runs:
        y, ed = r["year"], r["ed"]
        fp = BASE / el / y / f"ED{ed}" / f"Nom_size_{el}_{y}_ED{ed}_2.xlsx"
        if not fp.exists():
            print(f"[SKIP] 缺文件: {fp}")
            continue

        df = pd.read_excel(fp, sheet_name="GW_tech")

        def s(col):
            return df[col].sum() if col in df.columns else 0.0

        rows.append({
            "EL": el,              
            "Year": y,             
            "ED": ed,              
            "PV": s("PV"),         
            "WT": s("WT"),         
            el: s(el),                          
            storage_col: s(storage_col),               
            "LiB": s("LiB"),            
        })

            
out_path = BASE / "Aggregated_totals_PEM_SOE.xlsx"
if rows:
    df_out = pd.DataFrame(rows)
                             
    ordered_cols = ["EL", "Year", "ED", "PV", "WT", "PEM", "SOE", "HST", "SST", "LiB"]
    keep = [c for c in ordered_cols if c in df_out.columns]
    df_out = df_out[keep]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_excel(out_path, index=False)
    print(f"已写入: {out_path}")
else:
    print("无可写入数据。")
