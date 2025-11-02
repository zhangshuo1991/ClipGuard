# ClipGuard 工作计划与日志

## 已执行计划
- 扩展数据库与 UI：新增收藏/回收站字段，完善筛选、搜索同步与回收站恢复/彻底删除流程。
- “最近”视图完善：引入 24 小时窗口，实时刷新导航计数并对齐类型映射。
- 设置面板重构：按 React 设计拆分监控、存储、隐私等分组；支持导入/导出、恢复默认与排除应用；同步主窗口监控开关。
- 分类逻辑增强：基于扩展名识别图片、文档、压缩包等类型，保持筛选兼容。
- UI 打磨：加托盘最小化、列表/详情双 `QSplitter` 可拖动；侧栏收缩显示自定义图标。
- 品牌资源：设计 SVG/PNG Logo，生成 `.iconset`/`.icns`，为 PyInstaller 打包接入。

## 关键命令日志
- 代码检视与编译：`python -m compileall …` 多次验证修改。
- 数据调试：`sqlite3 ~/.clipguard/clipboard.db 'SELECT …'` 检查现有条目。
- 资源生成：使用 Pillow 生成 `assets/clipguard-logo.png`、`assets/clipguard.iconset`，`sips` 转换 `icns`。
- 构建脚本：`python build.py`（需预先安装 `pyinstaller`），`iconutil -c icns …`、`pyinstaller ClipGuard.spec`（说明中给出）。
- 目录/文件管理：`mkdir -p docs`、`ls assets/icons` 等确认资源位置。

## 产出文件
- `assets/clipguard-logo.svg` / `assets/clipguard-logo.png`
- `assets/clipguard.icns`（供 macOS 打包）
- `docs/work_log.md`（本日志）
- 更新的 `build.py`、`ClipGuard.spec`、`ui/main_window.py`、`ui/components/sidebar.py`、`ui/styles.py` 等

## 对话摘要（压缩）
- 明确仓库规则：中文沟通、改代码前需列计划；逐步实现剪贴板收藏/回收站、托盘隐藏等需求。
- 追踪剪贴板问题并加调试日志；修复设置弹窗常量、同步顶部/侧栏搜索，完善过滤逻辑。
- 讨论文件分类、图片识别与扩展名映射，逐渐扩展到文档/压缩包等类型。
- 实现设置页大幅改版、侧栏拖拽、回收站恢复删除；解决 Qt 样式警告、分隔条手柄提示。
- 生成品牌 Logo、配置打包脚本、指导 macOS `.app` 打包流程；引入自定义 SVG 图标美化侧栏。
