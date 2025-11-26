# 任务 04: 高级序列化与数据转换系统

## 任务信息

### Session ID - Seed_Beta
待填写

### Session ID - Kimi_K2
待填写

### Prompt
开发一个功能强大的数据序列化与转换系统，扩展 flask-restful 的 fields 模块，具体要求如下：

1. 创建高级字段类型，扩展现有的 fields 模块：
   - PolymorphicField：支持多态序列化（根据对象类型自动选择序列化方案）
   - ComputedField：支持计算字段（基于其他字段动态计算值）
   - ConditionalField：条件字段（根据权限或条件决定是否序列化）
   - NestedListField：嵌套列表字段，支持深层嵌套和循环引用检测
   - FileField：文件字段，支持 base64 编码、URL 生成、预签名 URL
   - GeoLocationField：地理位置字段，支持坐标转换和距离计算
   - EncryptedField：加密字段，自动加密/解密敏感数据

2. 实现智能序列化器：
   - 自动从 SQLAlchemy/MongoEngine 模型生成序列化方案
   - 支持字段别名和多语言字段名映射
   - 实现字段级别的验证和清洗
   - 支持序列化上下文（context）传递和条件序列化

3. 创建反序列化系统（数据导入）：
   - 支持从 JSON、XML、CSV、Excel 等多种格式导入数据
   - 实现数据验证和错误收集（一次性返回所有验证错误）
   - 支持批量导入和部分失败处理
   - 添加数据转换管道（pipeline）支持自定义转换逻辑

4. 实现序列化性能优化：
   - 延迟加载和按需序列化（sparse fieldsets）
   - 序列化缓存机制
   - 批量序列化优化
   - 异步序列化支持（使用 asyncio）

5. 添加序列化钩子系统：
   - pre_serialize、post_serialize 钩子
   - 支持全局和局部钩子
   - 实现序列化事件通知

6. 创建序列化配置 DSL：
   - 支持 YAML/JSON 格式的序列化配置
   - 实现配置热加载
   - 提供配置验证工具

7. 编写完整的测试套件，包括性能基准测试
8. 提供详细的使用文档和最佳实践指南

### Description
这是一个涉及数据建模、类型系统、性能优化的复杂后端开发任务。需要深入理解序列化机制，实现多种高级字段类型和优化策略。

### 题目方向
数据访问实现 + 工具类实现 + 功能组件创建

### 任务难度评估——代码量
≥700 行（多文件：fields_advanced.py, serializers.py, deserializers.py, validators.py, hooks.py, cache.py, tests/）

### 任务难度评估——技术栈广度
跨技术栈（≥4种）：Python + Flask-RESTful + SQLAlchemy/MongoEngine + asyncio + 多种数据格式(JSON/XML/CSV)

### 任务难度评估——优化要求
- 性能优化：序列化速度提升3-5倍
- 内存优化：大数据集序列化的内存控制
- 异步优化：支持高并发序列化场景
- 极致性能/资源优化

### 任务难度评估——人工开发耗时预估
≥9 小时

### Github PR 链接
待填写

### Github 原始 Repo 链接
https://github.com/flask-restful/flask-restful

### Repo 介绍
Flask-RESTful 是一个 Flask 扩展，用于快速构建 REST API。它鼓励使用最佳实践，并且非常易于上手。

### 技术栈
Python, Flask, Flask-RESTful, SQLAlchemy, MongoEngine, asyncio, 数据格式转换

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

