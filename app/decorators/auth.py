from functools import wraps
from flask import request, jsonify, g
from app.services.wallet_auth_service import WalletAuthService

def wallet_auth_required(f):
    """钱包认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': '缺少认证token'
            }), 401
        
        # 检查Bearer token格式
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({
                'success': False,
                'error': '无效的认证格式'
            }), 401
        
        # 验证token
        auth_service = WalletAuthService()
        is_valid, result = auth_service.verify_jwt_token(token)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': result
            }), 401
        
        # 将用户信息添加到g对象中
        g.current_user = result
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_wallet_auth(f):
    """可选钱包认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
                auth_service = WalletAuthService()
                is_valid, result = auth_service.verify_jwt_token(token)
                
                if is_valid:
                    g.current_user = result
                else:
                    g.current_user = None
            except (IndexError, Exception):
                g.current_user = None
        else:
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function
