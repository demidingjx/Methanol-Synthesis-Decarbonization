import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
plt.rcParams.update({'font.size': 20})
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator  # 放在文件开头
import matplotlib.lines as mlines


# ─── 全局颜色定义 ─────────────────────────────
COLORS = {
# Capacity colors
'PV': '#a30543',
'WT': '#FBDA83',
'LiB': '#F36F43',
'PEM': "#0093a3", # PEM自身
'HST': '#75bbc3',
'SOE': '#c2a1db',
'SST': "#A0579CB2",
# Energy colors
'Grid': '#4965B0',
}

# ─── 1. 路径 & 文件 ──────────────────────────────
base = Path(r"E:\2025_Methanol_synthesis\3_GAMS\P4_Sensitivity_Analysis\excel")
paths = {
    "PEM": base / "PEM" / "Scenario_Summary_PEM_HST.xlsx",
    "SOE": base / "SOE" / "Scenario_Summary_SOE_SST.xlsx",  # <- 这里的键必须是 "SOE"
}

lcom_leg = None
LCCR_leg = None
# ─── 2. 读取 Scenario & Energy ────────────────────
scenario_order = ["LSC", "HSC", "LTN_PEP","HTN_NEP",
                       "PEP", "NEP", "LTN", "HTN", "LRE_LEL",
                        "HRE_HEL", "LEL", "HEL", "LRE", "HRE",  "BLN",
                    ]
data = {}
for tech, pth in paths.items():
    # 确保第一列是 “Scenario”，直接当索引
    df_cap    = pd.read_excel(pth, sheet_name="Scenario", index_col=0)
    df_energy = pd.read_excel(pth, sheet_name="Energy",   index_col=0)
    df_cap    = df_cap.reindex(scenario_order)
    df_energy = df_energy.reindex(scenario_order)
    data[tech] = (df_cap, df_energy)
    print("Loaded data keys:", data.keys())
 # ─── 3. 建立 2×2 子图 ─────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(18, 14),
                            sharey='row', sharex='col')
display_labels = [sc.replace("_","-") for sc in scenario_order]
for row, tech in enumerate(["PEM", "SOE"]):
    df_cap, df_energy = data[tech]
    ax = axes[row, 0]
    saved_xlim_main = None
    saved_xlim_top  = None
    # 左图：Capacity (GW)
    cap_cols = ["PV", "WT", "LiB", tech, "HST"] if tech=="PEM" else ["PV", "WT", "LiB", tech, "SST"]
    cap_colors = [COLORS[c] for c in cap_cols]
    df_cap[cap_cols].plot.barh(
        stacked=True, ax=ax, color=cap_colors, edgecolor="none", legend=False
    )
    ax.set_yticklabels(display_labels)
    ax.set_xlim(0, 800)
    ax.xaxis.set_major_locator(MultipleLocator(200))
    ax_top = ax.twiny()
    ax_top.xaxis.set_major_locator(MultipleLocator(100))

    y_locs = ax.get_yticks()
    lcoms  = pd.read_excel(paths[tech], sheet_name="Metrics", index_col=0).loc[df_cap.index, "LCOM"].values

    if row == 0:
        # 第一行：用上轴显示散点，隐藏下轴刻度
        lcom_leg = ax_top
        ax_top.scatter(lcoms, y_locs, color="#000000", marker="o", label="LCOM")
        ax_top.set_xlabel("LCOM (2025 USD/ton)", labelpad=10)
        ax.tick_params(direction='in')
        ax.xaxis.set_tick_params(labelbottom=False)
        ax_top.set_xlim(400, 750)
        ax_top.axvline(482.05, color="gray", linestyle="--", linewidth=2)        
        saved_xlim = ax_top.get_xlim()
        ax.set_xlim(saved_xlim_main)
    else:
        # 第二行：在本轴底部画散点
        ax.scatter(lcoms, y_locs, color="#000000", marker="o", label="LCOM")
        ax.set_xlabel("Capacity (GW)", labelpad=10)
        ax_top.set_xticks([])
        ax_top.set_xlim(saved_xlim)
        ax_top.xaxis.label.set_visible(False)
        ax.tick_params(direction='in')

    ax_top.axvline(482.05, color="gray", linestyle="--", linewidth=2)
    display_labels = [sc.replace("_","-") for sc in scenario_order]
    ax.set_yticklabels(display_labels)
    ax_top.set_yticklabels(display_labels)
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.xaxis.label.set_size(26)
    ax_top.xaxis.label.set_size(26)
    # 右图：Energy (TWh)
    # 这里假设 Energy 表里有 PV、WT、Grid、PEM 或 SST 四个列
    energy_cols = ["PV", "WT", "Grid"]
    eng_colors = [COLORS[c] for c in energy_cols]
    ax2 = axes[row, 1]
    df_energy[energy_cols].plot.barh(
        stacked=True, ax=ax2, color=eng_colors, edgecolor="none", legend=False
    )
    
    ax2.set_xlim(0, 1500)
    ax2.xaxis.set_major_locator(MultipleLocator(300))
 #   ax2.axvline(0, color="black", linestyle="--", linewidth=2)
    y_locs2 = ax2.get_yticks()
    LCCRs  = pd.read_excel(paths[tech], sheet_name="Metrics", index_col=0).loc[df_energy.index, "LCCR"].values
    soe_metrics = pd.read_excel(paths["SOE"], sheet_name="Metrics", index_col=0)

    # 打印出所有 Scenario 的 LCCR 数值
    print("—— SOEC (SST) LCCR values ——")
    print(soe_metrics["LCCR"])
    if row == 0:
        # 第一行：用上轴显示 LCCR，隐藏本轴下刻度
        ax2_top = ax2.twiny()
        ax2_top.set_xlim(-50, 100)
        ax2_top.xaxis.set_major_locator(MultipleLocator(50))           
        LCCR_leg = ax2_top
        ax2_top.scatter(LCCRs, y_locs2, color="#000000", marker="x", label="LCCR")
        ax2_top.set_xlabel("LCCR (2025 USD/ton CO₂)", labelpad=10)
#        ax2_top.axvline(0, color="gray", linestyle="--", linewidth=2)
        ax2.xaxis.set_tick_params(labelbottom=False)
        display_labels = [sc.replace("_","-") for sc in scenario_order]
        ax2.set_yticklabels(display_labels)
        ax2_top.tick_params(direction='in')

    else:
        # 第二行：在本轴底部画 LCCR
        ax2.scatter([], [])  # 不在主轴画 scatter
        ax2.set_xlabel("Energy Consumption (TWh)", labelpad=10)
        display_labels = [sc.replace("_","-") for sc in scenario_order]
        ax2.set_yticklabels(display_labels)
        ax2.tick_params(direction='in')
        # 再创建一个上轴用来定位散点，但不显示刻度标签
        ax2_top2 = ax2.twiny()
        ax2_top2.scatter(LCCRs, y_locs2, color="#000000", marker="x", label="LCCR")
        # 对齐到右上那条轴的范围
        ax2_top2.set_xlim(-50, 100)
        ax2_top2.xaxis.set_major_locator(MultipleLocator(50))
        # 隐藏这个上轴的所有刻度标签，只留刻度线（可选）
        ax2_top2.tick_params(axis='x', labeltop=False, labelbottom=False)
#        ax2_top2.axvline(0, color="gray", linestyle="--", linewidth=2)
        display_labels = [sc.replace("_","-") for sc in scenario_order]
        ax2_top2.set_yticklabels(display_labels)

    ax2.set_ylabel("")
    ax2.grid(axis="x", linestyle="--", alpha=0.5)
    ax2.xaxis.label.set_size(26)
    ax2_top.xaxis.label.set_size(26)
# ─── 4. 顶部合并图例 ───────────────────────────────
tech_h,  tech_l  = axes[0,0].get_legend_handles_labels()
lcom_h,  lcom_l  = lcom_leg.get_legend_handles_labels()
LCCR_h, LCCR_l = LCCR_leg.get_legend_handles_labels()
# ─── 新增：Grid 的 proxy handle ───────────────────────
grid_color = "#4965B0"                  # 要和你 plot.barh 时的灰色保持一致
grid_patch = Patch(color=grid_color, label="Grid")
soe_patch = Patch(color="#c2a1db", label="SOE")   # 与 capacity/energy 中 tech 颜色一致
sst_patch = Patch(color="#A0579CB2", label="SST")   # 与 capacity 中 HST/SST 颜色一致

tech_h, tech_l = axes[0,0].get_legend_handles_labels()
energy_h, energy_l = axes[0,1].get_legend_handles_labels()
all_h = tech_h + [grid_patch, soe_patch, sst_patch] + lcom_h + LCCR_h
all_l = tech_l + ["Grid", "SOE", "SST"]            + lcom_l + LCCR_l
all_l = [lbl.replace("PEM", "PEME").replace("SOE", "SOEC") for lbl in all_l]
baseline_line = mlines.Line2D([], [], color='gray', linestyle='--', linewidth=2, label='BAU LCOM')
all_h += [baseline_line]
all_l += ['BAU LCOM']

fig.legend(
    all_h, all_l,
    ncol= 6,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.005),
    fontsize=24,
    frameon=False      # ← 这一行关闭边框
)
# ─── 5. 左侧纵向大标题 PEM/SOE ────────────────────
fig.text(0.02, 0.685, "PEME", va="center", ha="center",
          rotation="vertical", fontsize=36, fontweight='bold')
fig.text(0.02, 0.30, "SOEC", va="center", ha="center",
          rotation="vertical", fontsize=36, fontweight='bold')
# ─── 6. 底部统一标签 Capacity / Energy ────────────
#fig.text(0.35, 0.03, "Capacity", ha="center", va="center", fontsize=18)
#fig.text(0.75, 0.03, "Energy",  ha="center", va="center", fontsize=18)

LCCR_leg.set_xlim(-50, 100)          # 右上上轴 Cost LCCR

plt.tight_layout(rect=[0.04, 0.04, 0.99, 0.93])


for ax in fig.axes:
    ax.tick_params(axis='both', which='both',
                   direction='in',
                   top=True, bottom=True,
                   left=True, right=False)


# ─── 6. 保存图形 ─────────────────────────────────
out_dir = base.parent / "fig"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "capacity_energy_2x2.png"
fig.savefig(out_path, dpi=1000)
print(f"Figure saved to: {out_path}")
