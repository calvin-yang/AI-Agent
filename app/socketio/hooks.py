"""
SocketIO扩展钩子系统
提供插件化的扩展机制，支持权限验证、分布式存储、监控等功能
"""

from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod
import logging


class SocketIOHook(ABC):
    """SocketIO钩子基类"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.enabled = True
    
    @abstractmethod
    def before_connect(self, **kwargs) -> bool:
        """连接前钩子"""
        pass
    
    @abstractmethod
    def after_connect(self, session_id: str, **kwargs) -> bool:
        """连接后钩子"""
        pass
    
    @abstractmethod
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        """断开连接前钩子"""
        pass
    
    @abstractmethod
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        """断开连接后钩子"""
        pass
    
    @abstractmethod
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        """问题提交前钩子"""
        pass
    
    @abstractmethod
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        """问题提交后钩子"""
        pass


class HookManager:
    """钩子管理器"""
    
    def __init__(self):
        self.hooks: List[SocketIOHook] = []
        self.logger = logging.getLogger(__name__)
    
    def register_hook(self, hook: SocketIOHook):
        """注册钩子"""
        self.hooks.append(hook)
        # 按优先级排序
        self.hooks.sort(key=lambda x: x.priority, reverse=True)
        self.logger.info(f"✅ 钩子已注册: {hook.name} (优先级: {hook.priority})")
    
    def unregister_hook(self, hook_name: str):
        """注销钩子"""
        self.hooks = [hook for hook in self.hooks if hook.name != hook_name]
        self.logger.info(f"✅ 钩子已注销: {hook_name}")
    
    def get_hook(self, hook_name: str) -> Optional[SocketIOHook]:
        """获取指定钩子"""
        for hook in self.hooks:
            if hook.name == hook_name:
                return hook
        return None
    
    def enable_hook(self, hook_name: str):
        """启用钩子"""
        hook = self.get_hook(hook_name)
        if hook:
            hook.enabled = True
            self.logger.info(f"✅ 钩子已启用: {hook_name}")
    
    def disable_hook(self, hook_name: str):
        """禁用钩子"""
        hook = self.get_hook(hook_name)
        if hook:
            hook.enabled = False
            self.logger.info(f"✅ 钩子已禁用: {hook_name}")
    
    def execute_before_connect(self, **kwargs) -> bool:
        """执行连接前钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.before_connect(**kwargs):
                        self.logger.warning(f"❌ 钩子阻止连接: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def execute_after_connect(self, session_id: str, **kwargs) -> bool:
        """执行连接后钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.after_connect(session_id, **kwargs):
                        self.logger.warning(f"❌ 钩子处理连接后事件失败: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def execute_before_disconnect(self, session_id: str, **kwargs) -> bool:
        """执行断开连接前钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.before_disconnect(session_id, **kwargs):
                        self.logger.warning(f"❌ 钩子处理断开连接前事件失败: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def execute_after_disconnect(self, session_id: str, **kwargs) -> bool:
        """执行断开连接后钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.after_disconnect(session_id, **kwargs):
                        self.logger.warning(f"❌ 钩子处理断开连接后事件失败: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def execute_before_question(self, session_id: str, question: str, **kwargs) -> bool:
        """执行问题提交前钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.before_question(session_id, question, **kwargs):
                        self.logger.warning(f"❌ 钩子阻止问题提交: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def execute_after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        """执行问题提交后钩子"""
        for hook in self.hooks:
            if hook.enabled:
                try:
                    if not hook.after_question(session_id, question, task_id, **kwargs):
                        self.logger.warning(f"❌ 钩子处理问题提交后事件失败: {hook.name}")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ 钩子执行失败: {hook.name} - {str(e)}")
                    return False
        return True
    
    def get_hooks_info(self) -> List[Dict[str, Any]]:
        """获取所有钩子信息"""
        return [
            {
                'name': hook.name,
                'priority': hook.priority,
                'enabled': hook.enabled,
                'class': hook.__class__.__name__
            }
            for hook in self.hooks
        ]


# 预定义的钩子实现

class AuthHook(SocketIOHook):
    """认证钩子"""
    
    def __init__(self):
        super().__init__("auth", priority=100)
        self.auth = None
    
    def _get_auth(self):
        """延迟导入认证模块"""
        if self.auth is None:
            from .auth import SocketIOAuth
            self.auth = SocketIOAuth()
        return self.auth
    
    def before_connect(self, **kwargs) -> bool:
        return self._get_auth().verify_connection()
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        return self._get_auth().verify_question_access(session_id, question)
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        return True


class StorageHook(SocketIOHook):
    """存储钩子"""
    
    def __init__(self):
        super().__init__("storage", priority=50)
        self.storage = None
    
    def _get_storage(self):
        """延迟导入存储模块"""
        if self.storage is None:
            from .storage import SocketIOStorage
            self.storage = SocketIOStorage()
        return self.storage
    
    def before_connect(self, **kwargs) -> bool:
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        # 存储会话信息
        storage = self._get_storage()
        session_data = {
            'connected_at': storage.get_current_timestamp(),
            'user_agent': kwargs.get('user_agent', 'unknown'),
            'ip_address': kwargs.get('ip_address', 'unknown')
        }
        return storage.store_session(session_id, session_data)
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        # 清理会话数据
        return self._get_storage().cleanup_session(session_id)
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        return True
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        # 存储问题到历史记录
        self._get_storage().store_question(session_id, question)
        return True


class MonitoringHook(SocketIOHook):
    """监控钩子"""
    
    def __init__(self):
        super().__init__("monitoring", priority=10)
        self.connection_count = 0
        self.question_count = 0
    
    def before_connect(self, **kwargs) -> bool:
        return True
    
    def after_connect(self, session_id: str, **kwargs) -> bool:
        self.connection_count += 1
        print(f"📊 监控: 当前连接数 {self.connection_count}")
        return True
    
    def before_disconnect(self, session_id: str, **kwargs) -> bool:
        return True
    
    def after_disconnect(self, session_id: str, **kwargs) -> bool:
        self.connection_count = max(0, self.connection_count - 1)
        print(f"📊 监控: 当前连接数 {self.connection_count}")
        return True
    
    def before_question(self, session_id: str, question: str, **kwargs) -> bool:
        return True
    
    def after_question(self, session_id: str, question: str, task_id: str, **kwargs) -> bool:
        self.question_count += 1
        print(f"📊 监控: 总问题数 {self.question_count}")
        return True


# 全局钩子管理器实例
hook_manager = HookManager()

# 注册默认钩子
hook_manager.register_hook(AuthHook())
hook_manager.register_hook(StorageHook())
hook_manager.register_hook(MonitoringHook())
