from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ListField, IntField, BooleanField

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
