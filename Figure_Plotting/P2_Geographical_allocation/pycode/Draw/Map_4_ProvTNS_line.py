                       
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib as mpl
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import LineString, Point, box
from shapely.ops import split, unary_union
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import Wedge, Patch, Circle
from matplotlib.colors import Normalize
from matplotlib import cm
from matplotlib.cm import ScalarMappable
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import Normalize, LinearSegmentedColormap
import matplotlib as mpl
mpl.rcParams['mathtext.default'] = 'regular'

         
ch_en_map = {
    "北京市": "Beijing", "天津市": "Tianjin", "上海市": "Shanghai", "重庆市": "Chongqing",
    "河北省": "Hebei", "山西省": "Shanxi", "内蒙古自治区": "Inner Mongolia", "辽宁省": "Liaoning",
    "吉林省": "Jilin", "黑龙江省": "Heilongjiang", "江苏省": "Jiangsu", "浙江省": "Zhejiang",
    "安徽省": "Anhui", "福建省": "Fujian", "江西省": "Jiangxi", "山东省": "Shandong",
    "河南省": "Henan", "湖北省": "Hubei", "湖南省": "Hunan", "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi", "海南省": "Hainan", "四川省": "Sichuan", "贵州省": "Guizhou",
    "云南省": "Yunnan", "西藏自治区": "Tibet", "陕西省": "Shaanxi", "甘肃省": "Gansu",
    "青海省": "Qinghai", "宁夏回族自治区": "Ningxia", "新疆维吾尔自治区": "Sinkiang",
    "台湾省": "Taiwan", "香港特别行政区": "Hong Kong", "澳门特别行政区": "Macau"
}

                                                                                                    
if os.name == 'nt':
    os.system('chcp 65001 >nul')
sys.stdout.reconfigure(encoding='utf-8')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

                 
prov_shp = r"D:\2025_Methanol_synthesis\GAMS\P3_Geographical_allocation\pycode\CN_Map\CN_Province.shp"
city_shp = r"D:\2025_Methanol_synthesis\GAMS\P3_Geographical_allocation\pycode\CN_Map_WGS1984\CN_Prefecture.shp"
nine_shp = r"D:\2025_Methanol_synthesis\GAMS\P3_Geographical_allocation\pycode\CN_Map\Jiu_Duan_Xian.shp"

out_dir = r"D:\2025_Methanol_synthesis\GAMS\P3_Geographical_allocation\fig"
os.makedirs(out_dir, exist_ok=True)
                                                                            
prov = gpd.read_file(prov_shp, engine='fiona', encoding='utf-8')
nine = gpd.read_file(nine_shp, engine='fiona', encoding='utf-8')

                 
prov_geo = prov.to_crs(epsg=4326)

                          
prov_2343 = prov.to_crs(epsg=2343)
nine_2343 = nine.to_crs(epsg=2343)

                                                                                   
fig, ax = plt.subplots(figsize=(12,9), constrained_layout=True)
albers_proj = 'EPSG:2343'
             
prov_2343.plot(ax=ax, facecolor="lightgrey", edgecolor='white', linewidth=0.5, zorder=1)
                                                               
ax.set_axis_off()
                        
             
bbox_geo = box(106.5, 2.8, 123.0, 24.5)
       
bbox_2343 = gpd.GeoSeries([bbox_geo], crs=4326).to_crs(epsg=2343).iloc[0]
      
prov_crop = prov_2343[prov_2343.intersects(bbox_2343)]
nine_crop = nine_2343[nine_2343.intersects(bbox_2343)]
axins = inset_axes(ax, width='20%', height='20%', loc='lower right', bbox_to_anchor=(0.11, 0.27, 1.0, 1.0), bbox_transform=ax.transAxes, borderpad=0)
prov_crop.plot(ax=axins, facecolor='lightgrey', edgecolor='white', linewidth=0.5, zorder=1)
nine_crop.plot(ax=axins, color='gray', linewidth=1.5, linestyle='--', zorder=2)

             
minx, miny, maxx, maxy = bbox_2343.bounds
axins.set_xlim(minx, maxx)
axins.set_ylim(miny, maxy)
axins.set_xticks([])
axins.set_yticks([])

rect = Rectangle((0, 0), 1, 1, transform=axins.transAxes, fill=False, edgecolor='black', linewidth=1)
axins.add_patch(rect)

ax.axis('off')

                                                                                        

                                     
city = gpd.read_file(city_shp, encoding='utf-8').to_crs(epsg=2343)

                       
im_city = city[city['省']=="内蒙古自治区"].copy()

                  
east_list = ["赤峰市","通辽市","兴安盟","呼伦贝尔市"]

west_list = [c for c in im_city['市'].unique() if c not in east_list]

                                
im_city['region'] = im_city['市'].apply(
    lambda s: 'W_InnerMongo' if s in west_list
              else ('E_InnerMongo' if s in east_list else None)
)

im_west = (
    im_city[im_city['region']=="W_InnerMongo"]
    .dissolve(by='region')
    .reset_index()                   
)

im_east = (
    im_city[im_city['region']=="E_InnerMongo"]
    .dissolve(by='region')
    .reset_index()
)


                                                                            
prov_2343['province_cn'] = prov_2343['省']
def remove_small_islands(geom, min_area=5e9):
    """
    过滤掉面积小于 min_area 的小岛。
    geom: Polygon 或 MultiPolygon
    """
    if isinstance(geom, MultiPolygon):
        parts = [p for p in geom.geoms if p.area > min_area]
        if not parts:
            return geom
        return parts[0] if len(parts)==1 else MultiPolygon(parts)
         
    return geom if geom.area > min_area else geom

                       
grid_regions = {
    'NE': { 'province_cn': ["辽宁省","吉林省","黑龙江省"],
            'use_im_east': True,
            'style': dict(edgecolor="#155f8b", linewidth=2, linestyle='--') },

    'NC': { 'province_cn': ["山东省","山西省","河北省","天津市","北京市"],
            'use_im_west': True,
            'style': dict(edgecolor="#2a4651", linewidth=2, linestyle='--') },

    'EC': { 'province_cn': ["上海市","江苏省","浙江省","安徽省","福建省"],
            'style': dict(edgecolor="#5e8440", linewidth=2, linestyle='--') },

    'HC': { 'province_cn': ["湖南省","湖北省","江西省","河南省"],
            'style': dict(edgecolor="#dd9230", linewidth=2, linestyle='--') },

    'SW': { 'province_cn': ["四川省","重庆市","西藏自治区"],
            'style': dict(edgecolor="#841e2a", linewidth=2, linestyle='--') },

    'NW': { 'province_cn': ["陕西省","甘肃省","宁夏回族自治区","青海省","新疆维吾尔自治区"],
            'style': dict(edgecolor="#c55274", linewidth=2, linestyle='--') },

    'SC': { 'province_cn': ["广东省","广西壮族自治区","海南省","云南省","贵州省"],
            'style': dict(edgecolor="#347219", linewidth=2, linestyle='--') }
}

                  
grid_borders = []
for code, info in grid_regions.items():
                     
    geoms = prov_2343[prov_2343['province_cn'].isin(info['province_cn'])].geometry.tolist()
            
    if info.get('use_im_east'):
        geoms.append(im_east.geometry.iloc[0])
    if info.get('use_im_west'):
        geoms.append(im_west.geometry.iloc[0])
             
    merged = unary_union(geoms)
    merged = remove_small_islands(merged, min_area=5e9)
                                        
    grid_borders.append({
        'region': code,
        'geometry': merged,
        'style': info['style']
    })

grid_gdf = gpd.GeoDataFrame(grid_borders, crs=prov_2343.crs)

         
for _, row in grid_gdf.iterrows():
    gpd.GeoSeries(row.geometry).boundary.plot(
        ax=ax, zorder=3, **row['style']
    )

legend_handles = []
for code, info in grid_regions.items():
    style = info['style']
                             
    line = Line2D(
        [0], [0],
        color=style['edgecolor'],
        linewidth=style['linewidth'],
        linestyle=style['linestyle']
    )
    legend_handles.append((line, code))

                    
handles, labels = zip(*legend_handles)

         
leg =ax.legend(
    handles, labels,
    loc='upper left',                 
    frameon=False,
    edgecolor='gray',
    ncol = 2,
    fontsize=14,
    bbox_to_anchor=(0.85, 0.64),
    title_fontsize=14
)
ax.add_artist(leg)
                                           
                                                                                             
                                                
csv_path = r"D:\2025_Methanol_synthesis\GAMS\csv_Single_Prov\TNS_caps.csv"
df_line = pd.read_csv(csv_path)

        
df_line["Cap"] = df_line["Cap"] / 1000.0

                          
en2cn = {en: cn for cn, en in ch_en_map.items()}
centroid_cache = {}
centroid_cache["E_InnerMongo"] = im_east.geometry.iloc[0].centroid
centroid_cache["W_InnerMongo"] = im_west.geometry.iloc[0].centroid

def get_centroid_en(en_name: str):
    if en_name in centroid_cache:
        return centroid_cache[en_name]
    if en_name not in en2cn:
        raise KeyError(f"[NameMap] English→Chinese 映射失败: {en_name}")
    cn_name = en2cn[en_name]
    sub = prov_2343[prov_2343['province_cn'] == cn_name]
    if sub.empty:
        raise KeyError(f"[Province] 省份未在 shapefile 中找到: {cn_name} (from {en_name})")
    geom_union = unary_union(sub.geometry)
    pt = geom_union.representative_point()
    centroid_cache[en_name] = pt
    return pt

            
GW_bins_prov     = [0, 5, 10, 30]             
width_knots_prov = [1, 2, 3, 4]

        
style_by_type = {
    "AC": dict(color="#1f77b4", linestyle='-', marker='o'),
    "DC": dict(color="#ff0000", linestyle='--', marker='o')
}
first_plot = {"prov_ac": True, "prov_dc": True}

                  
for prov_type, key in [("AC", "prov_ac"), ("DC", "prov_dc")]:
    mask = (df_line["ACDC"].astype(str).str.upper() == prov_type)
    sub = df_line.loc[mask].copy()
    if sub.empty:
        continue

    vals = sub["Cap"].astype(float).clip(lower=0.01)
    widths = np.interp(vals, GW_bins_prov, width_knots_prov)

    for (o_en, d_en, cap, lw) in zip(sub["Origin"].astype(str),
                                     sub["Destination"].astype(str),
                                     vals, widths):
        try:
            p_o = get_centroid_en(o_en.strip())
            p_d = get_centroid_en(d_en.strip())
        except KeyError as e:
            print("[Skip]", e)
            continue

        sty = style_by_type[prov_type]

             
        ax.plot([p_o.x, p_d.x], [p_o.y, p_d.y],
                color=sty["color"], linestyle=sty["linestyle"],
                linewidth=lw, alpha=0.8,
                label=prov_type if first_plot[key] else "_nolegend_",
                zorder=4)

             
        ax.scatter([p_o.x], [p_o.y],
                   color=sty["color"], s=30, zorder=5,
                   edgecolor='black', linewidth=0.3, marker=sty["marker"])
        ax.scatter([p_d.x], [p_d.y],
                   color=sty["color"], s=30, zorder=5,
                   edgecolor='black', linewidth=0.3, marker=sty["marker"])

    first_plot[key] = False


                      
type_handles = []
type_labels  = []
for prov_type in ["AC", "DC"]:
    sty = style_by_type[prov_type]
    type_handles.append(Line2D([0], [0],
                                color=sty["color"],
                                linestyle=sty["linestyle"],
                                linewidth=2,
                                marker=sty["marker"],
                                markersize=6,
                                markerfacecolor=sty["color"],
                                markeredgecolor='black',
                                markeredgewidth=0.3))
    type_labels.append(prov_type)

leg_type = ax.legend(
    handles=type_handles,
    labels=type_labels,
    title="Transmission lines",
    loc="lower left",
    frameon=False,
    fontsize=14,
    title_fontsize=13,
    bbox_to_anchor=(0.85, 0.63),          
    ncol=2,
    labelspacing=0.2
)
ax.add_artist(leg_type)


              
out_file = os.path.join(out_dir, "China_grid_with_lines_prov.png")
fig.savefig(out_file, dpi=600)  
print(f"图片已保存到: {out_file}")
plt.show()



