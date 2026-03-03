import pandas as pd
from pathlib import Path

def build_matrix(el, year, ed, drop_type):
    """
    Read the U_prov sheet for the given parameters,
    drop rows where Type == drop_type,
    pivot Prov_jx×Prov into a matrix (missing→0), and
    save alongside the source file with drop_type in its name.
    """
    el_up     = el.upper()
    drop_type = drop_type.upper()
    
                     
    base_dir  = Path(r"D:\2025_Methanol_synthesis\GAMS\P3_Geographical_allocation\Results_new")
    file_name = f"TNS_yr_{el_up}_{year}_ED{ed}_2s.xlsx"
    file_path = base_dir / el_up / str(year) / f"ED{ed}" / file_name
    
                                          
    out_name = f"{file_path.stem}_matr_{drop_type}.xlsx"
    out_path = file_path.parent / out_name
    
                     
    df = pd.read_excel(file_path, sheet_name="U_prov")
    df = df[df["Type"].str.upper() != drop_type]
    
                     
    mat = (
        df
        .pivot(index="Prov_jx", columns="Prov", values="Value")
        .fillna(0)
    )
    
          
    mat.to_excel(out_path)
    print(f"Saved matrix to: {out_path}")
    
    return mat

if __name__ == "__main__":
                               
    el        = "SOE"              
    year      = 2050
    ed        = 50
    drop_type = "AC"              
    
    matrix = build_matrix(el, year, ed, drop_type)
    print(matrix)
