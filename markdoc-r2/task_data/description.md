# 任务 Prompt

修复 Flask-RESTful CORS 装饰器在特定场景下的边界情况错误，具体需求如下：
1. 修复当 origin 参数为 '*' 且 credentials=True 时，浏览器拒绝请求的问题（CORS 规范不允许同时使用）
2. 修复当 methods 参数为 None 时，get_methods 函数可能返回 None 导致响应头错误的问题
3. 修复当 request.method 为 OPTIONS 且 automatic_options=False 时，CORS 头未正确设置的问题
4. 修复当 headers 参数包含小写字母时，某些浏览器无法识别的问题（需要统一转换为大写）
5. 修复当 max_age 为 0 时，响应头格式错误的问题
6. 修复当多个 CORS 装饰器叠加使用时，响应头重复或冲突的问题
7. 修复当 origin 为列表且包含通配符时，origin 匹配逻辑错误的问题
8. 添加对预检请求（OPTIONS）的完整支持，确保所有必要的 CORS 头都被设置
9. 实现动态 origin 验证，支持基于正则表达式的 origin 白名单
10. 编写测试用例，覆盖所有边界情况和 CORS 规范要求

## 题目方向
运行时异常修复

## 代码量估算
Medium: 50-300行

## 技术栈广度
Medium: 单一框架/语言（Python/Flask/HTTP）

## 优化要求
Medium: 基础优化

## 人工开发耗时预估
Medium: 1-4小时
