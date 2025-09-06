from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ListField, IntField, BooleanField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField

class User(Document):
    """用户模型"""
    
    # 基本信息
    wallet_address = StringField(required=True, unique=True, max_length=42)
    wallet_type = StringField(required=True, choices=['metamask', 'okx'], default='metamask')
    chain_id = IntField(required=True, default=1)  # 默认以太坊主网
    
    # 用户信息
    username = StringField(max_length=50, unique=True, sparse=True)
    email = StringField(max_length=100, unique=True, sparse=True)
    avatar_url = StringField(max_length=500)
    
    # 状态信息
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    last_login = DateTimeField()
    
    # 时间戳
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # 元数据
    meta = {
        'collection': 'users',
        'indexes': [
            'wallet_address',
            'username',
            'email',
            'created_at'
        ]
    }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'wallet_address': self.wallet_address,
            'wallet_type': self.wallet_type,
            'chain_id': self.chain_id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def get_by_wallet_address(cls, wallet_address):
        """根据钱包地址获取用户"""
        return cls.objects(wallet_address=wallet_address.lower()).first()
    
    @classmethod
    def create_user(cls, wallet_address, wallet_type='metamask', chain_id=1, **kwargs):
        """创建新用户"""
        user = cls(
            wallet_address=wallet_address.lower(),
            wallet_type=wallet_type,
            chain_id=chain_id,
            **kwargs
        )
        user.save()
        return user

class WalletNonce(Document):
    """钱包认证随机数模型"""
    
    wallet_address = StringField(required=True, max_length=42)
    nonce = StringField(required=True, max_length=100)
    expires_at = DateTimeField(required=True)
    used = BooleanField(default=False)
    
    # 时间戳
    created_at = DateTimeField(default=datetime.utcnow)
    
    # 元数据
    meta = {
        'collection': 'wallet_nonces',
        'indexes': [
            'wallet_address',
            'nonce',
            'expires_at'
        ]
    }
    
    @classmethod
    def create_nonce(cls, wallet_address, nonce, expires_at):
        """创建新的随机数"""
        wallet_nonce = cls(
            wallet_address=wallet_address.lower(),
            nonce=nonce,
            expires_at=expires_at
        )
        wallet_nonce.save()
        return wallet_nonce
    
    @classmethod
    def get_valid_nonce(cls, wallet_address, nonce):
        """获取有效的随机数"""
        now = datetime.utcnow()
        return cls.objects(
            wallet_address=wallet_address.lower(),
            nonce=nonce,
            expires_at__gt=now,
            used=False
        ).first()
    
    def mark_as_used(self):
        """标记为已使用"""
        self.used = True
        self.save()


class ChatMessage(EmbeddedDocument):
    """聊天消息嵌入文档"""
    
    # 消息类型：user 或 ai
    message_type = StringField(required=True, choices=['user', 'ai'])
    
    # 消息内容
    content = StringField(required=True)
    
    # 消息元数据（AI回答的搜索信息等）
    metadata = StringField()  # JSON字符串格式
    
    # 时间戳
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'message_type': self.message_type,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class ChatSession(Document):
    """聊天会话模型"""
    
    # 会话基本信息
    session_id = StringField(required=True, unique=True, max_length=100)
    title = StringField(max_length=200)  # 会话标题，自动生成或用户设置
    user = ReferenceField(User, required=True)
    
    # 会话状态
    is_active = BooleanField(default=True)
    is_archived = BooleanField(default=False)
    
    # 消息列表
    messages = ListField(EmbeddedDocumentField(ChatMessage), default=list)
    
    # 统计信息
    message_count = IntField(default=0)
    last_message_at = DateTimeField()
    
    # 时间戳
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # 元数据
    meta = {
        'collection': 'chat_sessions',
        'indexes': [
            'session_id',
            'user',
            'created_at',
            'last_message_at',
            'is_active'
        ]
    }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'session_id': self.session_id,
            'title': self.title,
            'user_id': str(self.user.id) if self.user else None,
            'is_active': self.is_active,
            'is_archived': self.is_archived,
            'messages': [msg.to_dict() for msg in self.messages],
            'message_count': self.message_count,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def add_message(self, message_type, content, metadata=None):
        """添加消息到会话"""
        message = ChatMessage(
            message_type=message_type,
            content=content,
            metadata=metadata
        )
        self.messages.append(message)
        self.message_count += 1
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # 自动生成标题（基于第一条用户消息）
        if not self.title and message_type == 'user' and len(self.messages) == 1:
            self.title = content[:50] + ('...' if len(content) > 50 else '')
        
        self.save()
        return message
    
    def get_messages(self, limit=None, offset=0):
        """获取消息列表"""
        messages = self.messages[offset:]
        if limit:
            messages = messages[:limit]
        return [msg.to_dict() for msg in messages]
    
    def clear_messages(self):
        """清空消息"""
        self.messages = []
        self.message_count = 0
        self.updated_at = datetime.utcnow()
        self.save()
    
    def archive(self):
        """归档会话"""
        self.is_archived = True
        self.is_active = False
        self.updated_at = datetime.utcnow()
        self.save()
    
    def restore(self):
        """恢复会话"""
        self.is_archived = False
        self.is_active = True
        self.updated_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def create_session(cls, user, session_id=None, title=None):
        """创建新会话"""
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        session = cls(
            session_id=session_id,
            title=title or '新对话',
            user=user
        )
        session.save()
        return session
    
    @classmethod
    def get_user_sessions(cls, user, include_archived=False, limit=50, offset=0):
        """获取用户的会话列表"""
        query = {'user': user}
        if not include_archived:
            query['is_archived'] = False
        
        sessions = cls.objects(**query).order_by('-last_message_at', '-created_at')
        return sessions.skip(offset).limit(limit)
    
    @classmethod
    def get_by_session_id(cls, session_id, user=None):
        """根据会话ID获取会话"""
        query = {'session_id': session_id}
        if user:
            query['user'] = user
        return cls.objects(**query).first()
