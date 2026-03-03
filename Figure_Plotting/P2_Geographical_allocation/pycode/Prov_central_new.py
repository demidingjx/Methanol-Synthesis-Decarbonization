                       
import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from shapely.geometry import LineString
from shapely.ops import split, unary_union

                      
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50)
pd.set_option('display.width', 0)
pd.set_option('display.float_format', '{:.6f}'.format)

                                                   
if os.name == 'nt':
    os.system('chcp 65001 >nul')
sys.stdout.reconfigure(encoding='utf-8')

                  
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

                              
shp = r"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\pycode\CN_Map\CN_Province.shp"

                     
sz = gpd.read_file(shp, encoding='utf-8', engine='fiona')
print("底图 CRS =", sz.crs)

                                 
sz['centroid_x'] = sz.geometry.centroid.x
sz['centroid_y'] = sz.geometry.centroid.y

                                     
sz_wgs = sz.to_crs(epsg=4326)
sz['lon'] = sz_wgs.geometry.centroid.x
sz['lat'] = sz_wgs.geometry.centroid.y

                      
ch_en_map = {
    "北京市": "Beijing",         "天津市": "Tianjin",
    "上海市": "Shanghai",         "重庆市": "Chongqing",
    "河北省": "Hebei",            "山西省": "Shanxi",
    "内蒙古自治区": "Inner Mongolia","辽宁省": "Liaoning",
    "吉林省": "Jilin",            "黑龙江省": "Heilongjiang",
    "江苏省": "Jiangsu",          "浙江省": "Zhejiang",
    "安徽省": "Anhui",            "福建省": "Fujian",
    "江西省": "Jiangxi",          "山东省": "Shandong",
    "河南省": "Henan",            "湖北省": "Hubei",
    "湖南省": "Hunan",            "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",    "海南省": "Hainan",
    "四川省": "Sichuan",          "贵州省": "Guizhou",
    "云南省": "Yunnan",           "西藏自治区": "Tibet",
    "陕西省": "Shaanxi",          "甘肃省": "Gansu",
    "青海省": "Qinghai",          "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Sinkiang", "台湾省": "Taiwan",
    "香港特别行政区": "Hong Kong","澳门特别行政区": "Macau"
}
sz['province_en'] = sz['省'].map(ch_en_map).fillna(sz['省'])

                              
out_dir = os.path.dirname(shp)
sz.loc[:, ['province_en','省代码','lon','lat']].to_excel(
    os.path.join(out_dir, "province_centroids_en.xlsx"),
    index=False,
    header=['Province','Code','Longitude','Latitude']
)
print("省级经纬度质心已保存到 province_centroids_en.xlsx")

                          
im_geom = sz_wgs.loc[sz['province_en']=="Inner Mongolia", 'geometry'].iloc[0]
split_line = LineString([(111.5, -90), (111.5, 90)])
parts = list(split(im_geom, split_line).geoms)
west_parts = [g for g in parts if g.centroid.x <= 118.5]
east_parts = [g for g in parts if g.centroid.x >  118.5]
west_geom, east_geom = unary_union(west_parts), unary_union(east_parts)
west_cent, east_cent = west_geom.centroid, east_geom.centroid
print(f"西蒙古中心 (lon,lat)=({west_cent.x:.4f},{west_cent.y:.4f})")
print(f"东蒙古中心 (lon,lat)=({east_cent.x:.4f},{east_cent.y:.4f})")

                             
pd.DataFrame([
    ["West Mongolia", west_cent.x, west_cent.y],
    ["East Mongolia", east_cent.x, east_cent.y]
], columns=["Province","Longitude","Latitude"])\
  .to_excel(os.path.join(out_dir, "inner_mongolia_centroids_en.xlsx"),
            index=False)
print("内蒙古东西部经纬度质心已保存到 inner_mongolia_centroids_en.xlsx")

                                 
                  
g_im_cent = gpd.GeoSeries([west_cent, east_cent], crs="EPSG:4326")
g_im_cent_proj = g_im_cent.to_crs(sz.crs)
west_proj, east_proj = g_im_cent_proj.iloc[0], g_im_cent_proj.iloc[1]

      
fig, ax = plt.subplots(figsize=(12,10))
sz.plot(ax=ax, edgecolor='gray', linewidth=0.5, facecolor='#66c2a5')

        
ax.scatter(sz['centroid_x'], sz['centroid_y'],
           color='red', s=20, marker='o',
           label='Province Centroid', zorder=3)

               
ax.scatter([west_proj.x, east_proj.x],
           [west_proj.y, east_proj.y],
           color='blue', s=80, marker='*',
           label='Inner Mongolia East/West Centroid', zorder=4)

            
for _, row in sz.iterrows():
    ax.text(row['centroid_x'], row['centroid_y'],
            row['province_en'],
            fontsize=6, ha='center', va='center', zorder=5)

ax.set_title("中国省级行政区划及各省质心", fontsize=16)
ax.set_xticks([]); ax.set_yticks([])
ax.legend(loc='lower left', fontsize=10)
plt.tight_layout()
plt.show()
