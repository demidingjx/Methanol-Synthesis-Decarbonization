import pandas as pd
import os

# —————— 用户统一配置 ——————
el = "SOE"  # 可设置为 "PEM" 或 "SOE"


# 年份-ED 组合：2030/2040/2050 × {25, 100}


#--------------------------Supplementary 用这个--------------------------

base_dir = fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED"
output_file = fr"{base_dir}\pycode\{el}\bar_allyears\Supplementary_CityProv.xlsx"

years_eds = {
    "2030": ["25", "100"],
    "2040": ["25", "100"],
    "2050": ["25", "100"],  # 若上游写成"100%"也能兼容，见下方rstrip('%')
}


tasks = [{"year": y, "ed": ed} for y, eds in years_eds.items() for ed in eds]

# —————— 初始化 ——————
cb_sheets = {}
lcce_sheets = {}

# —— 辅助：按层级给出文件路径与友好名称 ——
LEVELS = {
    "C": "City",
    "P": "Prov",
    "S": "State",
}
def file_path(level, year, ed):
    return fr"{base_dir}\Results_new\{el}\{year}\TCB_UE_CAP_{level}_{el}_{year}_ED{ed}.xlsx"

def safe_read_cell(xlsx_path, sheet, r=0, c=1):
    v = pd.read_excel(xlsx_path, sheet_name=sheet, header=None).iloc[r, c]
    return v

def to_label(v):
    try:
        x = pd.to_numeric(pd.Series([v]), errors="coerce").iloc[0]
        return v if pd.notna(x) and x <= 1000 else "Infeasible"
    except Exception:
        return "Infeasible"

# —— 主循环 ——
for task in tasks:
    year = task["year"]
    # 兼容“100%”写法
    ed = str(task["ed"]).rstrip("%")

    # 1) 成本 CB：合并 City/Prov/State
    merged = None
    for lv, name in LEVELS.items():
        try:
            fp = file_path(lv, year, ed)
            df = pd.read_excel(fp, sheet_name="Eco_cost").iloc[:, :2]
            df.columns = ["Type", name]
            merged = df if merged is None else pd.merge(merged, df, on="Type", how="outer")
        except Exception as e:
            print(f"[Warn] Skip CB {name} for {year} ED{ed}: {e}")

    if merged is not None:
        cb_sheets[f"{year}_ED{ed}_CB"] = merged
        print(f"[Info] CB merged for {year} ED{ed} with cols: {list(merged.columns)}")
    else:
        print(f"[Error] No CB data for {year} ED{ed}")

    # 2) LCCE：分别读三层级 Decarbonization!B1
    rows = []
    for lv, name in LEVELS.items():
        try:
            fp = file_path(lv, year, ed)
            val = safe_read_cell(fp, "Decarbonization", 0, 1)
            rows.append({"Type": name, "Value": to_label(val)})
        except Exception as e:
            print(f"[Warn] Skip LCCE {name} for {year} ED{ed}: {e}")

    if rows:
        df_lcce = pd.DataFrame(rows, columns=["Type", "Value"])
        lcce_sheets[f"{year}_ED{ed}_LCCE"] = df_lcce
        print(f"[Info] LCCE for {year} ED{ed} processed.")
    else:
        print(f"[Error] No LCCE data for {year} ED{ed}")

# —————— 写入 Excel 文件 ——————
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet_name, df in cb_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    for sheet_name, df in lcce_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"[Success] All data saved to:\n{output_file}")
