# 任务 01: 高级认证与授权系统

## 任务信息

### Session ID - Seed_Beta
待填写

### Session ID - Kimi_K2
待填写

### Prompt
实现一个完整的基于 JWT 的认证与授权系统，具体要求如下：

1. 在 flask_restful 中创建一个新的认证模块 `auth.py`，实现 JWT token 的生成、验证和刷新功能
2. 实现基于角色的访问控制（RBAC）系统，支持至少 3 种用户角色：管理员(admin)、编辑者(editor)、访客(viewer)
3. 创建装饰器 `@require_auth` 和 `@require_role(role)` 用于保护 API 端点
4. 实现 token 黑名单机制，支持用户登出后 token 立即失效
5. 添加 token 自动刷新机制，在 token 即将过期时自动生成新 token
6. 实现密码加密存储（使用 bcrypt 或 argon2）和密码强度验证
7. 添加登录失败次数限制和账户锁定功能（5次失败后锁定15分钟）
8. 创建完整的 RESTful API 端点：/auth/register、/auth/login、/auth/logout、/auth/refresh、/auth/change-password
9. 编写完整的单元测试，覆盖所有认证场景和边界情况
10. 添加详细的 API 文档和使用示例

### Description
这是一个涉及后端安全、会话管理、权限控制的复杂全栈开发任务。需要实现完整的认证授权体系，包括 JWT token 管理、RBAC 权限系统、密码安全、防暴力破解等多个安全特性。

### 题目方向
数据访问实现 + 业务流程 + 工具类实现

### 任务难度评估——代码量
≥400 行（多文件：auth.py, decorators.py, models.py, tests/test_auth.py）

### 任务难度评估——技术栈广度
跨技术栈：Python + Flask-RESTful + JWT + 加密库(bcrypt/argon2) + 缓存系统(Redis)

### 任务难度评估——优化要求
- 安全性优化：防止时序攻击、token 泄露、暴力破解
- 性能优化：token 验证缓存、黑名单高效查询
- 极致性能/资源优化

### 任务难度评估——人工开发耗时预估
6-8 小时（熟练者）

### Github PR 链接
待填写

### Github 原始 Repo 链接
https://github.com/flask-restful/flask-restful

### Repo 介绍
Flask-RESTful 是一个 Flask 扩展，用于快速构建 REST API。它鼓励使用最佳实践，并且非常易于上手。

### 技术栈
Python, Flask, Flask-RESTful, JWT, bcrypt/argon2, Redis

### 交互轮次 - Seed_Beta
待填写

### 交互轮次 - Kimi_K2
待填写

### 评分理由（交付完整性）
待评估

### 评分理由（用户体验）
待评估

### 评分理由（工具调用）
待评估

### 评分理由（上下文理解）
待评估

### GSB - 整体评估
待评估

### Trae CN 用户 ID
待填写

### 一面千识 用户 ID
待填写

