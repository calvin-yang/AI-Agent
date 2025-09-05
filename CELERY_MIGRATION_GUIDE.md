# Celery任务迁移指南

## 概述

已成功将Celery任务从`app/tasks.py`迁移到`app/schedules/`目录结构中，以便更好地组织和扩展任务。

## 主要变更

### 1. 目录结构变更

**之前:**
```
app/
├── tasks.py          # 所有任务都在这里
└── celery_app.py     # Celery配置
```

**现在:**
```
app/
├── schedules/                    # 新的任务目录
│   ├── __init__.py
│   ├── alert.py                 # 告警相关任务
│   ├── chat_tasks.py           # 聊天相关任务（从tasks.py迁移）
│   ├── user_task.py            # 用户相关任务
│   └── project/                # 项目特定任务
│       ├── __init__.py
│       └── nftfair_task.py     # NFT Fair项目任务
├── celeryconfig.py             # 新的Celery配置文件
└── celery_app.py               # 更新的Celery应用配置
```

### 2. 配置文件变更

- **新增**: `app/celeryconfig.py` - 集中管理所有Celery配置
- **更新**: `app/celery_app.py` - 使用新的配置加载方式
- **更新**: `app/ext/__init__.py` - 更新扩展初始化

### 3. 任务迁移

- `process_question_async` → `app/schedules/chat_tasks.py`
- `get_suggestions_async` → `app/schedules/chat_tasks.py`
- `task_status_callback` → `app/schedules/chat_tasks.py`

## 启动Worker

### 方法1: 使用根目录脚本
```bash
python celery_worker.py
```

### 方法2: 使用scripts目录脚本
```bash
python scripts/start_worker.py
```

### 方法3: 直接使用celery命令
```bash
celery -A app.ext.celery worker --loglevel=info
```

## 验证配置

### 测试新的任务结构
```bash
python test_schedules.py
```

### 测试chat_tasks
```bash
python test_chat_tasks.py
```

## 添加新任务

### 1. 创建任务文件
```python
# app/schedules/your_module.py
from app.ext import celery

@celery.task(bind=True)
def your_task(self, param1, param2):
    # 任务逻辑
    pass
```

### 2. 在celeryconfig.py中注册
```python
CELERY_IMPORTS = (
    'app.schedules.alert',
    'app.schedules.chat_tasks',
    'app.schedules.project.nftfair_task',
    'app.schedules.user_task',
    'app.schedules.your_module',  # 添加你的模块
)
```

### 3. 配置定时任务（可选）
```python
CELERYBEAT_SCHEDULE = {
    'your-scheduled-task': {
        'task': 'app.schedules.your_module.your_task',
        'schedule': crontab(minute='*/10'),
        'args': ('param1', 'param2'),
    },
}
```

## 队列配置

系统现在支持多个队列：

- `default`: 默认队列
- `alerts`: 告警队列
- `nft`: NFT相关任务队列

### 指定队列启动Worker
```bash
# 监听特定队列
celery -A app.ext.celery worker --loglevel=info --queues=default,alerts

# 监听所有队列
celery -A app.ext.celery worker --loglevel=info
```

## 监控任务

### 使用Flower监控
```bash
celery -A app.ext.celery flower
```

### 查看任务状态
```python
from app.ext import celery

# 获取任务结果
result = celery.AsyncResult('task-id')
print(result.state)
print(result.result)
```

## 故障排除

### 1. 任务未注册
- 检查`celeryconfig.py`中的`CELERY_IMPORTS`
- 确保任务文件语法正确
- 重启Worker

### 2. 导入错误
- 检查Python路径
- 确保所有依赖已安装
- 检查模块导入语句

### 3. 配置不生效
- 确保`celery.config_from_object('app.celeryconfig')`被调用
- 检查配置文件语法
- 重启Worker

## 性能优化

### 1. 队列分离
- 将不同类型的任务分配到不同队列
- 使用专门的Worker处理特定队列

### 2. 任务路由
- 使用`CELERY_ROUTES`配置任务路由
- 根据任务类型选择合适的工作进程

### 3. 监控和日志
- 启用任务事件监控
- 配置适当的日志级别
- 使用Flower进行实时监控

## 下一步

1. 根据业务需求添加更多任务模块
2. 配置定时任务
3. 设置监控和告警
4. 优化队列和路由配置
5. 添加任务重试和错误处理机制
