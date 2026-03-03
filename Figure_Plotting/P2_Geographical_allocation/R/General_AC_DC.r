library(openxlsx)
library(circlize)
library(viridis)
library(glue)

# —————— 用户可调参数 ——————
# 年份、ED 深度
years <- c(2050)
eds   <- c(25)
#50, 55, 59, 76, 75, 100
# 电解槽类型 和 绘图模式
els <- c("SOE")
lns <- c("DC")

# 省份缩写顺序
zx <- c( "SC","GX", "GS", "HL", "HI", "AH","SD","QH","NX","HB", "JL", "SN","XJ","HN",   
          "YN", "SX","JS","ZJ", "WIM", "SH", "JX","HU", "TJ",
          "CQ", "GZ","EIM","LN" )

# Viridis 配色（给所有 zx 分配颜色）
viridis_colors <- viridis(length(zx))
grid_colors <- setNames(viridis_colors, zx)
# 文件路径模板：*.xlsx
file_tpl  <- "E:/2025_Methanol_synthesis/3_GAMS/P3_Geographical_allocation/Results_new/{el}/{year}/ED{ed}/TNS_yr_{el}_{year}_ED{ed}_2s.xlsx"
# sheet 名称模板
sheet_tpl <- "matr_{ln}"
# 输出图片模板
output_tpl <- "E:/2025_Methanol_synthesis/3_GAMS/P3_Geographical_allocation/fig/{el}_{ln}_{year}_ED{ed}.png"

# —————— 批量循环 ——————
for(el in els){
  for(year in years){
    for(ed in eds){
      for(ln in lns){
        # 构造路径和 sheet 名称
        file_path  <- glue(file_tpl,  el=el, year=year, ed=ed)
        sheet_name <- glue(sheet_tpl,  ln=ln)
        out_png    <- glue(output_tpl, el=el, ln=ln, year=year, ed=ed)
        
        # —— 文件存在性检查 —— 
        if (!file.exists(file_path)) {
          message("File not found, skipping: ", file_path)
          next
        }
        # —— Sheet 存在性检查 —— 
        sheets <- openxlsx::getSheetNames(file_path)
        if (!sheet_name %in% sheets) {
          message("Sheet not found, skipping: ", sheet_name, " in ", basename(file_path))
          next
        }
        
        
        # 读数据
        mat <- read.xlsx(file_path, sheet = sheet_name, rowNames = TRUE)
        mat <- as.matrix(mat)

# 筛选出 zx 中实际参与的行列
        valid_rows <- intersect(rownames(mat), zx)
        valid_cols <- intersect(colnames(mat), zx)
        mat <- mat[valid_rows, valid_cols]
        
# 转长表 + 只保留非 0
        df_long <- as.data.frame(as.table(mat))
        colnames(df_long) <- c("from", "to", "value")
        df_long <- df_long[df_long$value != 0, ]
        
        # —— 识别当前区域 & 计算权重 —— 
        # 1) 当前参与的区域（保持 zx 的顺序）
        regions    <- zx[zx %in% union(df_long$from, df_long$to)]
        orig_order <- regions
        
        # 2) 计算每个区域的原始进出流量总和
        raw_w <- setNames(numeric(length(regions)), regions)
        for(r in regions){
          if(r %in% rownames(mat))   raw_w[r] <- raw_w[r] + sum(mat[r, ], na.rm=TRUE)
          if(r %in% colnames(mat))   raw_w[r] <- raw_w[r] + sum(mat[, r], na.rm=TRUE)
        }
        
        # 3) 先打印 raw_w，看看都是哪些值
        message("---- 原始进出流量总和 ----")
        for(r in regions){
          message(r, ": ", raw_w[r])
        }
        
        # 4) 用一个你能控制的“绝对阈值”来划三组
        tiny_thr  <- 0.12    # 你自己根据实际数据调试
        large_thr <- 0.3
        
        groupTiny  <- regions[raw_w  <  tiny_thr]
        groupLarge <- regions[raw_w >= large_thr]
        groupMid   <- setdiff(regions, c(groupTiny, groupLarge))
        
        # 5) 再打印分组结果，确认没问题
        message("Tiny (<",  tiny_thr, "): ", paste(groupTiny, collapse=", "))
        message("Large (≥", large_thr, "): ", paste(groupLarge, collapse=", "))
        message("Mid:              ", paste(groupMid,   collapse=", "))
        
        # 6) 插入逻辑：大扇区优先，每遇到 Large/Mid 都尝试插入一个 tiny
        tiny_q    <- groupTiny
        new_order <- character(0)
        
        for(sec in orig_order) {
          # 先把当前扇区放进去（无论 Large 还是 Mid）
          new_order <- c(new_order, sec)
          
          # 如果是 Large，马上插一个 tiny
          if(sec %in% groupLarge && length(tiny_q) > 0) {
            new_order <- c(new_order, tiny_q[1])
            tiny_q    <- tiny_q[-1]
            
            # 否则如果是 Mid，也插一个 tiny（优先补剩余 tiny）
          } else if(sec %in% groupMid && length(tiny_q) > 0) {
            new_order <- c(new_order, tiny_q[1])
            tiny_q    <- tiny_q[-1]
          }
          # orig_order 中的 tiny 本身不先放
        }
        
        # 7) 最后把还没插完的 tiny 全部补到末尾
        if(length(tiny_q) > 0) {
          new_order <- c(new_order, tiny_q)
        }
        
        # 8) 结果赋值
        region_order   <- new_order
        grid_col_final <- grid_colors[region_order]
        message("Final order: ", paste(region_order, collapse=", "))
        
        
        # 绘制并保存
        png(out_png, width = 2500, height = 2500, res = 900)
        par(cex = 0.55, lwd = 0.8)
        par(oma = c(0.5, 0.5, 0.5, 0.5), mar = c(0.1, 0.1, 0.1, 0.1))
        
        chordDiagram(df_long,
                     order = region_order,
                     grid.col = grid_col_final,
                     directional = 1,
                     direction.type = c("diffHeight", "arrows"),
                     link.arr.type = "big.arrow")
        dev.off()
        circos.clear()
        
        message("Done: ", el, "-", ln, "-", year, "ED", ed)
      }
    }
  }
}
