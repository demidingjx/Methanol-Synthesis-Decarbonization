                       
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

                 
prov_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map\CN_Province.shp"
city_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map_WGS1984\CN_Prefecture.shp"
nine_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map\Jiu_Duan_Xian.shp"
out_dir = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\fig"
file_path = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\Plant_Distribution\CN_MeOH_Plants_Location.xlsx"

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

                                                                                
plant_loc = pd.read_excel(file_path, sheet_name = "Province")

plant_loc = plant_loc[["Capacity", "Lons", "Lats"]]

plant_loc.dropna(axis = 0, inplace = True)

plant_loc

plant_loc["Capacity"] = pd.to_numeric(plant_loc["Capacity"], errors="coerce")
plant_loc = plant_loc.dropna(subset=["Capacity", "Lons", "Lats"])
plant_loc["CapMt"] = plant_loc["Capacity"] / 1000.0

           
gdcens = gpd.GeoDataFrame(
    plant_loc,
    geometry=gpd.points_from_xy(plant_loc["Lons"], plant_loc["Lats"]),
    crs="EPSG:4326"
).to_crs(epsg=2343)


                                    
plant_Caps = plant_loc['Capacity'].copy() / 1000                
cmap = plt.cm.plasma                                                                                             
vmin, vmax = gdcens["CapMt"].min(), gdcens["CapMt"].max()
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

            
for cap in sorted(plant_Caps.unique()):
    norm_val = norm(cap)              
    print(f"Capacity={cap:.2f} Mton/year -> normalized={norm_val:.3f}")
print("Colorbar range:", norm.vmin, "→", norm.vmax)


                          
gdcens_sorted = gdcens.sort_values('CapMt')
gdcens_sorted.plot(
    ax=ax,
    column="CapMt",
    cmap=cmap,
    vmin=vmin, vmax=vmax,
    markersize=20,                                              
    alpha=0.8,
    zorder=3
)

sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])


                                
                                                           

                             
cax = inset_axes(
    ax,
    width = "3%",                           
    height = "40%",                         
    loc = "center left",               
    bbox_to_anchor = (-0.03, 0.15, 1.0, 1.0),                
    bbox_transform = ax.transAxes,
    borderpad = 0
)

cbar = plt.colorbar(sm, cax = cax,
                    extend = "neither"                            
                    )

cbar.ax.minorticks_on()
cbar.ax.yaxis.set_ticks_position("right")
cbar.ax.yaxis.set_label_position("right")
cbar.outline.set_visible(False)                   
cbar.ax.tick_params(which = "major", labelsize = 10, length = 3)           
cbar.ax.tick_params(which = "minor", labelsize = 10, length = 2)           

                                                               
                            
cax.text(-1.0, 0.5, "Production capacity (Mton/year)",                    
         va = "center", ha = "left", fontsize = 13,
         rotation = 90, transform = cax.transAxes)


                                  
cord_x = 1.05
ax.text(cord_x, 0.89, "N", transform = ax.transAxes,
        fontsize = 12, fontweight = 'bold', ha = 'center', va = 'center')

ax.annotate(
    text = " ",
    xy = (cord_x, 0.87),                                 
    xytext = (cord_x, 0.8),                      
    arrowprops = dict(facecolor = 'black', width = 3, headwidth = 8),
    ha = 'center', va = 'center', fontsize = 14,
    xycoords = 'axes fraction'                                 
)

ax.axis("off")

plt.draw()               
out_png = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\fig\MeOH_Distribution_correct.png"
fig.savefig(out_png, dpi=300, pad_inches=0.05, transparent=True)
