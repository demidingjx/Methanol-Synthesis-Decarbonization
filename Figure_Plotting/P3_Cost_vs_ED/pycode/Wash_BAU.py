import pandas as pd
from pathlib import Path

# ===== 参数 =====
el = "PEM"  # "SOE" 或 "PEM"
file_path = Path(fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\pycode\{el}\bar_allyears\merged_CB_UE_NEW.xlsx")
out_path  = file_path.with_name(f"merged_CB_UE_NEW.xlsx")  # 如要覆盖就改为 file_path

target_sheets = ["2030_CB", "2040_CB", "2050_CB"]

dfs = pd.read_excel(file_path, sheet_name=None)

for sh in target_sheets:
    if sh not in dfs:
        print(f"[跳过] 未找到工作表: {sh}")
        continue
    df = dfs[sh].copy()

    first_col = df.columns[0]

    # 精确匹配 CO2e 和 CO2
    co2e_rows = df[first_col] == "CO2e"
    co2_rows  = df[first_col] == "CO2"

    if not co2e_rows.any():
        print(f"[跳过] {sh} 未找到 CO2e 行")
        continue
    if not co2_rows.any():
        print(f"[跳过] {sh} 未找到 CO2 行")
        continue

    # 数值列索引
    num_cols = df.columns[1:]

    # 替换 CO2e 行为 CO2e + CO2
    df.loc[co2e_rows, num_cols] = df.loc[co2e_rows, num_cols].fillna(0).values + df.loc[co2_rows, num_cols].fillna(0).values

    dfs[sh] = df

# 保存
with pd.ExcelWriter(out_path, engine="openpyxl") as w:
    for name, d in dfs.items():
        d.to_excel(w, sheet_name=name, index=False)

print(f"完成：{out_path}")
