# TamperShield 开发冲刺看板

## 🏁 阶段一：基础流水线搭建 (MVP)
- [x] 搭建项目核心基础骨架 (目录树与依赖)
- [x] 实现基于 OpenCV 的红黑分离 (去除红色印章干扰)
- [x] 接入 PP-Structure 引擎提取扫描件表格为 HTML/DataFrame
- [x] 接入 pdfplumber 提取原生 PDF 基准表格
- [x] 实现基于 Pandas 的 `ffill` 合并单元格展开与主键对齐
- [x] 实现基于 Levenshtein 编辑距离的文本容错比对机制

## 🚧 阶段二：鲁棒性与工程强化 (Current)
- [ ] **(当前任务)** 在 `core/pre_processing.py` 中增加 OpenCV 倾斜检测与自动校正 (Deskew)，防止 PP-Structure 表格线识别崩溃。
- [ ] 实现跨页表格的 DataFrame 自动缝合逻辑 (处理没有表头的续页表格拼接)。

## 🚀 阶段三：商业级特性 (Future)
- [ ] 支线任务：印章与签名区域特征提取及真伪核验。
- [ ] 前端可视化开发：支持双屏 Diff 连线高亮展示差异报告。