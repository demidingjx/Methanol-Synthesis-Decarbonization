library(openxlsx)
library(circlize)
library(viridis)
library(glue)

# —————— 用户可调参数 ——————
# 年份、ED 深度
years <- c(2040, 2050)
eds   <- c(21, 25, 50, 55, 59, 76, 75, 100)

# 电解槽类型 和 绘图模式
els <- c("PEM","SOE")

# 省份缩写顺序
zx <- c("EC", "HC", "NC", "SW", "NE", "NW", "SC")

# Viridis 配色（给所有 zx 分配颜色）
viridis_colors <- viridis(length(zx))
grid_colors <- setNames(viridis_colors, zx)

# 文件路径与 sheet
file_tpl   <- "E:/2025_Methanol_synthesis/3_GAMS/P3_Geographical_allocation/Results_new/{el}/{year}/ED{ed}/TNS_yr_{el}_{year}_ED{ed}_2s.xlsx"
sheet_name <- "matr_Region"

# 输出文件
output_tpl <- "E:/2025_Methanol_synthesis/3_GAMS/P3_Geographical_allocation/fig/{el}_Region_{year}_ED{ed}.png"

# —————— 批量循环 ——————
for(el in els) {
  for(year in years) {
    for(ed in eds) {
      # 构造路径和输出
      file_path  <- glue(file_tpl, el=el, year=year, ed=ed)
      out_png     <- glue(output_tpl, el=el, year=year, ed=ed)
      
      # 如果文件或 sheet 不存在则跳过
      if(!file.exists(file_path)) {
        warning("文件不存在，跳过：", file_path)
        next
      }
      sheets <- openxlsx::getSheetNames(file_path)
      if(! sheet_name %in% sheets) {
        warning("找不到 sheet，跳过：", file_path, "::", sheet_name)
        next
      }
      
# 读取数据
      mat <- read.xlsx(file_path, sheet = sheet_name, rowNames = TRUE)
      mat <- as.matrix(mat)
      
# 筛选出 zx 中实际参与的行列
      valid_rows <- intersect(rownames(mat), zx)
      valid_cols <- intersect(colnames(mat), zx)
      mat <- mat[valid_rows, valid_cols]
      
# 转长表 + 只保留非 0
      df_long <- as.data.frame(as.table(mat))
      colnames(df_long) <- c("from", "to", "value")
      df_long <- df_long[df_long$value != 0,]
      
# 有效节点绘图顺序（从 zx 中筛出）
      region_in_data <- union(df_long$from, df_long$to)
      region_order <- zx[zx %in% region_in_data]
      grid_col_final <- grid_colors[region_order]
      
# ———— 显示图像 ————
      png(out_png, width = 2500, height = 2500, res = 1000)
      par(cex=0.55, lwd=0.8, oma=c(0.5, 0.5, 0.5, 0.5), mar=c(0.1, 0.1, 0.1, 0.1))
      chordDiagram(df_long,
                   order = region_order,
                   grid.col = grid_col_final,
                   directional = 1,
                   direction.type = c("diffHeight","arrows"),
                   link.arr.type = "big.arrow")
      circos.clear()
      dev.off()
      
      message("完成：", el, " Region ", year, " ED", ed)
    }
  }
}
