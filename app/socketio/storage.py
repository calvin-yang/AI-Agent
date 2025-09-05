"""
SocketIO分布式存储模块
提供会话数据、历史记录、任务状态等分布式存储功能
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app


class SocketIOStorage:
    """SocketIO分布式存储类"""
    
    def __init__(self):
        self.session_prefix = "socketio:session:"
        self.task_prefix = "socketio:task:"
        self.history_prefix = "socketio:history:"
        self.suggestion_prefix = "socketio:suggestion:"
        self.session_ttl = 3600 * 24  # 会话数据24小时过期
        self.history_ttl = 3600 * 24 * 7  # 历史记录7天过期
    
    def get_redis_client(self):
        """获取Redis客户端"""
        try:
            return current_app.redis
        except:
            # 如果无法获取app上下文，返回None
            return None
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        return int(time.time())
    
    def store_session(self, session_id: str, session_data: Dict[str, Any]):
        """存储会话数据"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                print("❌ 无法获取Redis客户端")
                return False
            
            key = f"{self.session_prefix}{session_id}"
            session_data['updated_at'] = self.get_current_timestamp()
            
            redis_client.hset(key, mapping=session_data)
            redis_client.expire(key, self.session_ttl)
            
            print(f"✅ 会话数据已存储: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 存储会话数据失败: {str(e)}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话数据"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return None
            
            key = f"{self.session_prefix}{session_id}"
            session_data = redis_client.hgetall(key)
            
            if session_data:
                # 转换字节字符串为普通字符串
                return {k.decode() if isinstance(k, bytes) else k: 
                       v.decode() if isinstance(v, bytes) else v 
                       for k, v in session_data.items()}
            
            return None
            
        except Exception as e:
            print(f"❌ 获取会话数据失败: {str(e)}")
            return None
    
    def cleanup_session(self, session_id: str):
        """清理会话数据"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            # 删除会话数据
            session_key = f"{self.session_prefix}{session_id}"
            redis_client.delete(session_key)
            
            # 删除相关任务数据
            task_key = f"{self.task_prefix}{session_id}"
            redis_client.delete(task_key)
            
            # 删除建议任务数据
            suggestion_key = f"{self.suggestion_prefix}{session_id}"
            redis_client.delete(suggestion_key)
            
            print(f"✅ 会话数据已清理: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 清理会话数据失败: {str(e)}")
            return False
    
    def store_question(self, session_id: str, question: str):
        """存储问题到历史记录"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.history_prefix}{session_id}"
            question_data = {
                'question': question,
                'timestamp': self.get_current_timestamp(),
                'type': 'question'
            }
            
            # 使用列表存储历史记录
            redis_client.lpush(key, json.dumps(question_data))
            redis_client.expire(key, self.history_ttl)
            
            print(f"✅ 问题已存储到历史: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 存储问题失败: {str(e)}")
            return False
    
    def store_answer(self, session_id: str, answer: str, task_id: str = None):
        """存储答案到历史记录"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.history_prefix}{session_id}"
            answer_data = {
                'answer': answer,
                'timestamp': self.get_current_timestamp(),
                'type': 'answer',
                'task_id': task_id
            }
            
            # 使用列表存储历史记录
            redis_client.lpush(key, json.dumps(answer_data))
            redis_client.expire(key, self.history_ttl)
            
            print(f"✅ 答案已存储到历史: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 存储答案失败: {str(e)}")
            return False
    
    def store_task(self, session_id: str, task_id: str, task_data: Dict[str, Any]):
        """存储任务信息"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.task_prefix}{session_id}"
            task_data['task_id'] = task_id
            task_data['updated_at'] = self.get_current_timestamp()
            
            redis_client.hset(key, task_id, json.dumps(task_data))
            redis_client.expire(key, self.session_ttl)
            
            print(f"✅ 任务信息已存储: {task_id}")
            return True
            
        except Exception as e:
            print(f"❌ 存储任务信息失败: {str(e)}")
            return False
    
    def update_task_status(self, session_id: str, task_id: str, status: str, result: Any = None):
        """更新任务状态"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.task_prefix}{session_id}"
            task_data_str = redis_client.hget(key, task_id)
            
            if task_data_str:
                task_data = json.loads(task_data_str.decode() if isinstance(task_data_str, bytes) else task_data_str)
                task_data['status'] = status
                task_data['updated_at'] = self.get_current_timestamp()
                
                if result is not None:
                    task_data['result'] = result
                
                redis_client.hset(key, task_id, json.dumps(task_data))
                redis_client.expire(key, self.session_ttl)
                
                print(f"✅ 任务状态已更新: {task_id} -> {status}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 更新任务状态失败: {str(e)}")
            return False
    
    def store_suggestion_task(self, session_id: str, task_id: str, task_data: Dict[str, Any]):
        """存储建议任务信息"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.suggestion_prefix}{session_id}"
            task_data['task_id'] = task_id
            task_data['updated_at'] = self.get_current_timestamp()
            
            redis_client.hset(key, task_id, json.dumps(task_data))
            redis_client.expire(key, self.session_ttl)
            
            print(f"✅ 建议任务信息已存储: {task_id}")
            return True
            
        except Exception as e:
            print(f"❌ 存储建议任务信息失败: {str(e)}")
            return False
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取会话历史记录"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return []
            
            key = f"{self.history_prefix}{session_id}"
            history_data = redis_client.lrange(key, 0, limit - 1)
            
            history = []
            for item in history_data:
                try:
                    data = json.loads(item.decode() if isinstance(item, bytes) else item)
                    history.append(data)
                except:
                    continue
            
            return history
            
        except Exception as e:
            print(f"❌ 获取历史记录失败: {str(e)}")
            return []
    
    def clear_session_history(self, session_id: str):
        """清除会话历史记录"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            key = f"{self.history_prefix}{session_id}"
            redis_client.delete(key)
            
            print(f"✅ 历史记录已清除: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 清除历史记录失败: {str(e)}")
            return False
    
    def get_task_status(self, session_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return None
            
            key = f"{self.task_prefix}{session_id}"
            task_data_str = redis_client.hget(key, task_id)
            
            if task_data_str:
                return json.loads(task_data_str.decode() if isinstance(task_data_str, bytes) else task_data_str)
            
            return None
            
        except Exception as e:
            print(f"❌ 获取任务状态失败: {str(e)}")
            return None
    
    def get_all_sessions(self) -> List[str]:
        """获取所有活跃会话ID"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return []
            
            pattern = f"{self.session_prefix}*"
            keys = redis_client.keys(pattern)
            
            sessions = []
            for key in keys:
                session_id = key.decode().replace(self.session_prefix, '') if isinstance(key, bytes) else key.replace(self.session_prefix, '')
                sessions.append(session_id)
            
            return sessions
            
        except Exception as e:
            print(f"❌ 获取会话列表失败: {str(e)}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return {}
            
            stats = {
                'active_sessions': len(redis_client.keys(f"{self.session_prefix}*")),
                'total_tasks': len(redis_client.keys(f"{self.task_prefix}*")),
                'total_history': len(redis_client.keys(f"{self.history_prefix}*")),
                'total_suggestions': len(redis_client.keys(f"{self.suggestion_prefix}*"))
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 获取存储统计失败: {str(e)}")
            return {}
