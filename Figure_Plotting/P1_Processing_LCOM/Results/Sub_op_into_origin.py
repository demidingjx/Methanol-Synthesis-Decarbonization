import pandas as pd
import os

                            
year = 2040
electrolyzer = "PEM"
ED_target = 25                                     
ED_source = 21                                          

               
base_path = r"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812"
source_file = os.path.join(base_path, electrolyzer, f"ED{ED_source}", f"LCOM_{electrolyzer}_ED{ED_source}.xlsx")
target_file = os.path.join(base_path, electrolyzer, f"ED{ED_target}", f"LCOM_{electrolyzer}_ED{ED_target}.xlsx")

                           
sheets_to_replace = [
    f"{year}_LCOM",
    f"{year}_Prov_LCOM_j",
    f"{year}_City_LCOM_j"
]

                    
original_sheets = pd.read_excel(target_file, sheet_name=None)                              
replacement_sheets = pd.read_excel(source_file, sheet_name=sheets_to_replace)                                        

                                    
for sheet in sheets_to_replace:
    original_sheets[sheet] = replacement_sheets[sheet]

                                   
with pd.ExcelWriter(target_file, engine='openpyxl', mode='w') as writer:
    for sheet_name, df in original_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Sheets {sheets_to_replace} have been replaced in ED{ED_target} using data from ED{ED_source}.")
