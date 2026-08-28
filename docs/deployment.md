# 部署指南

## 私有 wheel 构建

```powershell
.\.venv\Scripts\python.exe -m pip install build
.\.venv\Scripts\python.exe -m build
```

产物：

```text
dist/semantic_reconstruction-1.0.0-py3-none-any.whl
dist/semantic-reconstruction-1.0.0.tar.gz
```

## 干净环境安装

```powershell
python -m venv verify-venv
.\verify-venv\Scripts\python.exe -m pip install dist\semantic_reconstruction-1.0.0-py3-none-any.whl
```

验证：

```powershell
.\verify-venv\Scripts\python.exe -c "from semantic_reconstruction import SemanticReconstructor; print(SemanticReconstructor)"
.\verify-venv\Scripts\semantic-reconstruction.exe --version
```

## 密钥管理

推荐方式：

1. 云平台 secret manager
2. 进程环境变量
3. 内部网关注入
4. CLI 本地 `.env` 文件

禁止：

- 将 key 写入代码
- 将 key 写入日志
- 将 key 打包进 wheel
- 将 key 传给前端或客户端

检查：

```powershell
Select-String -Path dist\* -Pattern "sk-[A-Za-z0-9]+" -SimpleMatch:$false
```

## 性能建议

- 大规模离线处理使用 `rule`
- 单文档默认上限 2,000,000 字符
- 超大文档按 H1/H2 拆分
- `include_code_blocks=False` 可降低输出体积
- `include_image_references=False` 和 `include_chart_blocks=False` 可进一步降低输出体积
- 大规模处理建议先使用 `image_understanding="off"`，抽样启用视觉理解
- `keep_raw_evidence=False` 可降低输出体积，但会削弱审计能力
- `llm_batch_size` 越大，请求越少，但单次输出越大；支持范围 1-25
- 视觉模型处理本地图片、`file:///`、data URI，并把 HTTP(S) URL 直接传给 provider；SDK 自身不下载远程图片
- 企业环境可设置 `allow_absolute_image_paths=False`，限制图片必须位于 Markdown 目录内

## 入库建议

只有以下状态建议进入生产知识库：

- `auto_validated`
- 已人工确认的 `pending_business_review`

`blocked` 只能进入待处理队列，不应参与问答。
