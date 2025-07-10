# mantou-earth-server

该仓库使用Github Actions自动下载Mantou Earth所需要的图片到Pictures分支。

需要配置2个仓库变量：

1. RESOLUTIONS：逗号分隔的分辨率列表（如 2160,1440,1080）
2. KEEP_DAYS：图片保留天数（可选，默认1天）

> 根目录中的prompt.txt为AI提示词，cron.js为cloudflare worker定时任务脚本，用于action精确定时。
> 
> 使用该定时脚本需要配置2个变量：GITHUB_REPO(yaml工作流对应的GitHub查看链接，去除GitHub.com前面的部分，例：sakurasep/qfnuLibraryBook/actions/workfIows/tomorrow.yml)、GITHUB_PAT(GitHub个人访问令牌,需要repo权限)。

## 项目说明

### 关键功能说明：

1. **自动时间计算**：
   - 获取当前UTC时间减去30分钟（处理延迟）
   - 分钟数向下取整到最近的10分钟（如08:37 → 08:30）
   - 生成路径所需变量：`2025-07-01`（目录）和 `0310`（文件名部分）

2. **分辨率处理**：
   - 从环境变量 `RESOLUTIONS` 读取多个分辨率
   - 自动计算最佳 `d` 值（分辨率倍数）：`d = round(分辨率 / 550)`
   - 限制 `d` 值在 1-20 范围内

3. **图片处理流程**：
   - 下载所有分块图片（`d x d` 网格）
   - 使用 ImageMagick 的 `montage` 拼接图片
   - 转换为 WebP 格式（85% 质量平衡大小和质量）
   - 保存路径格式：`/2025-07-01/0310_2160.webp`

4. **自动清理机制**：
   - 每天删除超过 `RETENTION_DAYS` 的旧图片
   - 基于目录名（日期格式）判断过期文件
   - 独立任务确保清理不影响主流程

5. **触发机制**：
   - 每10分钟自动执行（匹配卫星更新频率）
   - 支持手动触发（GitHub 界面操作）
   - 清理任务每天自动执行（通过主任务间接触发）

### 使用前配置：
1. 在仓库 Settings → Environments 中设置：
   ```env
   RESOLUTIONS="2160,1440,1080"  # 所需分辨率列表
   RETENTION_DAYS=1              # 图片保留天数
   ```
2. 确保仓库有写入权限（Settings → Actions → General → Workflow permissions）

### 文件路径示例：
新图片将保存在仓库根目录的日期文件夹中：
```
/2025-07-01/
  0310_2160.webp
  0310_1440.webp
  0310_1080.webp
```

旧图片（超过保留天数）会在后续任务中自动删除。