                                 
el   = "SOE"  
year = "2040"
ed   = "75"
ST   = "SST"

                       
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib as mpl
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

                 
prov_shp = r"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\pycode\CN_Map\CN_Province.shp"
nine_shp = r"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\pycode\CN_Map\Jiu_Duan_Xian.shp"
excel_path = rf"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\Results\{el}\{year}\ED{ed}\Nom_size_{el}_{year}_ED{ed}_2.xlsx"
tns_path   = rf"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\Results\{el}\{year}\ED{ed}\TNS_yr_{el}_{year}_ED{ed}_2s.xlsx"
out_dir = r"D:\GAMS_optimization\Statewide\Updated_Gams\P3_Geographical_allocation\fig"
os.makedirs(out_dir, exist_ok=True)
                                                                            
prov = gpd.read_file(prov_shp, engine='fiona', encoding='utf-8')
nine = gpd.read_file(nine_shp, engine='fiona', encoding='utf-8')

                 
prov_geo = prov.to_crs(epsg=4326)

                          
prov_2343 = prov.to_crs(epsg=2343)
nine_2343 = nine.to_crs(epsg=2343)

                                                                                   
fig, ax = plt.subplots(figsize=(12,9), constrained_layout=True)
albers_proj = 'EPSG:2343'
             
prov_2343.plot(ax=ax, facecolor='lightgray', edgecolor='white', linewidth=0.5, zorder=1)
nine_2343.plot(ax=ax, color='gray',  linewidth=1.5,  zorder=2)
ax.set_axis_off()
                        
             
bbox_geo = box(106.5, 2.8, 123.0, 24.5)
       
bbox_2343 = gpd.GeoSeries([bbox_geo], crs=4326).to_crs(epsg=2343).iloc[0]
      
prov_crop = prov_2343[prov_2343.intersects(bbox_2343)]
nine_crop = nine_2343[nine_2343.intersects(bbox_2343)]
axins = inset_axes(ax, width='20%', height='20%', loc='lower right', bbox_to_anchor=(0.11, 0.27, 1.0, 1.0), bbox_transform=ax.transAxes, borderpad=0)
prov_crop.plot(ax=axins, facecolor='lightgray', edgecolor='white', linewidth=0.5, zorder=1)
nine_crop.plot(ax=axins, color='gray', linewidth=1.5, linestyle='--', zorder=2)

             
minx, miny, maxx, maxy = bbox_2343.bounds
axins.set_xlim(minx, maxx)
axins.set_ylim(miny, maxy)
axins.set_xticks([])
axins.set_yticks([])

rect = Rectangle((0, 0), 1, 1, transform=axins.transAxes, fill=False, edgecolor='black', linewidth=1)
axins.add_patch(rect)

ax.axis('off')

                                                                                      
                     
im_geom = prov_geo.loc[prov_geo['省']=="内蒙古自治区", 'geometry'].iloc[0]

        
meridian = LineString([ (111.5, -90), (111.5, 90) ])
parts = list(split(im_geom, meridian).geoms)

           
west_parts = [g for g in parts if g.centroid.x <= 111.5]
east_parts = [g for g in parts if g.centroid.x  > 111.5]
west_union = unary_union(west_parts)
east_union = unary_union(east_parts)

                   
west_2343 = gpd.GeoSeries([west_union], crs=4326).to_crs(epsg=2343)
east_2343 = gpd.GeoSeries([east_union], crs=4326).to_crs(epsg=2343)


                                                                                

                                                  

df_ed = pd.read_excel(excel_path, sheet_name="ED_prov")
df_ed = df_ed.rename(columns={df_ed.columns[0]:'Province', df_ed.columns[1]:'Value'})

              
ch_en_df = pd.DataFrame(list(ch_en_map.items()), columns=['province_cn','province_en'])

                             
prov_2343['province_cn'] = prov_2343['省']
prov_merged = prov_2343.merge(ch_en_df, on='province_cn', how='left')

                                           
prov_main = prov_merged[prov_merged['province_cn'] != "内蒙古自治区"].copy()

                           
west_df = gpd.GeoDataFrame({'province_en': ['W_InnerMongo'], 'geometry': west_2343})
east_df = gpd.GeoDataFrame({'province_en': ['E_InnerMongo'], 'geometry': east_2343})

            
prov_main = prov_main.merge(df_ed, left_on='province_en', right_on='Province', how='left')
west_df  = west_df.merge( df_ed, left_on='province_en', right_on='Province', how='left')
east_df  = east_df.merge( df_ed, left_on='province_en', right_on='Province', how='left')

                           
plot_gdf = pd.concat([
    prov_main[['province_en','geometry','Value']],
    west_df[['province_en','geometry','Value']],
    east_df[['province_en','geometry','Value']]
], ignore_index=True)
plot_gdf = gpd.GeoDataFrame(plot_gdf, geometry='geometry', crs=prov_2343.crs)

                                         
plot_gdf.plot(
    column='Value',
    cmap='summer_r',
    alpha=0.3,
    linewidth=0.5,
    edgecolor='white',
    ax=ax,
    zorder=1,
)

                                     
vmin, vmax = plot_gdf['Value'].min(), plot_gdf['Value'].max()
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

                         
orig_cmap = mpl.cm.get_cmap('summer_r', 256)
colors = orig_cmap(np.linspace(0, 1, 256))
colors[:, -1] = 0.3                                 
cmap_alpha = mpl.colors.ListedColormap(colors)

sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap_alpha)
sm._A = []

cax = inset_axes(
    ax,
    width="3%",                    
    height="40%",                  
    loc="lower left",
    bbox_to_anchor=(1.0, 0.5, 1, 1),
    bbox_transform=ax.transAxes,
    borderpad=0
)

cbar = plt.colorbar(
    sm,
    cax=cax,
    orientation='vertical',
    label='Electrification Degree'
)

                                 
cbar.ax.patch.set_facecolor('lightgrey')
cbar.outline.set_edgecolor('none')

                  
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Electrification Degree', fontsize=16, labelpad=20)


                                                                             
                                                                
from matplotlib.lines import Line2D

def _global_min_max(sheets):
    vals = []
    for sh in sheets:
        df = pd.read_excel(tns_path, sheet_name=sh)\
               .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value"])
        vals += df["Value"].clip(lower=0).tolist()
    arr = np.array(vals)
    return arr.min(), arr.max()

                
exp_sheets  = ["U_PV_exp", "U_WT_exp"]
imp_sheets  = ["U_imp"]
prov_sheet  = "U_prov"

                    
style_group = {
    "exp":     {"color":"#2C86DB", "linestyle":"-.", "label":"Export"},
    "imp":     {"color":"#CE1C1C", "linestyle":"-.", "label":"Import"},
    "prov_ac": {"color":"#2254e9", "linestyle":"-",  "label":"Prov. Tx AC"},
    "prov_dc": {"color":"#A731A5", "linestyle":"-",  "label":"Prov. Tx DC"},
}

                                  
exp_min, exp_max = _global_min_max(exp_sheets)
imp_min, imp_max = _global_min_max(imp_sheets)

              
min_lw, max_lw = 0.5, 6.0

first_plot = {"exp":True, "imp":True, "prov_ac":True, "prov_dc":True}


                                                                   
for sheet, group in zip(
    exp_sheets + imp_sheets,
    ["exp"]*len(exp_sheets) + ["imp"]*len(imp_sheets)
):
    df = pd.read_excel(tns_path, sheet_name=sheet)\
           .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value"])
    vals = df["Value"].clip(lower=0)
    vmin, vmax = (exp_min, exp_max) if group=="exp" else (imp_min, imp_max)

          
    norm   = (vals - vmin) / (vmax - vmin + 1e-6)
    widths = norm * (max_lw - min_lw) + min_lw

    cfg = style_group[group]
    pts1 = gpd.GeoSeries(
        gpd.points_from_xy(df.Longitude_1, df.Latitude_1),
        crs="EPSG:4326"
    ).to_crs(epsg=2343)
    pts2 = gpd.GeoSeries(
        gpd.points_from_xy(df.Longitude_2, df.Latitude_2),
        crs="EPSG:4326"
    ).to_crs(epsg=2343)

    for p1,p2,lw in zip(pts1, pts2, widths):
        ax.plot([p1.x,p2.x],[p1.y,p2.y],
                color=cfg["color"], linestyle=cfg["linestyle"], linewidth=lw,
                alpha=0.7,
                label=cfg["label"] if first_plot[group] else "_nolegend_",
                zorder=2.5)
    first_plot[group] = False

        
    face = "white" if group=="exp" else "grey"
    s1, s2 = (15,30) if group=="exp" else (10,30)
    ax.scatter(pts1.x, pts1.y, marker='o', facecolor=face, edgecolor='grey', s=s1, zorder=4)
    ax.scatter(pts2.x, pts2.y, marker='o', facecolor=face, edgecolor='grey', s=s2, zorder=4)


                                                                        
                                                                       
dfp = pd.read_excel(tns_path, sheet_name=prov_sheet)\
          .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value","Type"])

         
pts1_all = gpd.GeoSeries(
    gpd.points_from_xy(dfp.Longitude_1, dfp.Latitude_1), crs="EPSG:4326"
).to_crs(epsg=2343)
pts2_all = gpd.GeoSeries(
    gpd.points_from_xy(dfp.Longitude_2, dfp.Latitude_2), crs="EPSG:4326"
).to_crs(epsg=2343)

               
ac_vals = dfp.loc[dfp.Type=="AC", "Value"].clip(lower=0)
dc_vals = dfp.loc[dfp.Type=="DC", "Value"].clip(lower=0)
prov_ac_min, prov_ac_max = ac_vals.min(), ac_vals.max()
prov_dc_min, prov_dc_max = dc_vals.min(), dc_vals.max()

for prov_type, key, (vmin, vmax) in [
    ("AC","prov_ac",(prov_ac_min,prov_ac_max)),
    ("DC","prov_dc",(prov_dc_min,prov_dc_max))
]:
                             
    mask = (dfp.Type == prov_type)
    vals = dfp.loc[mask, "Value"].clip(lower=0)
    cfg = style_group[key]

             
    norm   = (vals - vmin) / (vmax - vmin + 1e-6)
    widths = norm * (max_lw - min_lw) + min_lw

          
    pts1 = pts1_all[mask]
    pts2 = pts2_all[mask]

          
    for (p1, p2, lw) in zip(pts1, pts2, widths):
        ax.plot(
            [p1.x, p2.x], [p1.y, p2.y],
            color=cfg["color"],
            linestyle=cfg["linestyle"],
            linewidth=lw,
            alpha=0.8,
            label=cfg["label"] if first_plot[key] else "_nolegend_",
            zorder=3
        )
    first_plot[key] = False


                                                             
                    
flow_handles = [
    Line2D([0],[0],
           color=style_group[g]["color"],
           linestyle=style_group[g]["linestyle"],
           linewidth=2,
           label=style_group[g]["label"])
    for g in ["exp","imp","prov_ac","prov_dc"]
]
leg_flow = ax.legend(handles=flow_handles,
                     title="Flow Type",
                     loc="lower left",
                     bbox_to_anchor=(0.25, 0.3),                              
                     fontsize=12,                       
                     title_fontsize=12,                 

                     frameon=False)
ax.add_artist(leg_flow)                  

sample_vals = [10,100,1000]
cap_handles, cap_labels = [], []
for group, (vmin, vmax) in [
    ("exp",(exp_min,exp_max)),
    ("imp",(imp_min,imp_max)),
    ("prov_ac",(prov_ac_min,prov_ac_max)),
    ("prov_dc",(prov_dc_min,prov_dc_max))
]:
    cfg = style_group[group]
    for v in sample_vals:
        norm = (v - vmin)/(vmax - vmin + 1e-6)
        lw   = norm*(max_lw - min_lw) + min_lw
        cap_handles.append(
            Line2D([0],[0],
                   color=cfg["color"],
                   linestyle=cfg["linestyle"],
                   linewidth=lw)
        )
        cap_labels.append(f"{cfg['label']} {v} GWh")

leg_cap = ax.legend(handles=cap_handles,
                    labels=cap_labels,
                    title="Capacity (GWh)", 
                    loc="lower left",
                    frameon=False,
                    fontsize=12,
                    title_fontsize=12, 
                    bbox_to_anchor=(-0.05, 0.1),                              
                    ncol=2)
ax.add_artist(leg_cap) 

                                                          

                                                                              
                      
raw_portion = pd.read_excel(excel_path, sheet_name="Portion")

                              
first_col = raw_portion.columns[0]
raw_portion = raw_portion.rename(columns={
    'Prov': 'province_en',  
    'Longitude': 'Longitude',
    'Latitude': 'Latitude'
})
        
print("Portion:", raw_portion.columns.tolist())

                     
if 'longitude' in raw_portion.columns:
    raw_portion = raw_portion.rename(columns={'longitude':'Longitude'})
if 'Latitude' not in raw_portion.columns and 'latitude' in raw_portion.columns:
    raw_portion = raw_portion.rename(columns={'latitude':'Latitude'})

        
for col in ['PV','WT','SOE','Lib','SST']:
    if col in raw_portion.columns:
        raw_portion[col] = raw_portion[col].fillna(0)
               
                     
df_portion = gpd.GeoDataFrame(
    raw_portion,
    geometry=gpd.points_from_xy(raw_portion.Longitude, raw_portion.Latitude),
    crs="EPSG:4326"
).to_crs(epsg=2343)
print("GeoDataFram：", df_portion.columns.tolist())

                                              
gdf_portion = df_portion.copy()
gdf_portion = gdf_portion.dropna(subset=['Total_size'])           
gdf_portion = gdf_portion.rename(columns={'Total_size':'capacity'})

       
print("合并后 gdf_portion 列：", gdf_portion.columns.tolist())
                                                

        
min_radius   = 15000
max_radius   = 150000
max_capacity = gdf_portion['capacity'].max()


                      
components = ['PV','WT','SOE','Lib','SST']
         
colors = ["#a30543", "#f36f43", "#fbda83", "#e9f4a3", "#4965b0"]

                    
offsets = {
    'Anhui':(800000,-200000),'Macau':(0,0),'Beijing':(0,0),'Fujian':(0,0),'Gansu':(0,750000),'Guangdong':(0,0),
    'Guangxi':(0,0),'Guizhou':(0,0),'Hainan':(0,0),'Hebei':(1000000,130000),'Henan':(800000,80000),'Heilongjiang':(0,0),
    'Hubei':(0,0),'Hunan':(0,0),'Jilin':(0,0),'Jiangsu':(550000,0),'Jiangxi':(0,0),'Liaoning':(450000,40000),
    'Ningxia':(0,750000),'Qinghai':(0,0),'Shandong':(900000,0),'Shanxi':(1050000,70000),'Shaanxi':(0,1150000),'Shanghai':(200000,0),
    'Sichuan':(0,0),'Taiwan':(0,0),'Tianjin':(200000,40000),'Tibet':(0,0),'Hong Kong':(0,0),'Sinkiang':(0,0),
    'Yunnan':(0,0),'Zhejiang':(0,0),'Chongqing':(0,0),'W_InnerMongo':(0,280000),'E_InnerMongo':(0,0),
}


                
max_capacity = gdf_portion['capacity'].max()
min_radius, max_radius = 15000, 150000

for _, row in gdf_portion.iterrows():
    cap = row['capacity']
    if cap <= 0:
        continue

             
    total = sum(row[c] for c in components)
    ratios = [row[c] / total for c in components]

                                           
    radius = (np.log(cap) / np.log(max_capacity)) * (max_radius - min_radius) + min_radius

            
    x0, y0 = row.geometry.x, row.geometry.y
                                   
    dx, dy = offsets.get(row['province_en'], (0, 0))
    x, y = x0 + dx, y0 + dy

                         
    if dx != 0 or dy != 0:
        ax.plot(
            [x0, x], [y0, y],
            linestyle='--', color="#8C8C8D",
            linewidth=1, zorder=2
        )
                  
    start = 0
    for frac, color in zip(ratios, colors):
        theta = frac * 360
        wedge = Wedge(
            center=(x, y),
            r=radius,
            theta1=start,
            theta2=start + theta,
            facecolor=color,
            edgecolor='#B0AAAE',
            linewidth=0.5,
            zorder=4
        )
        ax.add_patch(wedge)
        start += theta



                                         
legend_patches = [
    Patch(facecolor=color, edgecolor='#B0AAAE', label=comp)
    for comp, color in zip(components, colors)
]
leg_pie = ax.legend(
    handles=legend_patches,
    title="Components",
    loc="lower left",
    bbox_to_anchor=(-0.05, 0.32),
    frameon=False,
    fontsize=12,
    title_fontsize=12,                 
    ncol=2
)

plt.show()

                          

filename = f"Map_{el}_{year}_ED{ed}_Prov.png"
out_path = os.path.join(out_dir, filename)
fig.canvas.draw()
fig.savefig(out_path, dpi=300)
print(f"Saved：{out_path}")