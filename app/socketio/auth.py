"""
SocketIO权限验证模块
提供连接权限、房间访问权限、问题提交权限等验证功能
"""

import time
from flask import request, session


class SocketIOAuth:
    """SocketIO权限验证类"""
    
    def __init__(self):
        self.max_connections_per_ip = 10  # 每个IP最大连接数
        self.max_questions_per_minute = 5  # 每分钟最大问题数
        self.blocked_ips = set()  # 被阻止的IP列表
        self.connection_counts = {}  # IP连接计数
        self.question_counts = {}  # IP问题计数
    
    def verify_connection(self):
        """验证连接权限"""
        try:
            client_ip = self.get_client_ip()
            
            # 检查IP是否被阻止
            if client_ip in self.blocked_ips:
                print(f"❌ 连接被拒绝：IP {client_ip} 已被阻止")
                return False
            
            # 检查连接数限制
            if not self._check_connection_limit(client_ip):
                print(f"❌ 连接被拒绝：IP {client_ip} 连接数超限")
                return False
            
            # 记录连接
            self._record_connection(client_ip)
            
            print(f"✅ 连接验证通过：IP {client_ip}")
            return True
            
        except Exception as e:
            print(f"❌ 连接验证失败: {str(e)}")
            return False
    
    def verify_room_access(self, session_id):
        """验证房间访问权限"""
        try:
            # 基本验证：检查session_id格式
            if not session_id or len(session_id) != 36:
                return False
            
            # 可以在这里添加更复杂的房间权限验证逻辑
            # 例如：检查用户是否有权限访问特定房间
            
            return True
            
        except Exception as e:
            print(f"❌ 房间访问验证失败: {str(e)}")
            return False
    
    def verify_question_access(self, session_id, question):
        """验证问题提交权限"""
        try:
            client_ip = self.get_client_ip()
            
            # 检查问题频率限制
            if not self._check_question_rate_limit(client_ip):
                print(f"❌ 问题提交被拒绝：IP {client_ip} 提交频率过高")
                return False
            
            # 检查问题内容
            if not self._validate_question_content(question):
                print(f"❌ 问题提交被拒绝：问题内容不符合规范")
                return False
            
            # 记录问题提交
            self._record_question(client_ip)
            
            return True
            
        except Exception as e:
            print(f"❌ 问题权限验证失败: {str(e)}")
            return False
    
    def verify_suggestion_access(self, session_id, question):
        """验证建议获取权限"""
        try:
            # 基本验证：检查session_id和问题
            if not session_id or not question:
                return False
            
            # 可以添加更复杂的建议权限验证逻辑
            return True
            
        except Exception as e:
            print(f"❌ 建议权限验证失败: {str(e)}")
            return False
    
    def verify_history_access(self, session_id):
        """验证历史记录访问权限"""
        try:
            # 基本验证：检查session_id
            if not session_id:
                return False
            
            # 可以添加更复杂的历史记录权限验证逻辑
            return True
            
        except Exception as e:
            print(f"❌ 历史记录权限验证失败: {str(e)}")
            return False
    
    def get_client_ip(self):
        """获取客户端IP地址"""
        try:
            # 尝试从代理头获取真实IP
            if request.headers.get('X-Forwarded-For'):
                return request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif request.headers.get('X-Real-IP'):
                return request.headers.get('X-Real-IP')
            else:
                return request.remote_addr
        except:
            return 'unknown'
    
    def get_user_agent(self):
        """获取用户代理"""
        try:
            return request.headers.get('User-Agent', 'unknown')
        except:
            return 'unknown'
    
    def get_current_session_id(self):
        """获取当前会话ID"""
        try:
            # 这里可以从session或其他地方获取当前会话ID
            # 具体实现取决于你的会话管理方式
            return session.get('session_id')
        except:
            return None
    
    def _check_connection_limit(self, client_ip):
        """检查连接数限制"""
        current_count = self.connection_counts.get(client_ip, 0)
        return current_count < self.max_connections_per_ip
    
    def _check_question_rate_limit(self, client_ip):
        """检查问题提交频率限制"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # 清理过期的计数记录
        if client_ip in self.question_counts:
            self.question_counts[client_ip] = [
                timestamp for timestamp in self.question_counts[client_ip]
                if timestamp > minute_ago
            ]
        
        # 检查当前分钟内的提交次数
        current_count = len(self.question_counts.get(client_ip, []))
        return current_count < self.max_questions_per_minute
    
    def _validate_question_content(self, question):
        """验证问题内容"""
        try:
            # 基本内容验证
            if len(question) < 2 or len(question) > 1000:
                return False
            
            # 检查是否包含敏感词（这里可以扩展）
            sensitive_words = ['spam', '广告', '垃圾']
            question_lower = question.lower()
            for word in sensitive_words:
                if word in question_lower:
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ 问题内容验证失败: {str(e)}")
            return False
    
    def _record_connection(self, client_ip):
        """记录连接"""
        self.connection_counts[client_ip] = self.connection_counts.get(client_ip, 0) + 1
    
    def _record_question(self, client_ip):
        """记录问题提交"""
        current_time = time.time()
        if client_ip not in self.question_counts:
            self.question_counts[client_ip] = []
        self.question_counts[client_ip].append(current_time)
    
    def block_ip(self, client_ip, reason="违规行为"):
        """阻止IP地址"""
        self.blocked_ips.add(client_ip)
        print(f"🚫 IP {client_ip} 已被阻止，原因: {reason}")
    
    def unblock_ip(self, client_ip):
        """解除IP阻止"""
        self.blocked_ips.discard(client_ip)
        print(f"✅ IP {client_ip} 已解除阻止")
    
    def get_connection_stats(self):
        """获取连接统计信息"""
        return {
            'total_connections': sum(self.connection_counts.values()),
            'unique_ips': len(self.connection_counts),
            'blocked_ips': len(self.blocked_ips),
            'connection_counts': dict(self.connection_counts),
            'blocked_ips_list': list(self.blocked_ips)
        }
