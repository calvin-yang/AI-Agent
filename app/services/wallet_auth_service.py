import jwt as pyjwt
import secrets
import hashlib
from datetime import datetime, timedelta
from web3 import Web3
from eth_account.messages import encode_defunct
from app.models.user import User, WalletNonce
from app.config import Config

class WalletAuthService:
    """钱包认证服务"""
    
    def __init__(self):
        self.jwt_secret = Config.WALLET_AUTH_CONFIG['jwt_secret']
        self.jwt_expiration = Config.WALLET_AUTH_CONFIG['jwt_expiration']
        self.nonce_expiration = Config.WALLET_AUTH_CONFIG['nonce_expiration']
        self.supported_chains = Config.WALLET_AUTH_CONFIG['supported_chains']
    
    def generate_nonce(self, wallet_address):
        """生成认证随机数"""
        # 生成随机字符串
        nonce = secrets.token_hex(32)
        
        # 设置过期时间
        expires_at = datetime.utcnow() + timedelta(seconds=self.nonce_expiration)
        
        # 保存到数据库
        wallet_nonce = WalletNonce.create_nonce(
            wallet_address=wallet_address,
            nonce=nonce,
            expires_at=expires_at
        )
        
        return {
            'nonce': nonce,
            'expires_at': expires_at.isoformat(),
            'message': f"请签名以下消息以完成登录:\n\nNonce: {nonce}\n\n时间: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    
    def verify_signature(self, wallet_address, signature, nonce):
        """验证钱包签名"""
        try:
            # 获取有效的随机数
            wallet_nonce = WalletNonce.get_valid_nonce(wallet_address, nonce)
            if not wallet_nonce:
                return False, "无效或过期的随机数"
            
            # 构造消息
            message = f"请签名以下消息以完成登录:\n\nNonce: {nonce}\n\n时间: {wallet_nonce.expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 编码消息
            message_hash = encode_defunct(text=message)
            
            # 验证签名
            try:
                recovered_address = Web3().eth.account.recover_message(message_hash, signature=signature)
                if recovered_address.lower() != wallet_address.lower():
                    return False, "签名验证失败"
            except Exception as e:
                return False, f"签名验证错误: {str(e)}"
            
            # 标记随机数为已使用
            wallet_nonce.mark_as_used()
            
            return True, "签名验证成功"
            
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"
    
    def authenticate_user(self, wallet_address, wallet_type='metamask', chain_id=1):
        """认证用户"""
        try:
            # 检查链ID是否支持
            if chain_id not in self.supported_chains:
                return False, f"不支持的链ID: {chain_id}"
            
            # 查找或创建用户
            user = User.get_by_wallet_address(wallet_address)
            if not user:
                user = User.create_user(
                    wallet_address=wallet_address,
                    wallet_type=wallet_type,
                    chain_id=chain_id
                )
            else:
                # 更新用户信息
                user.wallet_type = wallet_type
                user.chain_id = chain_id
                user.updated_at = datetime.utcnow()
                user.save()
            
            # 更新最后登录时间
            user.update_last_login()
            
            # 生成JWT token
            token = self.generate_jwt_token(user)
            
            return True, {
                'user': user.to_dict(),
                'token': token,
                'expires_in': self.jwt_expiration
            }
            
        except Exception as e:
            return False, f"用户认证失败: {str(e)}"
    
    def generate_jwt_token(self, user):
        """生成JWT token"""
        payload = {
            'user_id': str(user.id),
            'wallet_address': user.wallet_address,
            'wallet_type': user.wallet_type,
            'chain_id': user.chain_id,
            'exp': datetime.utcnow() + timedelta(seconds=self.jwt_expiration),
            'iat': datetime.utcnow()
        }
        
        return pyjwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token):
        """验证JWT token"""
        try:
            payload = pyjwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return False, "无效的token"
            
            user = User.objects(id=user_id).first()
            if not user or not user.is_active:
                return False, "用户不存在或已被禁用"
            
            return True, user
            
        except pyjwt.ExpiredSignatureError:
            return False, "Token已过期"
        except pyjwt.InvalidTokenError:
            return False, "无效的token"
        except Exception as e:
            return False, f"Token验证失败: {str(e)}"
    
    def get_user_from_token(self, token):
        """从token获取用户信息"""
        is_valid, result = self.verify_jwt_token(token)
        if is_valid:
            return result
        return None
    
    def refresh_token(self, user):
        """刷新token"""
        return self.generate_jwt_token(user)
