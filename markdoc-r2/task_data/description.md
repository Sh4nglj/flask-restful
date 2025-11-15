# 任务 Prompt

为 Flask-RESTful 实现自定义 XML 表示器功能，具体需求如下：
1. 在 flask_restful/representations 目录下创建 xml.py 模块，实现 output_xml 函数
2. output_xml 函数应接受 data、code、headers 三个参数，将 Python 字典/列表转换为 XML 格式
3. XML 输出应支持嵌套结构，正确处理字典、列表和基本数据类型
4. 实现 XML 命名空间支持，允许用户自定义根元素名称和命名空间
5. 在 Api 类中添加注册 XML 表示器的方法，支持 'application/xml' 和 'text/xml' 两种 MIME 类型
6. 确保 XML 输出符合 XML 1.0 标准，正确处理特殊字符转义（<、>、&、'、"）
7. 添加配置选项，允许用户自定义 XML 根元素名称、缩进格式和编码方式
8. 编写完整的单元测试，覆盖各种数据结构（嵌套字典、列表、混合类型）
9. 更新文档，说明如何使用 XML 表示器
10. 确保与现有的 JSON 表示器兼容，不影响现有功能

## 题目方向
业务逻辑

## 代码量估算
Hard: ≥300行多文件

## 技术栈广度
Hard: 跨技术栈≥3种（Python、XML、Flask、测试框架）

## 优化要求
Hard: 极致性能/资源优化（XML 序列化性能、内存使用）

## 人工开发耗时预估
Hard: ≥4小时
