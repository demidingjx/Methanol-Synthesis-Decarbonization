import subprocess
import re
from pathlib import Path

                  
GAMS_EXE = r"D:\GAMS\48\48\gams.exe"

                
                                      
ed_points = [25, 55, 50, 76, 75, 100]

             
template_path = Path(
    r"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\gdx\Individual_City_LCOM_PEM.gms"
)

          
lines = template_path.read_text(encoding="utf-8").splitlines(keepends=True)

                          
pattern = re.compile(r'(\$Set\s+ED\s+)ED\d+', re.IGNORECASE)

                
out_dir = template_path.parent
out_dir.mkdir(exist_ok=True)

for ed in ed_points:
                    
    new_lines = [
        pattern.sub(r'\1ED{}'.format(ed), ln)
        for ln in lines
    ]

                    
    for ln in new_lines:
        if ln.lstrip().startswith('$Set') and 'ED' in ln:
            print(f"替换后：{ln.strip()}")
            break

                     
    out_gms = out_dir / f"LCOM_city_indi_ED{ed}.gms"
    out_gms.write_text("".join(new_lines), encoding="utf-8")

                
    print(f"Running ED = {ed} …")
    proc = subprocess.run(
        [GAMS_EXE, str(out_gms)],
        cwd=str(out_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        print(f"ED={ed} 失败 (exit code {proc.returncode})：\n{proc.stderr}")
    else:
        print(f"ED={ed} 完成，输出：{out_gms.stem}.lst")

print("所有 ED 点均已处理完毕。")


