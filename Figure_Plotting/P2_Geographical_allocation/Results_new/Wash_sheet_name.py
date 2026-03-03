                       
import sys
import os
import pandas as pd

                   
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

                    


el = "PEM"         
runs = [
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
]

"""
el = "SOE"  # 电解器类型
runs = [
    {"year": "2040", "ed": "25"},
    {"year": "2040", "ed": "50"},
    {"year": "2040", "ed": "21"},
    {"year": "2040", "ed": "75"},
    {"year": "2040", "ed": "100"},
    {"year": "2050", "ed": "25"},
    {"year": "2050", "ed": "50"},
    {"year": "2050", "ed": "59"},
    {"year": "2050", "ed": "75"},
    {"year": "2050", "ed": "100"},
]
"""
def process_tns(el, year, ed):

                         
    base_dir  = rf"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new\{el}\{year}\ED{ed}"
    file_name = f"Nom_size_{el}_{year}_ED{ed}.xlsx"
    file_path = os.path.join(base_dir, file_name)

                          
    rename_map = {
        "Portion": "Prov",
        "GW_tech": "Prov",
    }

                
    all_sheets = pd.read_excel(file_path, sheet_name=None)

                     
    for sheet_name, new_col in rename_map.items():
        if sheet_name in all_sheets:
            df = all_sheets[sheet_name]
            old_first = df.columns[0]
            all_sheets[sheet_name] = df.rename(columns={old_first: new_col})
        else:
            print(f"警告：未找到 sheet “{sheet_name}”，已跳过。")

                     
    with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
        for sheet, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet, index=False)

    print(f"已在 {year}/ED{ed} 下的文件中完成首列重命名。")
if __name__ == "__main__":
    for cfg in runs:
        process_tns(el, cfg["year"], cfg["ed"])