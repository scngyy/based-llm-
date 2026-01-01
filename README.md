# PDF预处理器

一个完整的PDF文档预处理工具，支持智能解析、结构化清洗、层级感知切分和Prompt上下文构建。

## 功能特性

### 四个预处理步骤

1. **智能解析** - 使用MinerU API解析PDF，提取文本、表格、公式
2. **结构化清洗** - 清洗和格式化Markdown内容，修复格式问题
3. **层级感知切分** - 智能切分文档，保持结构层次和上下文
4. **Prompt构建** - 构建适合LLM处理的Prompt上下文

### 额外功能

- **PDF转URL** - 将本地PDF转换为可访问的URL
- **云服务器上传** - 支持上传到用户自己的云服务器
- **统一接口** - 一个函数完成所有预处理流程

## 项目结构

```
毕设/
├── utils/                          # 核心工具包（所有配置和操作）
│   ├── 01_pdf_parser.py           # 智能PDF解析器
│   ├── 02_markdown_cleaner.py     # 结构化清洗器
│   ├── 03_chunk_splitter.py       # 层级感知切分器
│   ├── 04_prompt_builder.py       # Prompt构建器
│   ├── 05_pdf_to_url.py           # PDF转URL工具
│   ├── 06_cloud_uploader.py       # 云服务器上传器
│   ├── pdf_preprocessor.py        # 统一预处理器
│   └── __init__.py                # 工具包初始化
├── pdf_processor.py               # 统一PDF预处理接口
├── test_pdf_processor.py          # 简化测试文件
├── cloud_server/                  # 云服务器部署
│   ├── server.py                  # Flask服务器
│   ├── deploy.sh                  # 部署脚本
│   ├── requirements.txt           # 服务器依赖
│   ├── test_connection.py         # 连接测试
│   └── README.md                  # 服务器说明
├── requirements.txt               # Python依赖
├── README.md                      # 项目说明
└── 资料/                          # 参考资料
    ├── PDF预处理方案.md
    ├── 可能要参考的论文.md
    └── 数据结构与算法.pdf
```

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

#### 命令行测试

```bash
python test_pdf_processor.py
# 选择 "2. 命令行测试"
```

#### 图形界面测试

```bash
python test_pdf_processor.py
# 选择 "1. 图形界面测试"
```

### 3. 编程使用

#### 使用统一接口（推荐）

```python
from pdf_processor import process_pdf, process_pdf_with_preset

# 基本使用
result = process_pdf(
    pdf_path="example.pdf",
    api_token="your_token",
    output_dir="./output"
)

if result["success"]:
    data = result["data"]
    print(f"Markdown长度: {len(data['markdown_content'])}")
    print(f"分块数量: {len(data['chunks'])}")
    print(f"Prompt数量: {len(data['prompts'])}")
else:
    print(f"处理失败: {result['error']}")

# 使用预设配置
result = process_pdf_with_preset(
    pdf_path="example.pdf",
    api_token="your_token",
    preset="full",  # minimal, basic, standard, full, qa, rag
    output_dir="./output"
)
```

#### 直接使用预处理器类

```python
from utils.pdf_preprocessor import PDFPreprocessor

# 初始化处理器
api_token = "your_mineru_api_token"
processor = PDFPreprocessor(api_token)

# 处理PDF文件
result = processor.quick_process("path/to/your/file.pdf", "你的问题")

if result["success"]:
    print("处理成功!")
    prompts = result["final_prompts"]
    print(f"生成了 {len(prompts)} 个prompt")
else:
    print(f"处理失败: {result['error']}")
```

## API说明

### PDFPreprocessor 主类

#### 初始化参数
- `api_token`: MinerU API Token（必需）
- `chunk_size`: 切分块大小（默认1000字符）
- `chunk_overlap`: 块重叠（默认200字符）
- `max_context_length`: 最大上下文长度（默认8000字符）

#### 主要方法

1. **quick_process(pdf_input, question="")**
   - 快速处理，使用默认配置

2. **process_for_qa(pdf_input, question)**
   - 为问答场景优化处理

3. **process_for_summary(pdf_input)**
   - 为摘要场景优化处理

4. **process_for_analysis(pdf_input)**
   - 为分析场景优化处理

## 配置说明

### MinerU API Token

需要在代码中配置有效的MinerU API Token：

```python
api_token = "your_api_token_here"
```

### 云服务器配置（可选）

如需使用云服务器上传功能，配置服务器信息：

```python
from utils.cloud_uploader import CloudServerUploader

server_config = {
    "host": "your-server-ip",
    "port": 8080,
    "protocol": "http",
    "upload_endpoint": "/api/upload",
    "auth_token": "your_auth_token"
}

uploader = CloudServerUploader(server_config)
```

## 测试

项目包含完整的测试程序，支持：

- 图形界面测试（点击上传文件）
- 命令行测试（输入文件路径）
- 多种处理模式测试（问答、摘要、分析、快速）

## 注意事项

1. **API限制**: MinerU API有每日2000页的优先级解析限制
2. **文件大小**: 建议PDF文件不超过200MB，600页
3. **网络访问**: 上传服务需要网络连接，某些服务可能受网络限制
4. **临时链接**: 免费上传服务生成的链接有时效性（24小时-30天）

## 故障排除

### 常见问题

1. **"field url is not a valid URL"**
   - 确保PDF文件已成功转换为URL
   - 检查上传服务是否正常工作

2. **上传失败**
   - 尝试不同的上传服务（temp.sh、file.io等）
   - 检查网络连接和文件大小

3. **API解析失败**
   - 检查API Token是否有效
   - 确认文件URL可访问

4. **依赖包问题**
   - 使用 `pip install -r requirements.txt` 安装所有依赖
   - 检查Python版本（建议3.8+）

## 更新日志

- v1.0.0: 初始版本，包含四个预处理步骤和统一接口
- 支持本地文件自动转URL
- 提供完整的测试程序
- 集成多种上传服务方案