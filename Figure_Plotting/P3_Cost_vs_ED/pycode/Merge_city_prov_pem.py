import pandas as pd
import os

# —————— 用户统一配置 ——————
el = "PEM"  # 可设置为 "PEM" 或 "SOE"


# 年份-ED 组合：2030/2040/2050 × {25, 100}

#--------------------------Maniscript 用这个--------------------------

base_dir = fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED"
output_file = fr"{base_dir}\pycode\{el}\bar_allyears\merged_CB_CityProv.xlsx"
#PEM

years_eds = {
    "2040": ["55%"],
    "2050": ["76%"],  # 若上游写成"100%"也能兼容,见下方rstrip('%')
}
'''
#SOE
years_eds = {
    "2040": ["21%"],
    "2050": ["59%"],  # 若上游写成"100%"也能兼容见下方rstrip('%')
}

'''
#--------------------------Supplementary 用这个--------------------------

base_dir = fr"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED"
output_file = fr"{base_dir}\pycode\{el}\bar_allyears\Supplementary_CityProv.xlsx"
'''

#PEM
years_eds = {
    "2030": ["25", "100"],
    "2040": ["25", "100"],
    "2050": ["25", "100"],  # 若上游写成"100%"也能兼容，见下方rstrip('%')
}
#SOE

years_eds = {
    "2030": ["25", "100"],
    "2040": ["25", "100"],
    "2050": ["25", "100"],  # 若上游写成"100%"也能兼容，见下方rstrip('%')
}
'''

tasks = [{"year": y, "ed": ed} for y, eds in years_eds.items() for ed in eds]

# —————— 初始化 ——————
cb_sheets = {}
lcce_sheets = {}

# —————— 主循环 ——————
for task in tasks:
    year = task["year"]
    # 兼容“100%”写法
    ed = str(task["ed"]).rstrip("%")

    file_P = fr"{base_dir}\Results_new\{el}\{year}\TCB_UE_CAP_P_{el}_{year}_ED{ed}.xlsx"
    file_C = fr"{base_dir}\Results_new\{el}\{year}\TCB_UE_CAP_C_{el}_{year}_ED{ed}.xlsx"

    # CB 合并处理
    try:
        df_city = pd.read_excel(file_C, sheet_name="Eco_cost").iloc[:, :2]
        df_prov = pd.read_excel(file_P, sheet_name="Eco_cost").iloc[:, :2]
        df_city.columns = ["Type", "City"]
        df_prov.columns = ["Type", "Prov"]
        df_merged = pd.merge(df_city, df_prov, on="Type", how="outer")

        cb_sheets[f"{year}_CB"] = df_merged
        print(f"[Info] CB data for {year} ED{ed} processed.")
    except Exception as e:
        print(f"[Error] processing CB for {year} ED{ed}: {e}")
    # LCCE 获取并判定可行性
    try:
        # 原始读取
        value_city = pd.read_excel(file_C, sheet_name="Decarbonization", header=None).iloc[0, 1]
        value_prov = pd.read_excel(file_P, sheet_name="Decarbonization", header=None).iloc[0, 1]

        city_label = value_city if pd.to_numeric(pd.Series([value_city]), errors="coerce").iloc[0] <= 1000 else "Infeasible"
        prov_label = value_prov if pd.to_numeric(pd.Series([value_prov]), errors="coerce").iloc[0] <= 1000 else "Infeasible"

        df_lcce = pd.DataFrame({
            "Type": ["City", "Prov"],
            "Value": [city_label, prov_label]
        })
        lcce_sheets[f"{year}_LCCE"] = df_lcce
        print(f"[Info] LCCE data for {year} ED{ed} processed. (City: {city_label}, Prov: {prov_label})")
    except Exception as e:
        print(f"[Error] processing LCCE for {year} ED{ed}: {e}")
# —————— 写入 Excel 文件 ——————
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet_name, df in cb_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    for sheet_name, df in lcce_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"[Success] All data saved to:\n{output_file}")
