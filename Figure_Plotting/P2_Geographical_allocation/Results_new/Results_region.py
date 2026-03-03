import pandas as pd
import os

                                     
            
"""
el = "PEM"  # 电解器类型
st = "HST"
runs = [
    {"year": "2040", "ed": "ED25"},
    {"year": "2040", "ed": "ED50"},
    {"year": "2040", "ed": "ED55"},
    {"year": "2040", "ed": "ED75"},
    {"year": "2040", "ed": "ED100"},
    {"year": "2050", "ed": "ED25"},
    {"year": "2050", "ed": "ED50"},
    {"year": "2050", "ed": "ED76"},
    {"year": "2050", "ed": "ED75"},
    {"year": "2050", "ed": "ED100"},
]

"""
el = "SOE"         
st = "SST"
runs = [
    {"year": "2040", "ed": "ED21"},
    {"year": "2040", "ed": "ED50"},
    {"year": "2040", "ed": "ED75"},
    {"year": "2040", "ed": "ED100"},
    {"year": "2050", "ed": "ED25"},
    {"year": "2050", "ed": "ED50"},
    {"year": "2050", "ed": "ED59"},
    {"year": "2050", "ed": "ED75"},
    {"year": "2050", "ed": "ED100"},
]


base_dir  = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new"
def process_tns(el, year, ed):

                                                  
    tech_columns = ["PV", "WT", el, st]

                               
    rid_regions = {
        "NE": ["Liaoning", "Jilin", "Heilongjiang", "E_InnerMongo"],
        "NC": ["Shandong", "Shanxi", "Hebei", "Tianjin", "Beijing", "W_InnerMongo"],
        "EC": ["Shanghai", "Jiangsu", "Zhejiang", "Anhui", "Fujian"],
        "HC": ["Hunan", "Hubei", "Jiangxi", "Henan"],
        "SW": ["Sichuan", "Chongqing", "Tibet"],
        "NW": ["Shaanxi", "Gansu", "Ningxia", "Qinghai", "Sinkiang"],
        "SC": ["Guangdong", "Guangxi", "Hainan", "Yunnan", "Guizhou"]
    }

                                
    nom_input   = os.path.join(base_dir, el, year, ed, f"Nom_size_{el}_{year}_{ed}_2.xlsx")
    csv_meoh    = r"E:\2025_Methanol_synthesis\3_GAMS\csv_Single_Prov\MeOH_Caps.csv"
    output_file = os.path.join(base_dir, el, year, ed, f"Aggregated_size_{el}_{year}_{ed}_2.xlsx")

                             
    sheets = pd.read_excel(nom_input, sheet_name=["Total_size", "GW_tech"])
    df_size = sheets["Total_size"]
    df_gw   = sheets["GW_tech"]

                           
    df_meoh = pd.read_csv(csv_meoh)                        

                                         
    prov_to_region = {
        prov: region
        for region, provs in rid_regions.items()
        for prov in provs
    }

                                                
    df_size["Region"] = df_size["Prov"].map(prov_to_region)
    agg_size = df_size.groupby("Region", as_index=False)["Total_size"].sum()
    national_total = agg_size["Total_size"].sum()
    agg_size["Share_%"] = agg_size["Total_size"] / national_total * 100

                                    
    df_gw["Region"] = df_gw["Prov"].map(prov_to_region)
    agg_gw = df_gw.groupby("Region", as_index=False)[tech_columns].sum()

                                       
    portion = agg_gw.copy()
    for col in tech_columns:
        portion[col] = portion[col] / portion[col].sum() * 100

                                      
    df_meoh["Region"] = df_meoh["j"].map(prov_to_region)
    agg_meoh = df_meoh.groupby("Region", as_index=False)["Caps"].sum().rename(columns={"Caps": "MeOH_cap"})
    total_meoh = agg_meoh["MeOH_cap"].sum()
    agg_meoh["Share_%"] = agg_meoh["MeOH_cap"] / total_meoh * 100

                                       
    with pd.ExcelWriter(output_file, engine="openpyxl", mode="w") as writer:
        agg_size.to_excel(writer, sheet_name="Total_size_by_region", index=False)
        agg_gw.to_excel(writer,   sheet_name="GW_tech_by_region",   index=False)
        portion.to_excel(writer,  sheet_name="Portion_by_region",    index=False)
        agg_meoh.to_excel(writer, sheet_name="MeOH_cap_by_region",   index=False)

    print("Inputs:")
    print("  - Nom_size:", nom_input)
    print("  - MeOH_CSV:", csv_meoh)
    print("Output Excel:", output_file)
    print("All aggregations and share calculations completed.")
if __name__ == "__main__":
    for cfg in runs:
        process_tns(el, cfg["year"], cfg["ed"])