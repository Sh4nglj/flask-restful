# 任务 03: GraphQL 集成与混合 API 支持

## 任务信息

### Session ID - Seed_Beta
待填写

### Session ID - Kimi_K2
待填写

### Prompt
在 flask-restful 项目中集成 GraphQL 支持，实现 REST 和 GraphQL 混合 API 架构，具体要求如下：

1. 集成 Graphene-Python 库，在 flask-restful 中添加 GraphQL 支持
2. 创建统一的数据模型层，同时支持 REST 和 GraphQL 两种查询方式
3. 实现 GraphQL Schema 定义：包括 Query、Mutation、Subscription 类型
4. 为现有的 RESTful 资源自动生成对应的 GraphQL 类型和解析器
5. 实现 GraphQL 高级特性：
   - DataLoader 模式解决 N+1 查询问题
   - 字段级别的权限控制
   - 查询复杂度分析和限制（防止恶意深层嵌套查询）
   - 查询缓存和性能优化
6. 创建 GraphQL Playground 集成，提供交互式查询界面
7. 实现 GraphQL 订阅(Subscriptions)功能，支持实时数据推送（使用 WebSocket）
8. 添加 GraphQL 和 REST 之间的统一错误处理机制
9. 实现 API 版本管理：支持 REST v1、v2 和 GraphQL 共存
10. 创建自动化测试套件，测试 REST 和 GraphQL 端点的功能一致性
11. 编写详细的迁移指南：如何从纯 REST API 迁移到混合架构
12. 提供性能对比报告：REST vs GraphQL 在不同场景下的性能表现

### Description
这是一个涉及现代 API 架构、多种查询语言、实时通信的复杂全栈开发任务。需要深入理解 REST 和 GraphQL 的差异，实现两者的无缝集成，并解决性能和安全问题。

### 题目方向
功能组件创建 + 业务流程 + 数据访问实现

### 任务难度评估——代码量
≥600 行（多文件：graphql/schema.py, graphql/resolvers.py, graphql/dataloaders.py, graphql/subscriptions.py, middleware.py, tests/）

### 任务难度评估——技术栈广度
跨技术栈（≥5种）：Python + Flask-RESTful + Graphene + GraphQL + WebSocket + Redis

### 任务难度评估——优化要求
- N+1 查询优化：使用 DataLoader 批量加载
- 查询复杂度控制：防止恶意查询攻击
- 性能优化：查询缓存、懒加载
- 极致性能/资源优化

### 任务难度评估——人工开发耗时预估
≥10 小时

### Github PR 链接
待填写

### Github 原始 Repo 链接
https://github.com/flask-restful/flask-restful

### Repo 介绍
Flask-RESTful 是一个 Flask 扩展，用于快速构建 REST API。它鼓励使用最佳实践，并且非常易于上手。

### 技术栈
Python, Flask, Flask-RESTful, Graphene, GraphQL, WebSocket, Redis

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

