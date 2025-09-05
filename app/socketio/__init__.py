"""
SocketIO事件处理模块
提供WebSocket事件处理、权限验证、分布式存储等功能
"""

from .events import register_socketio_events
from .auth import SocketIOAuth
from .storage import SocketIOStorage
from .hooks import hook_manager, SocketIOHook, HookManager

__all__ = [
    'register_socketio_events', 
    'SocketIOAuth', 
    'SocketIOStorage',
    'hook_manager',
    'SocketIOHook',
    'HookManager'
]
