                                 
el = "SOE"         
st = "SST"
runs = [

    {"year": "2040", "ed": "21"},
    {"year": "2040", "ed": "25"},
    {"year": "2040", "ed": "50"},
    {"year": "2040", "ed": "75"},
    {"year": "2040", "ed": "100"},
    {"year": "2050", "ed": "25"},
    {"year": "2050", "ed": "50"},
    {"year": "2050", "ed": "59"},
    {"year": "2050", "ed": "75"},
    {"year": "2050", "ed": "100"},
]


                       
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib as mpl
import matplotlib.ticker as ticker
from matplotlib.ticker import LinearLocator, FuncFormatter
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
def plot_map(el, year, ed):
                     
    prov_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map\CN_Province.shp"
    city_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map_WGS1984\CN_Prefecture.shp"
    nine_shp = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode\CN_Map\Jiu_Duan_Xian.shp"
    excel_path = rf"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new\{el}\{year}\ED{ed}\Nom_size_{el}_{year}_ED{ed}_2.xlsx"
    tns_nom_path   = rf"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new\{el}\{year}\ED{ed}\TNS_nom_{el}_{year}_ED{ed}_2s.xlsx"
    tns_yr_path   = rf"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\Results_new\{el}\{year}\ED{ed}\TNS_yr_{el}_{year}_ED{ed}_2s.xlsx"

    out_dir = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\fig"
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
        fontsize=11,
        bbox_to_anchor=(-0.30, 0.72),
        title_fontsize=11
    )
    ax.add_artist(leg)
                                               

                                                                                 
                                                                                                 
    df_ed = pd.read_excel(excel_path, sheet_name="Total_size")
    df_ed = df_ed.rename(columns={df_ed.columns[0]:'Province', df_ed.columns[1]:'Value'})
                
    df_ed['Province'] = df_ed['Province'].astype(str).str.strip()

                                                                                
    ch_en_df = pd.DataFrame(list(ch_en_map.items()), columns=['province_cn','province_en'])

                                                                                    
    prov_2343['province_cn'] = prov_2343['省']

                                                                                        
    prov_merged = (
        prov_2343
        .merge(ch_en_df, on='province_cn', how='left')
                                 
        .merge(df_ed[['Province','Value']], left_on='province_en', right_on='Province', how='left')
                                            
    )

    mask_drop = (
        (prov_merged['province_cn']=="内蒙古自治区") |
        (prov_merged['province_en']=="Inner Mongolia")
    )
              
    prov_main = prov_merged[~mask_drop][['province_en','geometry']]

                                                                                            
    west_df = gpd.GeoDataFrame(
        {'province_en': ['W_InnerMongo']},
        geometry=im_west.geometry,
        crs=prov_2343.crs
    )
    east_df = gpd.GeoDataFrame(
        {'province_en': ['E_InnerMongo']},
        geometry=im_east.geometry,
        crs=prov_2343.crs
    )

                                                                              
                               
    prov_main = (
        prov_main
        .merge(df_ed[['Province','Value']],
                left_on='province_en', right_on='Province',
                how='left')
        [['province_en','geometry','Value']]
    )

    west_df = (
        west_df
        .merge(df_ed[['Province','Value']],
                left_on='province_en', right_on='Province',
                how='left')
        [['province_en','geometry','Value']]
    )
    east_df = (
        east_df
        .merge(df_ed[['Province','Value']],
                left_on='province_en', right_on='Province',
                how='left')
        [['province_en','geometry','Value']]
    )
    print(">>> west_dE:\n", west_df[['province_en','Value']])
    print(">>> east_dE:\n", east_df[['province_en','Value']])
                                                                             
    plot_gdf = pd.concat([prov_main, west_df, east_df], ignore_index=True)
    plot_gdf = gpd.GeoDataFrame(plot_gdf, geometry='geometry', crs=prov_2343.crs)
    print(plot_gdf[plot_gdf['province_en'].isin(['W_InnerMongo','E_InnerMongo'])])

    plot_gdf.plot(
        column='Value',
        cmap='viridis_r',
        alpha=0.3,
        linewidth=0.5,
        edgecolor='white',
        ax=ax,
        zorder=1,
    )

                                     
    vmin, vmax = plot_gdf['Value'].min(), plot_gdf['Value'].max()
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

                      
    orig_cmap = mpl.colormaps['viridis_r']
    colors = orig_cmap(np.linspace(0,1,256))
    colors = orig_cmap(np.linspace(0, 1, 256))
    colors[:, -1] = 0.3                              
    cmap_alpha = mpl.colors.ListedColormap(colors)

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap_alpha)
    sm._A = []

    cax = inset_axes(
        ax,
        width="2.7%",                    
        height="36%",                  
        loc="lower left",
        bbox_to_anchor=(1.0, 0.5, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0
    )

    cbar = plt.colorbar(
        sm,
        cax=cax,
        orientation='vertical',
        label='Capacity (GW)'
    )



                        
    cbar.ax.patch.set_facecolor('lightgrey')
    cbar.outline.set_edgecolor('none')
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Capacity (GW)', fontsize=18, labelpad=5)


    cbar.locator = LinearLocator(6)              
    cbar.formatter = FuncFormatter(lambda val, _pos: f"{val:.0f}")
    cbar.update_ticks()
                                                                                 
                                                                    

                    
    exp_sheets  = ["U_PV_exp", "U_WT_exp"]
    imp_sheets  = ["U_imp"]
    prov_sheet  = "U_prov"

                        
    style_group = {
        "exp":     {"color":"#D40000", "linestyle":"-.", "label":"Export"},
        "imp":     {"color":"#0000FF", "linestyle":"-.", "label":"Import"},
        "prov_ac": {"color":"#29a59f", "linestyle":"-",  "label":"Prov. Tx AC"},
        "prov_dc": {"color":"#C03FA2", "linestyle":"--",  "label":"Prov. Tx DC"},
    }

    first_plot = {"exp":True, "imp":True, "prov_ac":True, "prov_dc":True}


                                                                       
    for sheet, group in zip(
        exp_sheets + imp_sheets,
        ["exp"]*len(exp_sheets) + ["imp"]*len(imp_sheets)
    ):
        df = pd.read_excel(tns_yr_path, sheet_name=sheet)\
            .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value"])
        
        print(f"{group} {sheet}: {len(df)} 条数据, Value统计: min={df['Value'].min()}, max={df['Value'].max()}, 非零数={sum(df['Value']>0)}")

              
        TWh_bins = [0, 0.5, 1, 2]                   
        width_knots = [0.5, 1, 2, 3]                        

        vals = df["Value"].clip(lower=0.0001) / 1000           

                 
        widths = np.interp(vals, TWh_bins, width_knots)
        print(f"==== {group} ====")
        for v, lw in zip(vals, widths):
            print(f"Value: {v:.2f} TWh, Linewidth: {lw:.2f}")

        cfg = style_group[group]
        pts1 = gpd.GeoSeries(
            gpd.points_from_xy(df.Longitude_1, df.Latitude_1),
            crs="EPSG:4326"
        ).to_crs(epsg=2343)
        pts2 = gpd.GeoSeries(
            gpd.points_from_xy(df.Longitude_2, df.Latitude_2),
            crs="EPSG:4326"
        ).to_crs(epsg=2343)

        for p1, p2, lw in zip(pts1, pts2, widths):
            ax.plot([p1.x, p2.x], [p1.y, p2.y],
                    color=cfg["color"], linestyle=cfg["linestyle"], linewidth=lw,
                    alpha=0.7,
                    label=cfg["label"] if first_plot[group] else "_nolegend_",
                    zorder=2.5)
        first_plot[group] = False

                           
        if group=="exp":
            ax.scatter(pts1.x, pts1.y, marker='o', facecolor='grey', edgecolor='black', s=15, zorder=4)
        elif group=="imp":
            ax.scatter(pts1.x, pts1.y, marker='o', facecolor='white', edgecolor='grey', s=15, zorder=4)

                                                          
    def get_label_text(group, low, high):
        if group == "exp":
            symbol = r"P^{\mathrm{City,ex}}_{i\prime,j}"
        else:
            symbol = r"P^{\mathrm{City,im}}_{i,j}"
        if low == 0:
            return rf"${symbol} \leq {high}$"
        else:
            return rf"${low} < {symbol} \leq {high}$"

    cap_handles, cap_labels = [], []
    for group in ["exp", "imp"]:
        cfg = style_group[group]
        for i in range(len(TWh_bins) - 1):
            low, high = TWh_bins[i], TWh_bins[i+1]
            lw = width_knots[i]              
            cap_handles.append(
                Line2D([0], [0],
                    color=cfg["color"],
                    linestyle=cfg["linestyle"],
                    linewidth=lw)
            )
            cap_labels.append(get_label_text(group, low, high))

    leg_cap = ax.legend(
        handles=cap_handles,
        labels=cap_labels,
        title=r"Municipal annual transmission (TWh)",
        loc="lower left",
        frameon=False,
        fontsize=11,
        title_fontsize=11,
        bbox_to_anchor=(-0.30, 0.34),
        labelspacing=0.2,
        ncol=2
    )
    ax.add_artist(leg_cap)

                                                                            
    dfp = pd.read_excel(tns_nom_path, sheet_name=prov_sheet)\
            .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value","Type"])

             
    pts1_all = gpd.GeoSeries(
        gpd.points_from_xy(dfp.Longitude_1, dfp.Latitude_1), crs="EPSG:4326"
    ).to_crs(epsg=2343)
    pts2_all = gpd.GeoSeries(
        gpd.points_from_xy(dfp.Longitude_2, dfp.Latitude_2), crs="EPSG:4326"
    ).to_crs(epsg=2343)

               
    GW_bins_prov = [0, 2, 4, 6]
    width_knots_prov = [1, 2, 3, 4]        

    for prov_type, key in [("AC", "prov_ac"), ("DC", "prov_dc")]:
        mask = (dfp.Type == prov_type)
        vals = dfp.loc[mask, "Value"].clip(lower=0.01)
        cfg = style_group[key]

                            
        widths = np.interp(vals, GW_bins_prov, width_knots_prov)

        pts1 = pts1_all[mask]
        pts2 = pts2_all[mask]

        for p1, p2, lw in zip(pts1, pts2, widths):
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

                    
                                              
    def get_prov_label_text(group, low, high):
        group_suffix = group.split("_")[1].upper()
        symbol = rf"U^{{\mathrm{{Prov,{group_suffix}}}}}_{{{{j\prime,j}}}}"

        if low == 0:
            return rf"${symbol} \leq {high}$"
        else:
            return rf"${low} < {symbol} \leq {high}$"

    cap_handles_prov, cap_labels_prov = [], []
    for group_prov in ["prov_ac", "prov_dc"]:
        cfg_prov = style_group[group_prov]
        for i in range(len(GW_bins_prov)-1):          
            low = GW_bins_prov[i]
            high = GW_bins_prov[i+1]
            lw = width_knots_prov[i]
            cap_handles_prov.append(
                Line2D([0], [0],
                    color=cfg_prov["color"],
                    linestyle=cfg_prov["linestyle"],
                    linewidth=lw)
            )
            cap_labels_prov.append(get_prov_label_text(group_prov, low, high))
            
    leg_cap_prov = ax.legend(
        handles=cap_handles_prov,
        labels=cap_labels_prov,
        title=r"Provincial transmission capacity (GW)",
        loc="lower left",
        frameon=False,
        fontsize=11,
        title_fontsize=11,
        bbox_to_anchor=(-0.30, 0.17),
        ncol=2,
        labelspacing=0.2
    )
    ax.add_artist(leg_cap_prov)
                                                              

                                                                                  
                          
    raw_portion = pd.read_excel(excel_path, sheet_name="Portion")

                                  
    first_col = raw_portion.columns[0]
    raw_portion = raw_portion.rename(columns={
        'Prov': 'province_en',  
        'Longitude': 'Longitude',
        'Latitude': 'Latitude'
    })


                         
    if 'longitude' in raw_portion.columns:
        raw_portion = raw_portion.rename(columns={'longitude':'Longitude'})
    if 'Latitude' not in raw_portion.columns and 'latitude' in raw_portion.columns:
        raw_portion = raw_portion.rename(columns={'latitude':'Latitude'})
    if 'Lib' in raw_portion.columns:
        raw_portion.rename(columns={'Lib':'LiB'}, inplace=True)

            
    for col in ['PV','WT','SOE','SST']:
        if col in raw_portion.columns:
            raw_portion[col] = raw_portion[col].fillna(0)
                   
                         
    df_portion = gpd.GeoDataFrame(
        raw_portion,
        geometry=gpd.points_from_xy(raw_portion.Longitude, raw_portion.Latitude),
        crs="EPSG:4326"
    ).to_crs(epsg=2343)

                                                  
    gdf_portion = df_portion.copy()
    gdf_portion = gdf_portion.dropna(subset=['Total_size'])           
    gdf_portion = gdf_portion.rename(columns={'Total_size':'capacity'})


            
    min_radius   = 15000
    max_radius   = 150000
    max_capacity = gdf_portion['capacity'].max()


                          
    components = ['PV','WT','SOE','SST']
             
    colors = ["#d73027", "#fc8d59", "#fee08b", "#91cf60"]
                                                                     
                                                                     


                        
    offsets = {
        'Anhui': (0, 0), 'Macau': (0, 0), 'Beijing': (0, 0), 'Fujian': (0, 0), 'Gansu': (0, 0), 'Guangdong': (0, 0),
        'Guangxi': (0, 0), 'Guizhou': (0, 0), 'Hainan': (0, 0), 'Hebei': (0, 0), 'Henan': (0, 0), 'Heilongjiang': (0, 0),
        'Hubei': (0, 0), 'Hunan': (0, 0), 'Jilin': (0, 0), 'Jiangsu': (0, 0), 'Jiangxi': (0, 0), 'Liaoning': (0, 0),
        'Ningxia': (0, 0), 'Qinghai': (0, 0), 'Shandong': (0, 0), 'Shanxi': (0, 0), 'Shaanxi': (0, 0), 'Shanghai': (300000, 0),
        'Sichuan': (0, 0), 'Taiwan': (0, 0), 'Tianjin': (600000, -50000), 'Tibet': (0, 0), 'Hong Kong': (0, 0), 'Sinkiang': (0, 0),
        'Yunnan': (0, 0), 'Zhejiang': (0, 0), 'Chongqing': (0, 0), 'W_InnerMongo': (0, 0), 'E_InnerMongo': (0, 0)
    }



                    
    max_capacity = gdf_portion['capacity'].max()
    min_radius, max_radius = 15000, 150000

    for _, row in gdf_portion.iterrows():
        cap = row['capacity']
        if cap <= 0:
            continue

                 
        total = sum(row[c] for c in components)
        if total == 0:
            continue              
        ratios = [row[c] / total for c in components]


                                               
                                                                                              
        radius = 90000                        

                
        x0, y0 = row.geometry.x, row.geometry.y
                                       
        dx, dy = offsets.get(row['province_en'], (0, 0))
        x, y = x0 + dx, y0 + dy

                
        if dx != 0 or dy != 0:
                         
            L = np.hypot(dx, dy)
            ux, uy = dx / L, dy / L

                                   
            border_x = x - ux * radius
            border_y = y - uy * radius

                                           
            arrow = FancyArrowPatch(
                (x0, y0),                    
                (border_x, border_y),        
                arrowstyle='-|>',
                mutation_scale=10,                                 
                color="black",                     
                linewidth=1.0,                 
                zorder=4.5
            )
            ax.add_patch(arrow)

                                                                                   
                                    

                      
        start = 0
        for frac, color in zip(ratios, colors):
            theta = frac * 360
            wedge = Wedge(
                center=(x, y),
                r=radius,
                theta1=start,
                theta2=start + theta,
                facecolor=color,
                edgecolor='grey',
                linewidth=0.5,
                zorder=4
            )
            ax.add_patch(wedge)
            start += theta

                                             
    legend_patches = [
        Patch(facecolor=color, edgecolor='none', label=comp)
        for comp, color in zip(components, colors)
    ]
    leg_pie = ax.legend(
        handles=legend_patches,
        loc="upper left",
        bbox_to_anchor=(-0.30, 0.6),
        frameon=False,
        fontsize=11,
        ncol = 2,
        title_fontsize=11,                 
    )
                            



                              

    filename = f"Map_{el}_{year}_ED{ed}_Prov.png"
    out_path = os.path.join(out_dir, filename)
    fig.canvas.draw()
    fig.savefig(out_path, dpi=1000)
    print(f"Saved：{out_path}")

if __name__ == "__main__":
    for cfg in runs:
        plot_map(el=el, year=cfg["year"], ed=cfg["ed"])