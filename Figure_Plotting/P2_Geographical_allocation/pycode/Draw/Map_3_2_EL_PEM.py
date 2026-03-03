                                 
el = "PEM"         
ST   = "HST"
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
    def remove_small_islands(geom, min_area=5e10):
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
        merged = remove_small_islands(merged, min_area=5e10)
                                            
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
        fontsize=12,
        bbox_to_anchor=(-0.18, 0.56),
        title_fontsize=14
    )
    ax.add_artist(leg)

                                                                                 
                                                                                              
    df_ed = pd.read_excel(excel_path, sheet_name="ED_prov")
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
        cmap='plasma_r',
        alpha=0.4,
        linewidth=0.5,
        edgecolor='white',
        ax=ax,
        zorder=1,
    )

                                     
    vmin, vmax = plot_gdf['Value'].min(), plot_gdf['Value'].max()
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

                      
    orig_cmap = mpl.colormaps['plasma_r']
    colors = orig_cmap(np.linspace(0,1,256))
    colors = orig_cmap(np.linspace(0, 1, 256))
    colors[:, -1] = 0.4                              
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
        label='Electrification Index'
    )


                        
    cbar.ax.patch.set_facecolor('lightgrey')
    cbar.outline.set_edgecolor('none')
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Electrification Index', fontsize=18, labelpad=20)
    cbar.locator = LinearLocator(6)              
    cbar.formatter = FuncFormatter(lambda val, _pos: f"{val:.2f}")
    cbar.update_ticks()
                                                                                            
                
                 
    edges = [0, 10, 100, 500]                               
                       
    gwh_knots   = [10, 100, 500]
    width_knots = [1.0, 2.0, 3.0]

    style_group = {
        "pv": {"color": "#980800", "linestyle": "-.", "label": "PV"},
        "wt": {"color": "#0E1C5C", "linestyle": "-.", "label": "WT"},
    }

    symbol_pv = r"P^{\mathrm{City,PV}}_{i^\prime,j}"
    symbol_wt = r"P^{\mathrm{City,WT}}_{i^\prime,j}"

    def interval_label(symbol, left, right, cnt, idx):
                                
                                      
        if idx == 0:
            expr = rf"{symbol} < {right}"
        else:
            expr = rf"{left} < {symbol} \leq {right}"
        return rf"${expr}$  (n={cnt})"

                
    endpoints = []
    def draw_city_lines(sheet, key):
        df = (pd.read_excel(tns_yr_path, sheet_name=sheet)
                .dropna(subset=["Longitude_1","Latitude_1","Longitude_2","Latitude_2","Value"]))
        vals = df["Value"].astype(float)
        widths = np.interp(vals, gwh_knots, width_knots)

        pts1 = gpd.GeoSeries(gpd.points_from_xy(df.Longitude_1, df.Latitude_1), crs="EPSG:4326").to_crs(epsg=2343)
        pts2 = gpd.GeoSeries(gpd.points_from_xy(df.Longitude_2, df.Latitude_2), crs="EPSG:4326").to_crs(epsg=2343)

                           
        for lon, lat in zip(df.Longitude_1, df.Latitude_1):
            endpoints.append((round(lon,6), round(lat,6)))
        for lon, lat in zip(df.Longitude_2, df.Latitude_2):
            endpoints.append((round(lon,6), round(lat,6)))

        cfg = style_group[key]
        first = True
        for p1, p2, lw in zip(pts1, pts2, widths):
            ax.plot([p1.x,p2.x],[p1.y,p2.y],
                    color=cfg["color"], linestyle=cfg["linestyle"],
                    linewidth=lw, alpha=0.7,
                    label=cfg["label"] if first else "_nolegend_",
                    zorder=2.5)
            first = False

    draw_city_lines("U_PV_city", "pv")
    draw_city_lines("U_WT_city", "wt")

    endpoint_set = set(endpoints)

    def load_and_filter(el):
        base = r"E:\2025_Methanol_synthesis\3_GAMS\P3_Geographical_allocation\pycode"
        wo = os.path.join(base, "Cities_wo_MeOH_with_coords.csv")
        w = os.path.join(base, "Cities_w_MeOH_with_coords.csv")
        df_wo = pd.read_csv(wo, encoding='utf-8').dropna(subset=['Longitude','Latitude'])
        df_w = pd.read_csv(w, encoding='utf-8').dropna(subset=['Longitude','Latitude'])
                                                          
        df_wo['coord'] = df_wo.apply(lambda r: (round(r.Longitude,6), round(r.Latitude,6)), axis=1)
        df_w['coord'] = df_w.apply(lambda r: (round(r.Longitude,6), round(r.Latitude,6)), axis=1)
        df_wo = df_wo[df_wo['coord'].isin(endpoint_set)]
        df_w = df_w[df_w['coord'].isin(endpoint_set)]

                              
        gdf_wo = gpd.GeoDataFrame(df_wo,
        geometry=gpd.points_from_xy(df_wo.Longitude, df_wo.Latitude), crs="EPSG:4326").to_crs(epsg=2343)
        gdf_w = gpd.GeoDataFrame(df_w,
        geometry=gpd.points_from_xy(df_w.Longitude, df_w.Latitude), crs="EPSG:4326").to_crs(epsg=2343)
        return gdf_wo, gdf_w

                                         
    gdf_wo, gdf_w = load_and_filter(el)
                                  
    gdf_wo.plot(ax=ax, marker='o', markersize=15, color='grey', edgecolor='black', label='City w/o MeOH', zorder=4)
    gdf_w.plot(ax=ax, marker='o', markersize=15, color='white', edgecolor='grey', label='City w/ MeOH', zorder=4)


                            
    pv_vals = pd.read_excel(tns_yr_path, sheet_name="U_PV_city")["Value"].astype(float)
    wt_vals = pd.read_excel(tns_yr_path, sheet_name="U_WT_city")["Value"].astype(float)
    pv_counts, _ = np.histogram(pv_vals, bins=edges)
    wt_counts, _ = np.histogram(wt_vals, bins=edges)

               
    all_handles, all_labels = [], []
    for key, counts, symbol in [
        ("pv", pv_counts, symbol_pv),
        ("wt", wt_counts, symbol_wt),
    ]:
        cfg = style_group[key]
        for i, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
                   
            all_handles.append(
                Line2D([0], [0],
                    color=cfg["color"],
                    linestyle=cfg["linestyle"],
                    linewidth=width_knots[i])
            )
                    
            if i == 0:
                expr = rf"{symbol} \leq {right}"
            else:
                expr = rf"{left} < {symbol} \leq {right}"
            all_labels.append(rf"${expr}$")

                        
    leg = ax.legend(
        handles=all_handles,
        labels=all_labels,
        title="Intra-provincial municipal annual transmission (GWh)",
        loc="lower left",
        frameon=False,
        fontsize=11,
        title_fontsize=13,
        bbox_to_anchor=(-0.2, 0.30),
        ncol=2,
        labelspacing=0.2
    )
    ax.add_artist(leg)


                                                       
    filename = f"Map_EL_{el}_{year}_ED{ed}_City.png"
    out_path = os.path.join(out_dir, filename)
    fig.canvas.draw()
    fig.savefig(out_path, dpi=300)
    print(f"Saved:{out_path}")

if __name__ == "__main__":
    for cfg in runs:
        plot_map(el=el, year=cfg["year"], ed=cfg["ed"])