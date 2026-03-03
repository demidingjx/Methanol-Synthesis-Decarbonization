import subprocess
import re
from pathlib import Path

# 1) GAMS 可执行程序
GAMS_EXE = r"D:\GAMS\48\gams.exe"

# 2. 年份与对应的 ED 列表
year_ed_map = {
    2030: [25, 50, 75, 100],
    2040: [25, 21, 50, 75, 100],
    2050: [25, 50, 59, 75, 100],
}

# 3. 模板 GMS 路径
template_path = Path(
    r"F:\2025_Methanol_synthesis\3_GAMS\P2_Cost_vs_ED\gdx_processing\Total_cost\Total_Cost_breakdown_SOE_gdx_CAP.gms"
)
#C_cost_breakdown_SOE
#P_cost_breakdown_SOE
#Total_Cost_breakdown_SOE_gdx_CAP

# 4. 读取模板内容一次
orig_lines = template_path.read_text(encoding="utf-8").splitlines(keepends=True)

# 5. 输出目录（同模板目录）
out_dir = template_path.parent
out_dir.mkdir(exist_ok=True)

# 正则
re_set_yr  = re.compile(r'^\s*\$Set\s+YR\b.*$', re.IGNORECASE)
re_set_ed  = re.compile(r'^\s*\$Set\s+ED\b.*$', re.IGNORECASE)
re_set_doi = re.compile(r'^\s*\$Set\s+DOI\b.*$', re.IGNORECASE)

for yr, ed_list in year_ed_map.items():
    for ed in ed_list:
        doi_val = f"{ed/100:.2f}"   # 25->0.25, 57->0.57, 100->1.00

        new_lines = []
        found_yr = found_ed = found_doi = False
        ed_line_idx = None

        for idx, ln in enumerate(orig_lines):
            if re_set_yr.match(ln):
                new_lines.append(f"$Set YR  {yr}\n")
                found_yr = True
            elif re_set_ed.match(ln):
                new_lines.append(f"$Set ED  ED{ed}\n")
                found_ed = True
                ed_line_idx = len(new_lines) - 1
            elif re_set_doi.match(ln):
                new_lines.append(f"$Set DOI  {doi_val}\n")
                found_doi = True
            else:
                new_lines.append(ln)

        # 若模板未包含 $Set DOI，则在 $Set ED 之后插入
        if not found_doi:
            insert_idx = (ed_line_idx + 1) if ed_line_idx is not None else 0
            new_lines.insert(insert_idx, f"$Set DOI  {doi_val}\n")

        # 若模板未包含 $Set YR/ED，也补写到文件开头
        header_inserts = []
        if not found_yr:
            header_inserts.append(f"$Set YR  {yr}\n")
        if not found_ed:
            header_inserts.append(f"$Set ED  ED{ed}\n")
        if header_inserts:
            new_lines = header_inserts + new_lines

        # 生成输出文件名（按需改成 SOE 或 SOE）
        out_gms = out_dir / f"Total_Cost_SOE_YR{yr}_ED{ed}.gms"
        out_gms.write_text("".join(new_lines), encoding="utf-8")

        # 打印前 10 行确认
        print(f"--- {out_gms.name} 前 10 行 ---")
        for line in new_lines[:10]:
            print(line.rstrip())
        print("--------------------------")

        # 运行 GAMS
        print(f"运行 YR={yr}, ED={ed}, DOI={doi_val} …")
        proc = subprocess.run(
            [GAMS_EXE, str(out_gms)],
            cwd=str(out_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(proc.stdout, proc.stderr)
        if proc.returncode != 0:
            print(f" YR={yr}, ED={ed} 失败 (exit code {proc.returncode})")
        else:
            print(f" YR={yr}, ED={ed} 完成")

print("所有组合执行完毕。")
