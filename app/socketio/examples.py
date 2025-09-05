"""
SocketIO扩展系统使用示例
展示如何创建自定义钩子和扩展功能
"""

from .hooks import SocketIOHook, hook_manager
import logging


class CustomLoggingHook(SocketIOHook):
    """自定义日志记录钩子"""
    
    def __init__(self):
        super().__init__("custom_logging", priority=5)
        self.logger = logging.getLogger(__name__)
    
    def before_connect(self, **kwargs) -> bool:
        self.logger.info("🔗 客户端尝试连接")
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        self.logger.info(f"✅ 客户端已连接: {session_id}")
        return True
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        self.logger.info(f"👋 客户端即将断开连接: {session_id}")
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        self.logger.info(f"❌ 客户端已断开连接: {session_id}")
        return True
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        self.logger.info(f"❓ 用户提问: {session_id} - {question[:50]}...")
        return True
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        self.logger.info(f"🚀 任务已启动: {session_id} - {task_id}")
        return True


class RateLimitHook(SocketIOHook):
    """自定义频率限制钩子"""
    
    def __init__(self):
        super().__init__("rate_limit", priority=80)
        self.question_limits = {}  # {session_id: [timestamps]}
        self.max_questions_per_minute = 3
    
    def before_connect(self, **kwargs) -> bool:
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        self.question_limits[session_id] = []
        return True
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        # 清理频率限制记录
        if session_id in self.question_limits:
            del self.question_limits[session_id]
        return True
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        import time
        current_time = time.time()
        minute_ago = current_time - 60
        
        # 清理过期的记录
        if session_id in self.question_limits:
            self.question_limits[session_id] = [
                timestamp for timestamp in self.question_limits[session_id]
                if timestamp > minute_ago
            ]
        
        # 检查频率限制
        current_count = len(self.question_limits.get(session_id, []))
        if current_count >= self.max_questions_per_minute:
            print(f"❌ 频率限制: {session_id} 在1分钟内提交了{current_count}个问题")
            return False
        
        # 记录问题提交时间
        if session_id not in self.question_limits:
            self.question_limits[session_id] = []
        self.question_limits[session_id].append(current_time)
        
        return True
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        return True


class AnalyticsHook(SocketIOHook):
    """自定义分析统计钩子"""
    
    def __init__(self):
        super().__init__("analytics", priority=1)
        self.stats = {
            'total_connections': 0,
            'total_questions': 0,
            'active_sessions': set(),
            'question_types': {}
        }
    
    def before_connect(self, **kwargs) -> bool:
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        self.stats['total_connections'] += 1
        self.stats['active_sessions'].add(session_id)
        self._log_stats()
        return True
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        self.stats['active_sessions'].discard(session_id)
        self._log_stats()
        return True
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        return True
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        self.stats['total_questions'] += 1
        
        # 分析问题类型
        question_type = self._analyze_question_type(question)
        if question_type not in self.stats['question_types']:
            self.stats['question_types'][question_type] = 0
        self.stats['question_types'][question_type] += 1
        
        self._log_stats()
        return True
    
    def _analyze_question_type(self, question: str) -> str:
        """分析问题类型"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['什么', 'what', '如何', 'how']):
            return '询问类'
        elif any(word in question_lower for word in ['为什么', 'why', '原因']):
            return '原因类'
        elif any(word in question_lower for word in ['怎么', '如何做', '步骤']):
            return '操作类'
        else:
            return '其他'
    
    def _log_stats(self):
        """记录统计信息"""
        print(f"📊 统计信息:")
        print(f"   总连接数: {self.stats['total_connections']}")
        print(f"   活跃会话: {len(self.stats['active_sessions'])}")
        print(f"   总问题数: {self.stats['total_questions']}")
        print(f"   问题类型分布: {self.stats['question_types']}")


def register_custom_hooks():
    """注册自定义钩子"""
    # 注册自定义钩子
    hook_manager.register_hook(CustomLoggingHook())
    hook_manager.register_hook(RateLimitHook())
    hook_manager.register_hook(AnalyticsHook())
    
    print("✅ 自定义钩子已注册")


def get_hooks_status():
    """获取钩子状态"""
    hooks_info = hook_manager.get_hooks_info()
    print("🔧 当前注册的钩子:")
    for hook_info in hooks_info:
        status = "✅ 启用" if hook_info['enabled'] else "❌ 禁用"
        print(f"   {hook_info['name']} ({hook_info['class']}) - 优先级: {hook_info['priority']} - {status}")


# 使用示例
if __name__ == "__main__":
    # 注册自定义钩子
    register_custom_hooks()
    
    # 显示钩子状态
    get_hooks_status()
    
    # 可以动态启用/禁用钩子
    # hook_manager.disable_hook('rate_limit')
    # hook_manager.enable_hook('rate_limit')
