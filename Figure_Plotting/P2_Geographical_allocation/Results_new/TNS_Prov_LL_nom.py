import pandas as pd
from pathlib import Path

            
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
    {"year": "2040", "ed": "21"},
    {"year": "2040", "ed": "50"},
    {"year": "2040", "ed": "25"},
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
            
    tns_file = fr"{base_results}\{el}\{year}\ED{ed}\TNS_nom_{el}_{year}_ED{ed}.xlsx"
    city_coords_file = fr"{base_pycode}\City_coordinates.xlsx"
    prov_coords_file = fr"{base_pycode}\Prov_coordinates_centre.xlsx"

    output_file = (
        Path(base_results) 
        / el 
        / year 
        / f"ED{ed}" 
        / f"TNS_nom_{el}_{year}_ED{ed}_2s.xlsx"
    )
                                                      
    def normalize_cols(df):
        df.columns = df.columns.str.strip()
        for alt in ['Prov_i', 'Prov_j', 'Pron']:
            if alt in df.columns and 'Prov' not in df.columns:
                df.rename(columns={alt: 'Prov'}, inplace=True)
        return df

                                       
    tns_xls = pd.ExcelFile(tns_file)
    dfs = {sheet: normalize_cols(tns_xls.parse(sheet)) for sheet in tns_xls.sheet_names}
    
                                       
    df_city = normalize_cols(pd.read_excel(city_coords_file))

    city_ix_df = df_city.rename(columns={'City': 'City_ix', 'Lons2': 'Longitude_1', 'Lats2': 'Latitude_1'})[['Prov', 'City_ix', 'Longitude_1', 'Latitude_1']]
    city_i_df  = df_city.rename(columns={'City': 'City_i',  'Lons2': 'Longitude_2', 'Lats2': 'Latitude_2'})[['Prov', 'City_i', 'Longitude_2', 'Latitude_2']]

                                           
    df_prov = normalize_cols(pd.read_excel(prov_coords_file))
    prov_df = df_prov.rename(columns={'Longitude': 'Longitude_2', 'Latitude': 'Latitude_2'})[['Prov', 'Longitude_2', 'Latitude_2']]

                         
    city_sheets = ['U_PV_city', 'U_WT_city']
    exp_sheets  = ['U_PV_exp', 'U_WT_exp', 'U_imp']
    prov_sheet  = 'U_prov'

                     
    def merge_city_sheet(df):
        df = normalize_cols(df)
        df = pd.merge(df, city_ix_df, on=['Prov', 'City_ix'], how='left')
        df = pd.merge(df, city_i_df, on=['Prov', 'City_i'], how='left')
        return df

    def merge_exp_imp_sheet(df):
        df = normalize_cols(df)
        if 'City' in df.columns:
            df.rename(columns={'City': 'City_ix'}, inplace=True)
        df = pd.merge(df, city_ix_df, on=['Prov', 'City_ix'], how='left')
        df.rename(columns={'City_ix': 'City'}, inplace=True)
        df = pd.merge(df, prov_df, on='Prov', how='left')
        return df

    def merge_prov_sheet(df):
        df = normalize_cols(df)
        cols = df.columns.tolist()
        colB, colC = cols[1], cols[2]
        df.rename(columns={colB: 'Prov1', colC: 'Prov2'}, inplace=True)
        p1 = prov_df.rename(columns={'Prov': 'Prov1', 'Longitude_2': 'Longitude_1', 'Latitude_2': 'Latitude_1'})
        df = pd.merge(df, p1, on='Prov1', how='left')
        p2 = prov_df.rename(columns={'Prov': 'Prov2'})
        df = pd.merge(df, p2, on='Prov2', how='left')
        df.rename(columns={'Prov1': colB, 'Prov2': colC}, inplace=True)
        return df

                  
    for sh in city_sheets:
        if sh in dfs:
            dfs[sh] = merge_city_sheet(dfs[sh])
    for sh in exp_sheets:
        if sh in dfs:
            dfs[sh] = merge_exp_imp_sheet(dfs[sh])
    if prov_sheet in dfs:
        dfs[prov_sheet] = merge_prov_sheet(dfs[prov_sheet])

                                                        
    df_uprov = dfs.get(prov_sheet, pd.DataFrame())

    matrix_ac = (
        df_uprov[df_uprov['Type'].str.upper() == 'AC']
        .pivot(index='Prov_jx', columns='Prov', values='Value')
        .fillna(0)
    )

    matrix_dc = (
        df_uprov[df_uprov['Type'].str.upper() == 'DC']
        .pivot(index='Prov_jx', columns='Prov', values='Value')
        .fillna(0)
    )
                                                    
    for matrix in [matrix_ac, matrix_dc]:
        matrix.index = matrix.index.str.replace('W_InnerMongo', 'West Inner Mongolia')
        matrix.index = matrix.index.str.replace('E_InnerMongo', 'East Inner Mongolia')
        matrix.columns = matrix.columns.str.replace('W_InnerMongo', 'West Inner Mongolia')
        matrix.columns = matrix.columns.str.replace('E_InnerMongo', 'East Inner Mongolia')

                                              
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)
                        
        sheet_ac = f"matr_AC"
        matrix_ac.to_excel(writer, sheet_name=sheet_ac, index=True)
                        
        sheet_dc = f"matr_DC"
        matrix_dc.to_excel(writer, sheet_name=sheet_dc, index=True)

    sheet_ac = f"matr_AC"
    sheet_dc = f"matr_DC"

    print(f"Workbook saved with AC & DC matrix sheets: {output_file}")

if __name__ == "__main__":
    for cfg in runs:
        process_tns(el, cfg["year"], cfg["ed"])