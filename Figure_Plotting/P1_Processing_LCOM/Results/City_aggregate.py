import pandas as pd
import numpy as np
from pathlib import Path

                                  
tech = "PEM"                             

                            
root = Path(fr"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812\{tech}")

                             
output_file = root / f"Collected_LCOM_results_{tech}.xlsx"
writer = pd.ExcelWriter(output_file, engine="openpyxl")

                                
for ed_folder in root.iterdir():
    if ed_folder.is_dir() and ed_folder.name.startswith("ED"):

        pattern = f"LCOM_city_*_{tech}_ED*.xlsx"

        for file in ed_folder.glob(pattern):

            name_parts = file.stem.split("_")                                                 
            sheet_name = "_".join(name_parts[2:])                   

            try:
                df = pd.read_excel(file, sheet_name="City_LCOM_j")
            except:
                print(f"Missing sheet in: {file.name}")
                continue

            df = df.iloc[:, :3]
            df.columns = ["Prov", "City", "Value"]

            df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

            filtered = df[df["Value"] > 0.1].copy()

            if filtered.empty:
                continue

            filtered.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()
print("Completed. Saved to:", output_file)
