from flask import Blueprint, request, jsonify, g
from app.services.deepseek_service import DeepSeekService
from app.services.search_service import SearchService
from app.services.crawler_service import CrawlerService
from app.services.ai_agent_service import AIAgentService
from app.models.user import User, ChatSession
from app.decorators.auth import wallet_auth_required, optional_wallet_auth
from datetime import datetime
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze_question():
    """分析问题是否需要搜索"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        deepseek_service = DeepSeekService()
        result = deepseek_service.analyze_question(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析问题时发生错误: {str(e)}'
        }), 500

@api_bp.route('/search', methods=['POST'])
def search():
    """搜索接口"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '').strip()
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400
        
        search_service = SearchService()
        results = search_service.search(keywords)
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': keywords,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索时发生错误: {str(e)}'
        }), 500

@api_bp.route('/crawl', methods=['POST'])
def crawl():
    """爬取网页内容"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({
                'success': False,
                'error': 'URL列表不能为空'
            }), 400
        
        crawler_service = CrawlerService()
        results = crawler_service.crawl_multiple_urls(urls)
        
        return jsonify({
            'success': True,
            'data': {
                'urls': urls,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'爬取网页时发生错误: {str(e)}'
        }), 500

@api_bp.route('/process', methods=['POST'])
def process_question():
    """完整的问题处理流程"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        ai_agent = AIAgentService()
        result = ai_agent.process_question(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理问题时发生错误: {str(e)}'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'AI Agent服务运行正常',
        'status': 'healthy'
    })


# ==================== 会话管理API ====================

@api_bp.route('/sessions', methods=['GET'])
@optional_wallet_auth
def get_sessions():
    """获取用户的会话列表"""
    try:
        # 获取查询参数
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # 限制查询数量
        limit = min(limit, 100)
        
        if g.current_user:
            # 已登录用户，获取其会话
            user = User.get_by_wallet_address(g.current_user['wallet_address'])
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            sessions = ChatSession.get_user_sessions(
                user=user,
                include_archived=include_archived,
                limit=limit,
                offset=offset
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'sessions': [session.to_dict() for session in sessions],
                    'total': sessions.count(),
                    'limit': limit,
                    'offset': offset
                }
            })
        else:
            # 未登录用户，返回空列表
            return jsonify({
                'success': True,
                'data': {
                    'sessions': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取会话列表时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions', methods=['POST'])
@optional_wallet_auth
def create_session():
    """创建新会话"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip() if data else ''
        
        if g.current_user:
            # 已登录用户，创建会话
            user = User.get_by_wallet_address(g.current_user['wallet_address'])
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            session = ChatSession.create_session(
                user=user,
                title=title or None
            )
            
            return jsonify({
                'success': True,
                'data': session.to_dict()
            })
        else:
            # 未登录用户，创建临时会话（不保存到数据库）
            import uuid
            session_id = str(uuid.uuid4())
            
            return jsonify({
                'success': True,
                'data': {
                    'id': None,
                    'session_id': session_id,
                    'title': title or '新对话',
                    'user_id': None,
                    'is_active': True,
                    'is_archived': False,
                    'messages': [],
                    'message_count': 0,
                    'last_message_at': None,
                    'created_at': None,
                    'updated_at': None
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>', methods=['GET'])
@optional_wallet_auth
def get_session(session_id):
    """获取特定会话的详细信息"""
    try:
        if g.current_user:
            # 已登录用户，获取其会话
            user = User.get_by_wallet_address(g.current_user['wallet_address'])
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            session = ChatSession.get_by_session_id(session_id, user=user)
            if not session:
                return jsonify({
                    'success': False,
                    'error': '会话不存在'
                }), 404
            
            return jsonify({
                'success': True,
                'data': session.to_dict()
            })
        else:
            # 未登录用户，返回空会话
            return jsonify({
                'success': True,
                'data': {
                    'id': None,
                    'session_id': session_id,
                    'title': '临时对话',
                    'user_id': None,
                    'is_active': True,
                    'is_archived': False,
                    'messages': [],
                    'message_count': 0,
                    'last_message_at': None,
                    'created_at': None,
                    'updated_at': None
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>', methods=['PUT'])
@wallet_auth_required
def update_session(session_id):
    """更新会话信息（仅限已登录用户）"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip() if data else ''
        
        user = User.get_by_wallet_address(g.current_user['wallet_address'])
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        session = ChatSession.get_by_session_id(session_id, user=user)
        if not session:
            return jsonify({
                'success': False,
                'error': '会话不存在'
            }), 404
        
        # 更新标题
        if title:
            session.title = title
            session.updated_at = datetime.utcnow()
            session.save()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>', methods=['DELETE'])
@wallet_auth_required
def delete_session(session_id):
    """删除会话（仅限已登录用户）"""
    try:
        user = User.get_by_wallet_address(g.current_user['wallet_address'])
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        session = ChatSession.get_by_session_id(session_id, user=user)
        if not session:
            return jsonify({
                'success': False,
                'error': '会话不存在'
            }), 404
        
        # 删除会话
        session.delete()
        
        return jsonify({
            'success': True,
            'message': '会话已删除'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>/archive', methods=['POST'])
@wallet_auth_required
def archive_session(session_id):
    """归档会话（仅限已登录用户）"""
    try:
        user = User.get_by_wallet_address(g.current_user['wallet_address'])
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        session = ChatSession.get_by_session_id(session_id, user=user)
        if not session:
            return jsonify({
                'success': False,
                'error': '会话不存在'
            }), 404
        
        session.archive()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'归档会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>/restore', methods=['POST'])
@wallet_auth_required
def restore_session(session_id):
    """恢复会话（仅限已登录用户）"""
    try:
        user = User.get_by_wallet_address(g.current_user['wallet_address'])
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        session = ChatSession.get_by_session_id(session_id, user=user)
        if not session:
            return jsonify({
                'success': False,
                'error': '会话不存在'
            }), 404
        
        session.restore()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'恢复会话时发生错误: {str(e)}'
        }), 500


@api_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@optional_wallet_auth
def add_message(session_id):
    """添加消息到会话"""
    try:
        data = request.get_json()
        message_type = data.get('message_type', '').strip()
        content = data.get('content', '').strip()
        metadata = data.get('metadata')
        
        if not message_type or message_type not in ['user', 'ai']:
            return jsonify({
                'success': False,
                'error': '无效的消息类型'
            }), 400
        
        if not content:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
        
        if g.current_user:
            # 已登录用户，保存到数据库
            user = User.get_by_wallet_address(g.current_user['wallet_address'])
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            session = ChatSession.get_by_session_id(session_id, user=user)
            if not session:
                return jsonify({
                    'success': False,
                    'error': '会话不存在'
                }), 404
            
            # 添加消息
            message = session.add_message(
                message_type=message_type,
                content=content,
                metadata=json.dumps(metadata) if metadata else None
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'message': message.to_dict(),
                    'session': session.to_dict()
                }
            })
        else:
            # 未登录用户，仅返回消息对象（不保存）
            from datetime import datetime
            message_data = {
                'message_type': message_type,
                'content': content,
                'metadata': json.dumps(metadata) if metadata else None,
                'created_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': {
                    'message': message_data,
                    'session': None
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'添加消息时发生错误: {str(e)}'
        }), 500


