# 任务 07: 微服务 API 网关系统

## 任务信息

### Session ID - Seed_Beta
待填写

### Session ID - Kimi_K2
待填写

### Prompt
基于 flask-restful 开发一个功能完整的微服务 API 网关，具体要求如下：

1. 实现服务发现与注册：
   - 集成 Consul、Etcd 或 Eureka 服务注册中心
   - 实现服务健康检查和自动摘除
   - 支持服务元数据管理
   - 动态服务路由更新（无需重启）

2. 创建智能路由系统：
   - 基于路径、Header、Query 参数的路由规则
   - 支持正则表达式和通配符路由
   - 实现路由优先级和冲突解决
   - 支持路由版本和灰度发布

3. 实现负载均衡策略：
   - 轮询（Round Robin）
   - 加权轮询（Weighted Round Robin）
   - 最少连接（Least Connections）
   - 一致性哈希（Consistent Hashing）
   - IP Hash
   - 自定义负载均衡算法接口

4. 添加熔断和降级机制：
   - 实现 Circuit Breaker 模式
   - 自动降级和服务回退
   - 故障隔离和快速失败
   - 熔断恢复策略（半开状态）

5. 创建请求/响应转换层：
   - 协议转换（HTTP/HTTPS/gRPC/WebSocket）
   - 请求聚合（多个后端请求合并）
   - 响应组装和字段映射
   - 数据格式转换（JSON/XML/Protobuf）

6. 实现 API 网关安全功能：
   - 统一认证和授权
   - API 密钥管理
   - IP 白名单/黑名单
   - 请求签名验证
   - SQL 注入和 XSS 防护

7. 添加监控和追踪系统：
   - 分布式追踪（OpenTelemetry/Jaeger 集成）
   - 请求日志聚合
   - 性能指标收集（Prometheus 集成）
   - 实时监控面板

8. 实现缓存策略：
   - 响应缓存（支持 ETag、Last-Modified）
   - 缓存失效策略
   - 分布式缓存支持
   - 缓存预热和更新

9. 创建管理 API 和控制面板：
   - 路由管理 API
   - 服务管理 API
   - 配置管理 API
   - 监控数据查询 API
   - Web 控制面板（可选）

10. 实现限流和配额管理：
    - 全局限流
    - 服务级别限流
    - 用户级别配额
    - 动态限流调整

11. 添加插件系统：
    - 支持自定义插件开发
    - 插件生命周期管理
    - 插件配置和热加载

12. 编写完整的集成测试，模拟微服务环境
13. 提供详细的部署文档和最佳实践指南

### Description
这是一个涉及微服务架构、分布式系统、服务治理的超复杂全栈开发任务。需要实现完整的 API 网关功能，包括服务发现、负载均衡、熔断降级、安全防护等多个核心模块。

### 题目方向
业务流程 + 功能组件创建 + 工具类实现 + 数据访问实现

### 任务难度评估——代码量
≥1000 行（多文件：gateway/router.py, gateway/discovery.py, gateway/loadbalancer.py, gateway/circuit_breaker.py, gateway/transformer.py, gateway/security.py, gateway/monitor.py, gateway/cache.py, gateway/plugins.py, tests/）

### 任务难度评估——技术栈广度
跨技术栈（≥7种）：Python + Flask-RESTful + 服务注册中心(Consul/Etcd) + gRPC + Redis + Prometheus + OpenTelemetry + 负载均衡算法

### 任务难度评估——优化要求
- 极致性能优化：低延迟路由（<5ms）
- 高可用性：99.99% 可用性保证
- 可扩展性：支持横向扩展
- 极致性能/资源优化

### 任务难度评估——人工开发耗时预估
≥15 小时

### Github PR 链接
待填写

### Github 原始 Repo 链接
https://github.com/flask-restful/flask-restful

### Repo 介绍
Flask-RESTful 是一个 Flask 扩展，用于快速构建 REST API。它鼓励使用最佳实践，并且非常易于上手。

### 技术栈
Python, Flask, Flask-RESTful, 微服务, Consul/Etcd, gRPC, Redis, Prometheus, OpenTelemetry

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

