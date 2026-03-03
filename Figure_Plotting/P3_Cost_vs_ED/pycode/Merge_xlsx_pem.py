import pandas as pd
import os

# —————— 用户自定义 ——————
electrolyzer_type = "PEM"  # 可设置为 "SOE" 或 "PEM"

# 通用 ED levels 列表（需确保每个都是独立字符串）
ed_levels = ["25%", "50%", "55%", "75%", "76%", "100%"]

# 各年份实际使用的 ED levels
year_ed_levels = {
    "2030": ["25%", "50%", "75%", "100%"],
    "2040": ["25%", "55%", "75%", "100%"],
    "2050": ["25%", "50%", "76%", "100%"],
}

# 输入/输出路径
base_root = fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\Results_new\{electrolyzer_type}"
output_file = fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\pycode\{electrolyzer_type}\bar_allyears\merged_CB_UE_NEW.xlsx"

# —————— 初始化存储变量 ——————
output_sheets = {}     # 每年的Eco_cost合并表
lcce_sheets = {}       # 每年的LCCE（EI-VALUE）

# —————— 主循环 ——————
for year, ed_list in year_ed_levels.items():
    year_dir = os.path.join(base_root, year)
    
    # 合并 Eco_cost 数据
    merged_df = None
    for ed in ed_list:
        ed_clean = ed.replace("%", "")
        file_name = f"TCB_UE_CAP_S_{electrolyzer_type}_{year}_ED{ed_clean}.xlsx"
        file_path = os.path.join(year_dir, file_name)

        if not os.path.exists(file_path):
            print(f"[Warning] Missing: {file_path}")
            continue

        df = pd.read_excel(file_path, sheet_name="Eco_cost").iloc[:, :2]
        df.columns = ["Type", ed]
        merged_df = df if merged_df is None else pd.merge(merged_df, df, on="Type", how="outer")

    # 补充 BAU
    bau_file = f"BAU_{electrolyzer_type}_{year}.xlsx"
    bau_path = os.path.join(year_dir, bau_file)
    if os.path.exists(bau_path):
        try:
            df_bau = pd.read_excel(bau_path, sheet_name="Eco_cost_BAU").iloc[:, :2]
            df_bau.columns = ["Type", "BAU"]
            merged_df = df_bau if merged_df is None else pd.merge(merged_df, df_bau, on="Type", how="outer")
        except Exception as e:
            print(f"[Error] Reading BAU: {e}")

    if merged_df is not None:
        merged_df.fillna(0, inplace=True)
        output_sheets[f"{year}_CB"] = merged_df
        print(f"[Info] Merged Eco_cost for {year}.")

    # 生成 LCCE 表（EI, VALUE）
    lcce_data = {"EI": [], "VALUE": []}
    for ed in ed_list:
        ed_clean = ed.replace("%", "")
        file_name = f"TCB_UE_CAP_S_{electrolyzer_type}_{year}_ED{ed_clean}.xlsx"
        file_path = os.path.join(year_dir, file_name)

        if os.path.exists(file_path):
            try:
                value = pd.read_excel(file_path, sheet_name="Decarbonization", header=None).iloc[0, 1]
                lcce_data["EI"].append(int(ed_clean))
                lcce_data["VALUE"].append(value)
                print(f"[Info] LCCE from {file_name}: {value}")
            except Exception as e:
                print(f"[Error] Reading LCCE from {file_name}: {e}")

    if lcce_data["EI"]:
        lcce_df = pd.DataFrame(lcce_data)
        lcce_sheets[f"{year}_LCCE"] = lcce_df

# —————— 写入 Excel ——————
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet_name, df in output_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    for sheet_name, df in lcce_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Finished! Data saved to:\n{output_file}")
