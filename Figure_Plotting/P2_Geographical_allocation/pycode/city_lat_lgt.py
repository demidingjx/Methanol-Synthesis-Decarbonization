import pandas as pd
import os

      
coord_path = r"F:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\City_coordinates.xlsx"
file_paths = [
    r"F:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\Cities_w_MeOH.csv",
    r"F:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\Cities_wo_MeOH.csv",
]

       
coords = pd.read_excel(coord_path, sheet_name='Sheet1')
coords = coords.rename(columns={
    'Pron': 'Province',
    'City': 'City',
    'Lons2': 'Longitude',
    'Lats2': 'Latitude'
})

                           
coords_city = coords.drop_duplicates(subset=['City'])[['City', 'Longitude', 'Latitude']]

           
for path in file_paths:
               
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(path)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(path)
    else:
        print(f"不支持的文件格式: {ext}")
        continue

                            
    if 'Province' in df.columns:
        merge_keys = ['Province', 'City']
        to_merge = coords[['Province', 'City', 'Longitude', 'Latitude']]
    else:
        merge_keys = ['City']
        to_merge = coords_city

          
    merged = df.merge(to_merge, on=merge_keys, how='left')

            
    missing = merged[merged['Longitude'].isna()]
    if not missing.empty:
        print(f"在文件 {os.path.basename(path)} 中，以下城市没有找到坐标：")
        print(missing[merge_keys].drop_duplicates())

           
    out_path = os.path.splitext(path)[0] + '_with_coords' + ext
    if ext == '.csv':
        merged.to_csv(out_path, index=False)
    else:
        merged.to_excel(out_path, index=False)
    print(f"已保存带坐标的文件: {out_path}")