// MongoDB初始化脚本
// 创建数据库和用户

// 切换到ai_agent_db数据库
db = db.getSiblingDB('ai_agent_db');

// 创建应用用户
db.createUser({
  user: 'ai_agent_user',
  pwd: 'ai_agent_password',
  roles: [
    {
      role: 'readWrite',
      db: 'ai_agent_db'
    }
  ]
});

// 创建索引
db.users.createIndex({ "wallet_address": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "email": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "created_at": 1 });

db.wallet_nonces.createIndex({ "wallet_address": 1 });
db.wallet_nonces.createIndex({ "nonce": 1 });
db.wallet_nonces.createIndex({ "expires_at": 1 });
db.wallet_nonces.createIndex({ "created_at": 1 });

print('✅ MongoDB初始化完成');
print('📊 数据库: ai_agent_db');
print('👤 应用用户: ai_agent_user');
print('🔑 应用密码: ai_agent_password');
print('🌐 管理界面: http://localhost:8081');
