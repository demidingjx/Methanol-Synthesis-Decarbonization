import pandas as pd
from pathlib import Path

# ─── 1. 定义要处理的技术和存储 ───────────────
el = "PEM"   # 可选 "PEM" or "SOE"
st = "HST"   # 可选 "HST" or "SST"

# ─── 2. 定位到对应目录 ───────────────────────
base_dir    = Path(r"F:\2025_Methanol_synthesis\3_GAMS\P4_Sensitivity_Analysis\excel")
results_dir = base_dir / el
if not results_dir.exists():
    raise FileNotFoundError(f"Directory not found: {results_dir}")

# ─── 3. 匹配所有 Data_<el>_*.xlsx ────────────
files = sorted(results_dir.glob(f"Data_{el}_*.xlsx"))
if not files:
    raise FileNotFoundError(f"No matching files Data_{el}_*.xlsx in {results_dir}")

# ─── 4. 读取并聚合 Capacity、Ratio、Capacity（可选）以及 Energy_TWh ───
Capacity_records = []
ratio_records = []
energy_records = []

for fp in files:
    scenario = fp.stem.replace(f"Data_{el}_", "")
    
    # --- 4.1 处理 Capacity sheet
    df_Capacity = pd.read_excel(fp, sheet_name="Capacity")
    df_Capacity.columns = df_Capacity.columns.str.strip().str.replace(" ", "").str.lower()
    Capacity_records.append({
        "Scenario": scenario,
        "PV":    df_Capacity.at[0, "pv"],
        "WT":    df_Capacity.at[0, "wt"],
        "LiB":   df_Capacity.at[0, "lib"] if "lib" in df_Capacity.columns else 0,
        el:      df_Capacity.at[0, el.lower()] if el.lower() in df_Capacity.columns else 0,
        st:      df_Capacity.at[0, st.lower()] if st.lower() in df_Capacity.columns else 0
    })

    # --- 4.2 process Ratio sheet (handle possible typos) ---
    try:
        df_ratio = pd.read_excel(fp, sheet_name="Ratio")
    except ValueError:
        df_ratio = pd.read_excel(fp, sheet_name="Raio")

    df_ratio.columns = (
        df_ratio.columns
        .str.strip()
        .str.replace(" ", "")
        .str.lower()
    )

    ratio_records.append({
        "Scenario": scenario,
        "LCOM":   df_ratio.at[0, "lcom"],
        "LCOC":   df_ratio.at[0, "lcoc"],
        "Ratio":  df_ratio.at[0, "ratio"],
        "LCCR":  df_ratio.at[0, "lccr"],
    })


    # --- 4.3 处理 Energy_TWh sheet
    df_energy = pd.read_excel(fp, sheet_name="Energy_TWh")
    # 假设列名同 Capacity：PV, WT, LiB, el, st
    df_energy.columns = df_energy.columns.str.strip().str.replace(" ", "").str.lower()
    energy_records.append({
        "Scenario": scenario,
        "PV":  df_energy.at[0, "pv"],
        "WT":  df_energy.at[0, "wt"],
        "Grid":  df_energy.at[0, "grid"] if "grid" in df_energy.columns else 0,
        f"{el}": df_energy.at[0, el.lower()] if el.lower() in df_energy.columns else 0
    })

# ─── 5. 构建各自的 DataFrame ───────────────────
df_Capacity_summary  = pd.DataFrame(Capacity_records)
df_ratio_summary  = pd.DataFrame(ratio_records)
df_energy_summary = pd.DataFrame(energy_records)

# ─── 6. 写入同一个 Excel 的多个 sheet ─────────
output_file = results_dir / f"Scenario_Summary_{el}_{st}.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_Capacity_summary.to_excel(writer, sheet_name="Scenario", index=False)
    df_ratio_summary.to_excel(writer, sheet_name="Metrics",  index=False)
    df_energy_summary.to_excel(writer, sheet_name="Energy",   index=False)

print(f"Aggregated results written to:\n  {output_file}")
