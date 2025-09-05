from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.services.wallet_auth_service import WalletAuthService
from app.decorators.auth import wallet_auth_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/nonce', methods=['POST'])
def generate_nonce():
    """生成钱包认证随机数"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address', '').strip()
        
        if not wallet_address:
            return jsonify({
                'success': False,
                'error': '钱包地址不能为空'
            }), 400
        
        # 验证钱包地址格式
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            return jsonify({
                'success': False,
                'error': '无效的钱包地址格式'
            }), 400
        
        auth_service = WalletAuthService()
        result = auth_service.generate_nonce(wallet_address)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成随机数时发生错误: {str(e)}'
        }), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_signature():
    """验证钱包签名并登录"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address', '').strip()
        signature = data.get('signature', '').strip()
        nonce = data.get('nonce', '').strip()
        wallet_type = data.get('wallet_type', 'metamask')
        chain_id = data.get('chain_id', 1)
        
        # 验证必需参数
        if not all([wallet_address, signature, nonce]):
            return jsonify({
                'success': False,
                'error': '钱包地址、签名和随机数不能为空'
            }), 400
        
        # 验证钱包地址格式
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            return jsonify({
                'success': False,
                'error': '无效的钱包地址格式'
            }), 400
        
        auth_service = WalletAuthService()
        
        # 验证签名
        is_valid, message = auth_service.verify_signature(wallet_address, signature, nonce)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # 认证用户
        is_authenticated, result = auth_service.authenticate_user(
            wallet_address=wallet_address,
            wallet_type=wallet_type,
            chain_id=chain_id
        )
        
        if not is_authenticated:
            return jsonify({
                'success': False,
                'error': result
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'验证签名时发生错误: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@wallet_auth_required
def get_profile():
    """获取用户资料"""
    try:
        user = g.current_user
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取用户资料时发生错误: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@wallet_auth_required
def update_profile():
    """更新用户资料"""
    try:
        user = g.current_user
        data = request.get_json()
        
        # 允许更新的字段
        allowed_fields = ['username', 'email', 'avatar_url']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        user.save()
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新用户资料时发生错误: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@wallet_auth_required
def refresh_token():
    """刷新token"""
    try:
        user = g.current_user
        auth_service = WalletAuthService()
        new_token = auth_service.refresh_token(user)
        
        return jsonify({
            'success': True,
            'data': {
                'token': new_token,
                'expires_in': auth_service.jwt_expiration
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'刷新token时发生错误: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@wallet_auth_required
def logout():
    """登出（客户端需要删除token）"""
    return jsonify({
        'success': True,
        'message': '登出成功'
    })
