# AI Agent - 联网智能助手

基于Flask + DeepSeek API的联网AI智能助手，能够自动判断问题是否需要实时信息，并进行联网搜索和分析。

## 功能特点

- 🤖 **智能分析**: 自动判断问题是否需要联网搜索
- 🔍 **多引擎搜索**: 支持DuckDuckGo和Google搜索
- 🕷️ **内容爬取**: 自动爬取网页内容进行分析
- 🧠 **AI分析**: 结合搜索结果生成准确回答
- 💬 **友好界面**: 现代化的聊天界面
- 🧪 **完整测试**: 包含完整的单元测试

## 项目结构

```
ai_agent_2/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── config.py                 # 配置文件
│   ├── blueprints/               # Flask蓝图
│   │   ├── __init__.py
│   │   ├── chat.py              # 聊天相关路由
│   │   └── api.py               # API接口
│   ├── services/                 # 服务层
│   │   ├── __init__.py
│   │   ├── deepseek_service.py  # DeepSeek API服务
│   │   ├── search_service.py    # 搜索引擎服务
│   │   ├── crawler_service.py   # 网页爬虫服务
│   │   └── ai_agent_service.py  # AI Agent核心服务
│   └── templates/                # 模板文件
│       ├── base.html
│       └── chat.html
├── test/                         # 测试目录
│   ├── __init__.py
│   ├── test_deepseek_service.py
│   ├── test_search_service.py
│   ├── test_crawler_service.py
│   ├── test_ai_agent_service.py
│   ├── test_app.py
│   └── run_tests.py
├── app.py                        # 应用入口
├── requirements.txt              # 依赖包
└── README.md                     # 项目说明
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 如果遇到 `duckduckgo_search` 包的警告，请运行依赖更新脚本：

```bash
python update_dependencies.py
```

### 2. 配置环境变量

创建 `.env` 文件并配置DeepSeek API密钥：

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export SECRET_KEY="your-secret-key"
```

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:8002` 启动。

## 使用说明

### 聊天界面

1. 打开浏览器访问 `http://localhost:8002`
2. 在输入框中输入您的问题
3. AI会自动分析问题是否需要联网搜索
4. 如果需要，会自动搜索并分析相关内容
5. 最终给出准确、及时的回答

### API接口

#### 1. 聊天接口
```bash
POST /chat
Content-Type: application/json

{
    "question": "今天有什么最新新闻？"
}
```

#### 2. 问题分析接口
```bash
POST /api/analyze
Content-Type: application/json

{
    "question": "什么是Python？"
}
```

#### 3. 搜索接口
```bash
POST /api/search
Content-Type: application/json

{
    "keywords": "人工智能"
}
```

#### 4. 爬取接口
```bash
POST /api/crawl
Content-Type: application/json

{
    "urls": ["http://example.com"]
}
```

#### 5. 完整处理接口
```bash
POST /api/process
Content-Type: application/json

{
    "question": "今天天气怎么样？"
}
```

## 工作流程

1. **问题分析**: AI分析用户问题，判断是否需要联网搜索
2. **关键词提取**: 如果需要搜索，提取相关搜索关键词
3. **多引擎搜索**: 使用DuckDuckGo和Google进行搜索
4. **内容爬取**: 爬取搜索结果中的网页内容
5. **AI分析**: 结合原始问题和搜索结果，生成最终回答
6. **结果展示**: 向用户展示回答和相关来源

## 配置说明

### 搜索引擎配置
```python
SEARCH_ENGINES = {
    'duckduckgo': {
        'enabled': True,
        'weight': 0.6,
        'max_results': 5
    },
    'google': {
        'enabled': True,
        'weight': 0.4,
        'max_results': 3
    }
}
```

### 爬虫配置
```python
CRAWLER_CONFIG = {
    'timeout': 10,
    'max_content_length': 50000,  # 提取的文本内容最大长度（字符数）
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### AI分析配置
```python
AI_ANALYSIS_CONFIG = {
    'max_context_length': 8000,
    'temperature': 0.7
}
```

## 测试

运行所有测试：

```bash
python test/run_tests.py
```

运行特定测试：

```bash
python -m unittest test.test_deepseek_service
python -m unittest test.test_search_service
python -m unittest test.test_crawler_service
python -m unittest test.test_ai_agent_service
python -m unittest test.test_app
```

## 技术栈

- **后端框架**: Flask
- **AI服务**: DeepSeek API
- **搜索引擎**: DuckDuckGo, Google
- **网页解析**: BeautifulSoup4, lxml
- **HTTP请求**: requests
- **前端**: Bootstrap 5, Font Awesome
- **测试**: unittest

## 注意事项

1. 需要有效的DeepSeek API密钥
2. 搜索引擎可能受到访问限制
3. 网页爬取需要遵守robots.txt规则
4. 建议在生产环境中配置适当的错误处理和日志记录

## 许可证

MIT License
