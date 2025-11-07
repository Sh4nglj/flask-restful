from flask import request
from sqlalchemy import or_, and_

class Filtering:
    def __init__(self, query, model, allowed_fields=None):
        self.query = query
        self.model = model
        self.allowed_fields = allowed_fields or []
        self.filters = self._parse_filters()
        self.sorting = self._parse_sorting()
        self.optimized = False

    def _parse_filters(self):
        # 解析过滤参数：?filter[field][operator]=value
        filters = []
        for key, value in request.args.items():
            if key.startswith('filter['):
                # 解析字段名和操作符
                parts = key.split('[')
                field_name = parts[1].rstrip(']')
                if len(parts) > 2:
                    operator = parts[2].rstrip(']')
                else:
                    operator = 'eq'  # 默认精确匹配

                # 检查字段是否允许过滤
                if self.allowed_fields and field_name not in self.allowed_fields:
                    continue

                # 获取模型字段
                field = getattr(self.model, field_name, None)
                if field is None:
                    continue

                # 解析多值筛选
                values = value.split(',')

                # 根据操作符创建过滤条件
                filter_cond = self._create_filter_condition(field, operator, values)
                if filter_cond:
                    filters.append(filter_cond)
        return filters

    def _create_filter_condition(self, field, operator, values):
        # 创建过滤条件
        if operator == 'eq':
            if len(values) > 1:
                return field.in_(values)
            else:
                return field == values[0]
        elif operator == 'ne':
            if len(values) > 1:
                return ~field.in_(values)
            else:
                return field != values[0]
        elif operator == 'like':
            return or_(*[field.like(f'%{v}%') for v in values])
        elif operator == 'ilike':
            return or_(*[field.ilike(f'%{v}%') for v in values])
        elif operator == 'gt':
            return field > values[0]
        elif operator == 'gte':
            return field >= values[0]
        elif operator == 'lt':
            return field < values[0]
        elif operator == 'lte':
            return field <= values[0]
        elif operator == 'between':
            if len(values) == 2:
                return field.between(values[0], values[1])
        return None

    def _parse_sorting(self):
        # 解析排序参数：?sort=name,-created_at
        sorting = []
        sort_param = request.args.get('sort')
        if sort_param:
            sort_fields = sort_param.split(',')
            for field_str in sort_fields:
                field_str = field_str.strip()
                if not field_str:
                    continue
                if field_str.startswith('-'):
                    field_name = field_str[1:]
                    direction = 'desc'
                else:
                    field_name = field_str
                    direction = 'asc'

                # 检查字段是否允许排序
                if self.allowed_fields and field_name not in self.allowed_fields:
                    continue

                # 获取模型字段
                field = getattr(self.model, field_name, None)
                if field is None:
                    continue

                # 添加排序条件
                if direction == 'desc':
                    sorting.append(field.desc())
                else:
                    sorting.append(field.asc())
        return sorting

    def optimize_query(self):
        # 优化查询：检测冗余或冲突的过滤条件
        if self.optimized:
            return

        # 简单的优化示例：移除重复的过滤条件
        unique_filters = []
        seen = set()
        for filter_cond in self.filters:
            filter_str = str(filter_cond)
            if filter_str not in seen:
                seen.add(filter_str)
                unique_filters.append(filter_cond)
        self.filters = unique_filters

        self.optimized = True

    def apply(self):
        # 应用过滤和排序
        self.optimize_query()

        # 应用过滤条件
        if self.filters:
            self.query = self.query.filter(and_(*self.filters))

        # 应用排序
        if self.sorting:
            self.query = self.query.order_by(*self.sorting)

        return self.query

def filterable(allowed_fields=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 调用原始函数获取查询对象和模型
            result = func(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                query, model = result
            else:
                # 假设函数返回查询对象，模型可以从查询中获取
                query = result
                model = query._entities[0].entity if hasattr(query, '_entities') else query.model

            # 创建过滤对象
            filtering = Filtering(query, model, allowed_fields)

            # 应用过滤和排序
            filtered_query = filtering.apply()

            return filtered_query
        return wrapper
    return decorator