# AI Agent - 联网智能助手

基于Flask + DeepSeek API的联网AI智能助手，能够自动判断问题是否需要实时信息，并进行联网搜索和分析。

## 功能特点

- 🤖 **智能分析**: 自动判断问题是否需要联网搜索
- 🔍 **多引擎搜索**: 支持DuckDuckGo和Google搜索
- 🕷️ **内容爬取**: 自动爬取网页内容进行分析
- 🧠 **AI分析**: 结合搜索结果生成准确回答
- 💬 **友好界面**: 现代化的聊天界面
- ⚡ **异步处理**: 支持高并发，实时进度显示
- 🔄 **实时通信**: WebSocket实时更新处理状态
- 🧪 **完整测试**: 包含完整的单元测试

## 项目结构

```
ai_agent_2/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── config.py                 # 配置文件
│   ├── celery_app.py            # Celery配置
│   ├── tasks.py                 # 异步任务
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
├── scripts/                      # 启动脚本目录
│   ├── start.py                 # 基础启动脚本
│   ├── start_async.py           # 异步启动脚本
│   ├── start_worker.py          # Worker启动脚本
│   ├── start_distributed.py     # 分布式启动脚本
│   ├── install.py               # 安装脚本
│   └── update_dependencies.py   # 依赖更新脚本
├── config/                       # 配置文件目录
│   └── nginx.conf               # Nginx配置文件
├── docker-compose.yml           # Docker编排文件
├── docker-compose-distributed.yml # 分布式Docker编排文件
├── Dockerfile                   # Docker镜像文件
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
python scripts/update_dependencies.py
```

### 2. 配置环境变量

创建 `.env` 文件并配置DeepSeek API密钥：

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export SECRET_KEY="your-secret-key"
```

### 3. 运行应用

#### 方式一：异步模式（推荐）

```bash
# 启动异步服务（包含Redis、Celery Worker和Flask应用）
python scripts/start_async.py
```

#### 方式二：手动启动各个组件

```bash
# 1. 启动Redis（如果未运行）
redis-server

# 2. 启动Celery Worker（新终端）
python scripts/start_worker.py

# 3. 启动Flask应用（新终端）
python app.py
```

#### 方式三：Docker部署

```bash
# 使用Docker Compose一键启动
docker-compose up -d
```

#### 方式四：分布式部署

```bash
# 启动分布式服务（3个Web实例 + 3个Worker实例）
python scripts/start_distributed.py --instances 3 --workers 3

# 使用Docker Compose启动分布式服务
docker-compose -f docker-compose-distributed.yml up -d
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

### 单元测试

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

### 配置测试

测试Celery和Redis配置：

```bash
python test/test_celery_config.py
```

### 性能测试

测试异步架构性能：

```bash
python test/test_performance.py
```

### 分布式测试

测试分布式架构：

```bash
python test/test_distributed.py
```

## 技术栈

### 后端技术
- **Web框架**: Flask + Flask-SocketIO
- **异步任务**: Celery + Redis
- **AI服务**: DeepSeek API
- **搜索引擎**: DuckDuckGo, Google
- **网页解析**: BeautifulSoup4, lxml
- **HTTP请求**: requests
- **实时通信**: WebSocket (SocketIO)

### 前端技术
- **UI框架**: Bootstrap 5
- **图标**: Font Awesome
- **Markdown渲染**: marked.js
- **代码高亮**: Prism.js
- **实时通信**: Socket.IO Client

### 部署技术
- **容器化**: Docker + Docker Compose
- **进程管理**: Celery Worker
- **缓存/消息队列**: Redis
- **负载均衡**: Nginx
- **分布式通信**: Redis + SocketIO
- **监控**: Flower
- **测试**: unittest

## 分布式架构

### 架构特点

- **水平扩展**: 支持多实例部署，轻松扩展处理能力
- **负载均衡**: Nginx自动分发请求到不同实例
- **实时通信**: Redis作为SocketIO消息代理，支持跨实例通信
- **任务队列**: Celery + Redis实现分布式任务处理
- **监控管理**: Flower提供任务监控和管理界面

### 部署架构图

```
                    ┌─────────────┐
                    │   用户请求   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    │ 负载均衡器   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │ Web实例1 │        │ Web实例2 │        │ Web实例3 │
   │ :8002   │        │ :8003   │        │ :8004   │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │    Redis    │
                    │ 消息代理/缓存 │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │Worker1  │        │Worker2  │        │Worker3  │
   │任务处理  │        │任务处理  │        │任务处理  │
   └─────────┘        └─────────┘        └─────────┘
```

### 性能优势

- **高可用性**: 单点故障不影响整体服务
- **高并发**: 支持数千个并发连接
- **弹性扩展**: 可根据负载动态调整实例数量
- **实时监控**: 完整的任务和性能监控

## 故障排除

### Worker启动失败

如果遇到 `'NoneType' object has no attribute 'Redis'` 错误：

1. **检查环境变量**：
   ```bash
   python test/test_worker.py
   ```

2. **确保.env文件存在**：
   ```bash
   cp env.example .env
   # 编辑.env文件，设置DEEPSEEK_API_KEY
   ```

3. **检查Redis服务**：
   ```bash
   redis-cli ping
   # 应该返回 PONG
   ```

4. **手动设置环境变量**：
   ```bash
   export DEEPSEEK_API_KEY="your-api-key"
   python celery_worker.py
   ```

### 常见问题

1. **Redis连接失败**：
   - 确保Redis服务正在运行
   - 检查端口6379是否被占用
   - 验证Redis配置

2. **任务执行失败**：
   - 检查DeepSeek API密钥是否有效
   - 验证网络连接
   - 查看Worker日志

3. **SocketIO连接问题**：
   - 确保Redis作为消息代理正常运行
   - 检查防火墙设置
   - 验证WebSocket支持

## 注意事项

1. 需要有效的DeepSeek API密钥
2. 搜索引擎可能受到访问限制
3. 网页爬取需要遵守robots.txt规则
4. 分布式部署需要确保Redis服务稳定运行
5. 建议在生产环境中配置适当的错误处理和日志记录
6. 监控地址: http://localhost:5555 (Flower)

## 许可证

MIT License
