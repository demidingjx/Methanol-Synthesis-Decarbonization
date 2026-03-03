import pandas as pd

            

"""
el = "PEM"  # 电解器类型
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
el = "SOE"         
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


province_abbr = {
    "Anhui": "AH", "Gansu": "GS", "Guangxi": "GX", "Guizhou": "GZ",
    "Hainan": "HI", "Hebei": "HB", "Henan": "HN", "Heilongjiang": "HL",
    "Hubei": "HU", "Jilin": "JL", "Jiangsu": "JS", "Jiangxi": "JX",
    "Liaoning": "LN", "E_InnerMongo": "EIM", "W_InnerMongo": "WIM",
    "Ningxia": "NX", "Qinghai": "QH", "Shandong": "SD", "Shanxi": "SN",
    "Shaanxi": "SX", "Shanghai": "SH", "Sichuan": "SC", "Tianjin": "TJ",
    "Sinkiang": "XJ", "Yunnan": "YN", "Zhejiang": "ZJ", "Chongqing": "CQ"
}

      
base_results = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new"
base_pycode = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode"
def process_tns(el, year, ed):
            
    nom_file = fr"{base_results}\{el}\{year}\ED{ed}\Nom_size_{el}_{year}_ED{ed}.xlsx"
    coords_file = fr"{base_pycode}\Prov_coordinates.xlsx"
    output_file = fr"{base_results}\{el}\{year}\ED{ed}\Nom_size_{el}_{year}_ED{ed}_2.xlsx"

                                 
    txls = pd.ExcelFile(nom_file)
    dfs = {sheet: txls.parse(sheet) for sheet in txls.sheet_names}

              
    df_coords = pd.read_excel(coords_file)

                              
    if 'Total_size' not in dfs:
        raise KeyError("未找到 'Total_size' 表，请确认工作簿中存在该 sheet 名称")
    df_total = dfs['Total_size']
    df_total_merged = pd.merge(
        df_total,
        df_coords[['Prov', 'Longitude', 'Latitude']],
        on='Prov',
        how='left'
    )
                         
    missing_total = df_total_merged['Longitude'].isnull() | df_total_merged['Latitude'].isnull()
    if missing_total.any():
        print("警告：Total_size 表中以下 Prov 在坐标表中未找到对应项：", df_total_merged.loc[missing_total, 'Prov'].unique())

    dfs['Total_size'] = df_total_merged

                                     
    if 'Portion' not in dfs:
        raise KeyError("未找到 'Portion' 表，请确认工作簿中存在该 sheet 名称")
    df_portion = dfs['Portion']
                                     
    cols_to_add = [c for c in df_total_merged.columns if c != 'Prov']
                               
    df_portion_merged = pd.merge(
        df_portion,
        df_total_merged[['Prov'] + cols_to_add],
        on='Prov',
        how='left'
    )
    df_portion_merged = df_portion_merged.replace("Undf", 0).fillna(0)

                      
    missing_portion = df_portion_merged[cols_to_add].isnull().any(axis=1)
    if missing_portion.any():
        print("警告：Portion 表中以下 Prov 在 Total_size 表中未找到对应项：", df_portion_merged.loc[missing_portion, 'Prov'].unique())

    dfs['Portion'] = df_portion_merged

                                 
                    
    ed_prov_sheet = 'ED_prov'
    if ed_prov_sheet in dfs:
        df_edprov = dfs[ed_prov_sheet].copy()
        df_edprov['Prov'] = df_edprov['Prov'].map(province_abbr).fillna(df_edprov['Prov'])
        ed_prov_abbr_df = df_edprov
    else:
        ed_prov_abbr_df = pd.DataFrame()

                          
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)

                                
        if not ed_prov_abbr_df.empty:
            ed_prov_abbr_df.to_excel(writer, sheet_name='ED_prov_abbr', index=False)

    print(f"已保存带经纬度并合并Total_size字段的文件到: {output_file}")
if __name__ == "__main__":
    for cfg in runs:
        process_tns(el, cfg["year"], cfg["ed"])