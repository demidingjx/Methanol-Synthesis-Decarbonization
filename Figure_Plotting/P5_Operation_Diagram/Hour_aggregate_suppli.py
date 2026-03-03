import pandas as pd
import os

cases = [
         
    {"mode": "PEM", "year": 2040, "EI": "25%",  "ED": 25},
    {"mode": "PEM", "year": 2040, "EI": "100%", "ED": 100},
    {"mode": "PEM", "year": 2050, "EI": "25%",  "ED": 25},
    {"mode": "PEM", "year": 2050, "EI": "100%", "ED": 100},

         
    {"mode": "SOE", "year": 2040, "EI": "25%",  "ED": 25},
    {"mode": "SOE", "year": 2040, "EI": "100%", "ED": 100},
    {"mode": "SOE", "year": 2050, "EI": "25%",  "ED": 25},
    {"mode": "SOE", "year": 2050, "EI": "100%", "ED": 100},
]



for case in cases:

    mode = case["mode"]
    year = case["year"]
    EI   = case["EI"]
    ED   = case["ED"]

                            
             
                            
    base_dir = r"E:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\Excel"
    file_path = os.path.join(
        base_dir,
        f"Hourly_{mode}_{year}_ED{ED}.xlsx"
    )

    if not os.path.exists(file_path):
        print(f"Skip (file not found): {file_path}")
        continue


                            
                   
                            
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


                            
                        
                            
    out_path = os.path.join(
        base_dir,
        f"Merged_{mode}_{year}_ED{ED}.xlsx"
    )
    h_master.to_excel(out_path)
    print(f"Merged file saved: {out_path}")



                                                                            
                                                     
                                                                            

    months = ["Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"]

    hours_per_month = 24

                                                      
    df_all = h_master.reset_index().copy()

    split_out_path = os.path.join(
    base_dir,
    f"SplitByMonth{mode}_{year}_ED{ED}.xlsx"
    )

    writer = pd.ExcelWriter(split_out_path, engine="openpyxl")

    for i, month in enumerate(months):

        start_h = i * hours_per_month + 1
        end_h   = (i + 1) * hours_per_month

        mask = df_all["h"].isin([f"h{j}" for j in range(start_h, end_h + 1)])
        df_month = df_all.loc[mask].copy()

        df_month.to_excel(writer, sheet_name=month, index=False)

    writer.close()
    print("Month-split file saved:", split_out_path)
