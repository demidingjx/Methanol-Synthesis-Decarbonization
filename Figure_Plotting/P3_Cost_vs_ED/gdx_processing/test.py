from pathlib import Path

template_path = Path(
    r"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\gdx_processing\Total_cost\Total_Cost_breakdown_SOE_gdx_CAP.gms"
)
print(">>> 模板绝对路径：", template_path.resolve())

lines = template_path.read_text(encoding="utf-8").splitlines(keepends=True)
print("--- 模板文件前 10 行（Python 读入）---")
for ln in lines[:10]:
    print(ln.rstrip())
print("-------------------------------------")
