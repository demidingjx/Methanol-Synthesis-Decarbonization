import subprocess
import re
from pathlib import Path

# 1. GAMS 可执行程序全路径
GAMS_EXE = r"D:\GAMS\48\gams.exe"
#GAMS_EXE = r"D:\GAMS\48\48\gams.exe"
# 2. 场景列表
scenarios = [
    "HEL", "LEL", "HRE", "LRE",
    "HRE_HEL", "LRE_LEL", "HTN", "LTN",
    "NEP", "PEP", "HTN_NEP", "LTN_PEP",
    "HSC", "LSC", "BLN"
]

# 3. GMS 模板路径
template_path = Path(
    r"F:\2025_Methanol_synthesis\3_GAMS\P4_Sensitivity_Analysis\gdx\Installation_ratio.gms"
)

# 4. 读取所有行
lines = template_path.read_text(encoding="utf-8").splitlines(keepends=True)

# 5. 准备输出目录（和模板同目录）
out_dir = template_path.parent
out_dir.mkdir(exist_ok=True)

# 6. 正则：匹配 "$Set" + 空白 + "Sens" + 空白 + “任意非空白字符”
pattern = re.compile(r'(\$Set\s+Sens\s+)\S+', re.IGNORECASE)

for scenario in scenarios:
    # 用正则对每一行做替换
    new_lines = [
        pattern.sub(r'\1' + scenario, ln)
        for ln in lines
    ]

    # （可选）打印一下确认替换正确
    # 找到那一行并打印
    for ln in new_lines:
        if ln.lstrip().startswith('$Set') and 'Sens' in ln:
            print(f"{ln.strip()}")
            break

    # 写出新的 .gms 文件
    out_gms = out_dir / f"Installation_ratio_{scenario}.gms"
    out_gms.write_text("".join(new_lines), encoding="utf-8")

    # 调用 GAMS
    print(f"Running scenario: {scenario} …")
    proc = subprocess.run(
        [GAMS_EXE, str(out_gms)],
        cwd=str(template_path.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        print(f"Scenario {scenario} failed (exit code {proc.returncode}):\n{proc.stderr}")
    else:
        print(f"Scenario {scenario} succeeded. Output: {out_gms.stem}.lst")

print("All scenarios processed.")
