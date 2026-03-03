import pandas as pd
import os

                        
         
                        
mode = "PEM"                 

if mode == "SOE":
    ED = 59
elif mode == "PEM":
    ED = 76
else:
    raise ValueError("Mode must be SOE or PEM")


                        
               
                        
base_dir = r"E:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\Excel"
file_path = os.path.join(base_dir, f"Hourly_{mode}_2050_ED{ED}.xlsx")


                        
               
                        
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

              
h_master = pd.DataFrame({"h": [f"h{i}" for i in range(1, 289)]})
h_master.set_index("h", inplace=True)


                        
                   
                        
for sheet in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)

    df = df.rename(columns={df.columns[0]: "h"})
    df.set_index("h", inplace=True)

    df = df.add_prefix(f"{sheet}_")
    h_master = h_master.join(df, how="left")

h_master = h_master.fillna(0)


                        
                    
                        
out_path = os.path.join(base_dir, f"Merged_{mode}_ED{ED}.xlsx")
h_master.to_excel(out_path)
print(f"Merged file saved: {out_path}")


                                                                        
                                                 
                                                                        

months = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

hours_per_month = 24

                                                  
df_all = h_master.reset_index().copy()

split_out_path = os.path.join(base_dir, f"Merged_{mode}_ED{ED}_SplitByMonth.xlsx")
writer = pd.ExcelWriter(split_out_path, engine="openpyxl")

for i, month in enumerate(months):

    start_h = i * hours_per_month + 1
    end_h   = (i + 1) * hours_per_month

    mask = df_all["h"].isin([f"h{j}" for j in range(start_h, end_h + 1)])
    df_month = df_all.loc[mask].copy()

    df_month.to_excel(writer, sheet_name=month, index=False)

writer.close()
print("Month-split file saved:", split_out_path)
