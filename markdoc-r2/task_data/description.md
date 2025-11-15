# 任务 Prompt

修复 Flask-RESTful RequestParser 在处理嵌套参数和边界情况时的运行时异常，具体需求如下：
1. 修复当 location 参数为元组且包含 'json' 时，解析嵌套 JSON 对象（如 {'user': {'name': 'test'}}）时出现的 AttributeError
2. 修复当参数类型为 FileStorage 且值为 None 时，convert 方法可能引发的 TypeError
3. 修复当 choices 参数为生成器或迭代器时，多次迭代导致的空值问题
4. 修复当 source 方法返回的 MultiDict 为空时，required 参数验证逻辑错误
5. 修复当 action='append' 且 location 包含多个位置时，值重复追加的问题
6. 修复当 trim=True 且值为非字符串类型时，strip 方法调用失败的问题
7. 修复当 nullable=False 且 default=None 时，参数验证逻辑不一致的问题
8. 添加对嵌套参数路径的支持（如 'user.name'），正确解析深层嵌套的 JSON 数据
9. 增强错误消息，当参数解析失败时提供更详细的上下文信息（参数位置、期望类型等）
10. 编写测试用例覆盖所有修复的边界情况，确保向后兼容性

## 题目方向
运行时异常修复

## 代码量估算
Medium: 50-300行

## 技术栈广度
Medium: 单一框架/语言（Python/Flask）

## 优化要求
Medium: 基础优化

## 人工开发耗时预估
Medium: 1-4小时
