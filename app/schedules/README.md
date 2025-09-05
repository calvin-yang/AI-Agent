# Celery任务调度目录

这个目录包含了所有的Celery任务，按功能模块组织。

## 目录结构

```
app/schedules/
├── __init__.py                 # 包初始化文件
├── README.md                   # 说明文档
├── alert.py                    # 告警相关任务
├── chat_tasks.py              # 聊天相关任务（从原tasks.py迁移）
├── user_task.py               # 用户相关任务示例
└── project/                   # 项目特定任务
    ├── __init__.py
    └── nftfair_task.py        # NFT Fair项目任务
```

## 任务分类

### 1. 系统任务
- `alert.py`: 系统告警和健康检查任务
- `chat_tasks.py`: 聊天和AI处理相关任务

### 2. 业务任务
- `user_task.py`: 用户管理相关任务
- `project/nftfair_task.py`: NFT Fair项目特定任务

## 添加新任务

### 1. 创建新的任务文件

```python
# app/schedules/your_module.py
from app.ext import celery

@celery.task(bind=True)
def your_task(self, param1, param2):
    """
    任务描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'status': '处理中...', 'progress': 50}
        )
        
        # 你的业务逻辑
        
        # 更新完成状态
        self.update_state(
            state='SUCCESS',
            meta={'status': '处理完成', 'progress': 100}
        )
        
        return {'status': 'SUCCESS', 'result': 'your_result'}
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'status': f'处理失败: {str(e)}', 'progress': 0}
        )
        return {'status': 'FAILURE', 'error': str(e)}
```

### 2. 在celeryconfig.py中注册任务

```python
# app/celeryconfig.py
CELERY_IMPORTS = (
    'app.schedules.alert',
    'app.schedules.chat_tasks',
    'app.schedules.project.nftfair_task',
    'app.schedules.your_module',  # 添加你的模块
)
```

### 3. 配置定时任务（可选）

```python
# app/celeryconfig.py
CELERYBEAT_SCHEDULE = {
    'your-scheduled-task': {
        'task': 'app.schedules.your_module.your_task',
        'schedule': crontab(minute='*/10'),  # 每10分钟执行一次
        'args': ('param1', 'param2'),
    },
}
```

### 4. 配置任务路由（可选）

```python
# app/celeryconfig.py
CELERY_ROUTES = {
    'app.schedules.your_module.*': {'queue': 'your_queue'},
}
```

## 任务最佳实践

1. **错误处理**: 始终使用try-catch包装任务逻辑
2. **状态更新**: 使用`update_state`提供任务进度反馈
3. **返回值**: 返回包含状态和结果的字典
4. **日志记录**: 在关键步骤添加日志输出
5. **超时设置**: 为长时间运行的任务设置合适的超时时间

## 队列管理

系统配置了以下队列：
- `default`: 默认队列，用于一般任务
- `alerts`: 告警队列，用于紧急通知
- `nft`: NFT相关任务专用队列

## 监控和调试

- 使用Celery Flower监控任务状态
- 查看Redis中的任务结果
- 检查日志文件获取详细错误信息
