# SocketIO扩展系统

这个模块提供了一个可扩展的SocketIO事件处理系统，支持权限验证、分布式存储、监控等功能。

## 目录结构

```
app/socketio/
├── __init__.py          # 模块初始化
├── events.py            # 事件处理器
├── auth.py              # 权限验证模块
├── storage.py           # 分布式存储模块
├── hooks.py             # 钩子系统
├── examples.py          # 使用示例
└── README.md            # 说明文档
```

## 核心组件

### 1. 事件处理器 (events.py)

负责处理WebSocket连接、断开、消息等事件：

- `connect` - 客户端连接
- `disconnect` - 客户端断开连接
- `join_room` - 加入房间
- `leave_room` - 离开房间
- `ask_question` - 处理用户问题
- `get_suggestions` - 获取搜索建议
- `get_history` - 获取历史记录
- `clear_history` - 清除历史记录

### 2. 权限验证模块 (auth.py)

提供多层权限验证：

- **连接权限验证**: 检查IP连接数限制、黑名单等
- **房间访问权限**: 验证用户是否有权限访问特定房间
- **问题提交权限**: 检查问题频率限制、内容验证等
- **历史记录权限**: 验证历史记录访问权限

### 3. 分布式存储模块 (storage.py)

基于Redis的分布式存储：

- **会话数据存储**: 存储用户会话信息
- **历史记录管理**: 存储和检索对话历史
- **任务状态跟踪**: 跟踪异步任务状态
- **数据清理**: 自动清理过期数据

### 4. 钩子系统 (hooks.py)

插件化的扩展机制：

- **钩子基类**: `SocketIOHook` 定义钩子接口
- **钩子管理器**: `HookManager` 管理钩子生命周期
- **预定义钩子**: 认证、存储、监控钩子
- **动态注册**: 支持运行时注册/注销钩子

## 使用方法

### 基本使用

```python
from app.socketio import register_socketio_events

# 在Flask应用中注册事件处理器
register_socketio_events(app)
```

### 创建自定义钩子

```python
from app.socketio.hooks import SocketIOHook, hook_manager

class CustomHook(SocketIOHook):
    def __init__(self):
        super().__init__("custom", priority=50)
    
    def before_connect(self, **kwargs) -> bool:
        # 连接前处理逻辑
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        # 连接后处理逻辑
        return True
    
    # 实现其他钩子方法...

# 注册自定义钩子
hook_manager.register_hook(CustomHook())
```

### 权限验证配置

```python
from app.socketio.auth import SocketIOAuth

auth = SocketIOAuth()

# 配置连接限制
auth.max_connections_per_ip = 10
auth.max_questions_per_minute = 5

# 阻止IP地址
auth.block_ip("192.168.1.100", "违规行为")

# 获取连接统计
stats = auth.get_connection_stats()
```

### 分布式存储使用

```python
from app.socketio.storage import SocketIOStorage

storage = SocketIOStorage()

# 存储会话数据
storage.store_session("session_id", {
    'user_id': 'user123',
    'connected_at': storage.get_current_timestamp()
})

# 获取历史记录
history = storage.get_session_history("session_id", limit=20)

# 存储任务状态
storage.store_task("session_id", "task_id", {
    'question': '用户问题',
    'status': 'processing'
})
```

## 扩展功能

### 1. 自定义权限验证

```python
class CustomAuthHook(SocketIOHook):
    def __init__(self):
        super().__init__("custom_auth", priority=90)
    
    def before_connect(self, **kwargs) -> bool:
        # 自定义连接验证逻辑
        # 例如：检查JWT token、数据库用户验证等
        return True
```

### 2. 自定义存储后端

```python
class DatabaseStorageHook(SocketIOHook):
    def __init__(self):
        super().__init__("database_storage", priority=60)
        # 初始化数据库连接
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        # 将会话数据存储到数据库
        return True
```

### 3. 监控和统计

```python
class MetricsHook(SocketIOHook):
    def __init__(self):
        super().__init__("metrics", priority=10)
        # 初始化监控系统
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        # 发送指标到监控系统
        return True
```

## 配置选项

### 权限验证配置

```python
# 在auth.py中配置
max_connections_per_ip = 10      # 每个IP最大连接数
max_questions_per_minute = 5     # 每分钟最大问题数
```

### 存储配置

```python
# 在storage.py中配置
session_ttl = 3600 * 24          # 会话数据24小时过期
history_ttl = 3600 * 24 * 7      # 历史记录7天过期
```

### 钩子优先级

钩子按优先级执行，数字越大优先级越高：

- 100: 认证钩子
- 80: 频率限制钩子
- 60: 存储钩子
- 50: 自定义钩子
- 10: 监控钩子

## 最佳实践

1. **钩子设计**: 保持钩子功能单一，避免复杂逻辑
2. **错误处理**: 在钩子中妥善处理异常，避免影响主流程
3. **性能考虑**: 避免在钩子中执行耗时操作
4. **日志记录**: 记录关键操作和错误信息
5. **配置管理**: 将配置项提取到配置文件中

## 故障排除

### 常见问题

1. **连接被拒绝**: 检查权限验证钩子配置
2. **存储失败**: 检查Redis连接和配置
3. **钩子不执行**: 检查钩子注册和优先级设置
4. **性能问题**: 检查钩子中的耗时操作

### 调试方法

```python
# 获取钩子状态
from app.socketio.hooks import hook_manager
hooks_info = hook_manager.get_hooks_info()
print(hooks_info)

# 启用/禁用钩子
hook_manager.disable_hook('rate_limit')
hook_manager.enable_hook('rate_limit')
```

## 未来扩展

- [ ] 支持更多存储后端（MongoDB、PostgreSQL等）
- [ ] 添加消息队列支持
- [ ] 实现分布式会话管理
- [ ] 添加实时监控面板
- [ ] 支持插件热加载
