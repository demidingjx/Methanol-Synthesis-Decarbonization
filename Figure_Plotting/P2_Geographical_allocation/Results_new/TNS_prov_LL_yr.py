import pandas as pd
from pathlib import Path

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
"""


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

            
    tns_file = fr"{base_results}\{el}\{year}\ED{ed}\TNS_yr_{el}_{year}_ED{ed}.xlsx"
    city_coords_file = fr"{base_pycode}\City_coordinates.xlsx"
    prov_coords_file = fr"{base_pycode}\Prov_coordinates_centre.xlsx"

    output_file = (
        Path(base_results) 
        / el 
        / year 
        / f"ED{ed}" 
        / f"TNS_yr_{el}_{year}_ED{ed}_2s.xlsx"
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
    df_city_i_src = normalize_cols(pd.read_excel(city_coords_file, sheet_name=0))

    city_ix_df = df_city.rename(columns={'City': 'City_ix', 'Lons2': 'Longitude_1', 'Lats2': 'Latitude_1'})[['Prov', 'City_ix', 'Longitude_1', 'Latitude_1']]
    city_i_df  = df_city_i_src.rename(columns={'City': 'City_i',  'Lons2': 'Longitude_2', 'Lats2': 'Latitude_2'})[['Prov', 'City_i', 'Longitude_2', 'Latitude_2']]

                                           
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

    rid_regions = {
        'NE': ['Liaoning', 'Jilin', 'Heilongjiang', 'E_InnerMongo'],
        'NC': ['Shandong', 'Shanxi', 'Hebei', 'Tianjin', 'Beijing', 'W_InnerMongo'],
        'EC': ['Shanghai', 'Jiangsu', 'Zhejiang', 'Anhui', 'Fujian'],
        'HC': ['Hunan', 'Hubei', 'Jiangxi', 'Henan'],
        'SW': ['Sichuan', 'Chongqing', 'Tibet'],
        'NW': ['Shaanxi', 'Gansu', 'Ningxia', 'Qinghai', 'Sinkiang'],
        'SC': ['Guangdong', 'Guangxi', 'Hainan', 'Yunnan', 'Guizhou']
    }

    prov2reg = {prov: r for r, lst in rid_regions.items() for prov in lst}
    df_region = df_uprov[['Type','Prov_jx','Prov','Value']].copy()
    df_region['Region_jx'] = df_region['Prov_jx'].map(prov2reg).fillna('Unknown')
    df_region['Region']    = df_region['Prov'].map(prov2reg).fillna('Unknown')



    matrix_ac = ((
        df_uprov[df_uprov['Type'].str.upper() == 'AC']
        .pivot(index='Prov_jx', columns='Prov', values='Value')
        .fillna(0)
        )
        .div(1000)                
    )

    matrix_dc = ((
        df_uprov[df_uprov['Type'].str.upper() == 'DC']
        .pivot(index='Prov_jx', columns='Prov', values='Value')
        .fillna(0)
        )
        .div(1000)                
    )

    matrix_ac.rename(index=province_abbr, columns=province_abbr, inplace=True)
    matrix_dc.rename(index=province_abbr, columns=province_abbr, inplace=True)

    for m in (matrix_ac, matrix_dc):
        m.rename(index=province_abbr, columns=province_abbr, inplace=True)

                                          
                                                   
    matrix_region = (
        df_region
        .pivot_table(
            index='Region_jx',
            columns='Region',
            values='Value',
            aggfunc='sum',
            fill_value=0
        )
        .div(1000)                
    )


                                                    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                   
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)
                       
        df_region.to_excel(writer, sheet_name='U_prov_region', index=False)
                   
        matrix_region.to_excel(writer, sheet_name='matr_Region', index=True)
                  
        matrix_ac.to_excel(writer, sheet_name=f"matr_AC", index=True)
        matrix_dc.to_excel(writer, sheet_name=f"matr_DC", index=True)

                                                                            
                                                                             
                                                                            
                                                                      
    if 'U_PV_city' in dfs:
        df_pv_sum = (
            dfs['U_PV_city']
            .groupby('Prov')['Value']
            .sum()
            .reset_index(name='Total_Value_PV')
        )
    else:
        df_pv_sum = pd.DataFrame(columns=['Prov', 'Total_Value_PV'])

    if 'U_WT_city' in dfs:
        df_wt_sum = (
            dfs['U_WT_city']
            .groupby('Prov')['Value']
            .sum()
            .reset_index(name='Total_Value_WT')
        )
    else:
        df_wt_sum = pd.DataFrame(columns=['Prov', 'Total_Value_WT'])

                                                
                                                                         

    df_combined = (
        pd.merge(
            df_pv_sum,
            df_wt_sum,
            on='Prov',
            how='outer'
        )
        .fillna(0)
    )
    df_combined['Total_Value'] = df_combined['Total_Value_PV'] + df_combined['Total_Value_WT']
                                        

    df_combined = df_combined.sort_values(by='Total_Value', ascending=False).reset_index(drop=True)

                                         
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                         
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)

                                                     
        if not df_pv_sum.empty:
            df_pv_sum.to_excel(writer, sheet_name='U_PV_city_Prov_Sum', index=False)
        if not df_wt_sum.empty:
            df_wt_sum.to_excel(writer, sheet_name='U_WT_city_Prov_Sum', index=False)

                                         
        df_combined.to_excel(writer, sheet_name='U_city_Prov_Sum_Total', index=False)

                                         
        df_region.to_excel(writer, sheet_name='U_prov_region', index=False)
        matrix_region.to_excel(writer, sheet_name='matr_Region', index=True)

                        
        matrix_ac.to_excel(writer, sheet_name=f"matr_AC", index=True)
        matrix_dc.to_excel(writer, sheet_name=f"matr_DC", index=True)

    print(f"Workbook saved with province summaries, combined sorted totals, U_prov_region, region matrix, AC & DC matrix sheets: {output_file}")
if __name__ == "__main__":
    for cfg in runs:
        process_tns(el, cfg["year"], cfg["ed"])