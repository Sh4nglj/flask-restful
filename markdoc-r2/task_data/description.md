# 任务 Prompt

为 Flask-RESTful 实现 API 文档自动生成功能，具体需求如下：
1. 在 flask_restful/utils 目录下创建 docs.py 模块，实现基于代码注释和类型注解的文档生成
2. 自动提取 Resource 类的文档字符串、方法签名和参数信息
3. 解析 RequestParser 的参数定义，生成请求参数文档
4. 解析 fields 定义，生成响应数据结构文档
5. 支持 OpenAPI 3.0 规范，生成标准的 OpenAPI JSON/YAML 文档
6. 实现 Swagger UI 集成，提供交互式 API 文档界面
7. 支持自定义文档模板，允许用户扩展文档格式
8. 自动识别 HTTP 方法、路径参数、查询参数和请求体结构
9. 支持文档版本管理和多版本 API 文档展示
10. 编写使用文档和示例，说明如何配置和使用文档生成功能

## 题目方向
业务逻辑

## 代码量估算
Hard: ≥300行多文件

## 技术栈广度
Hard: 跨技术栈≥3种（Python、Flask、OpenAPI、Swagger、AST 解析）

## 优化要求
Hard: 极致性能/资源优化（文档生成性能）

## 人工开发耗时预估
Hard: ≥4小时
