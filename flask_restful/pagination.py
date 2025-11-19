from flask import request, url_for
from math import ceil

class Pagination:
    def __init__(self, query, resource, resource_args=None, resource_kwargs=None, page=None, per_page=None, offset=None, limit=None, cursor=None):
        self.query = query
        self.resource = resource
        self.resource_args = resource_args or []
        self.resource_kwargs = resource_kwargs or {}
        self.page = page
        self.per_page = per_page
        self.offset = offset
        self.limit = limit
        self.cursor = cursor
        self.total = query.count()
        self.items = []
        self.pagination_type = self._determine_pagination_type()
        self._paginate_query()

    def _determine_pagination_type(self):
        # 智能选择分页策略：数据量小于10000条时使用偏移量分页，大于时使用游标分页
        if self.total < 10000:
            return 'offset'
        else:
            return 'cursor'

    def _paginate_query(self):
        if self.pagination_type == 'offset':
            self._offset_paginate()
        else:
            self._cursor_paginate()

    def _offset_paginate(self):
        # 处理基于偏移量的分页
        if self.page is None:
            self.page = 1
        if self.per_page is None:
            self.per_page = 20
        if self.offset is not None:
            self.page = ceil((self.offset + 1) / self.per_page)
        if self.limit is not None:
            self.per_page = self.limit

        self.page = max(1, self.page)
        self.per_page = max(1, self.per_page)

        offset = (self.page - 1) * self.per_page
        self.items = self.query.offset(offset).limit(self.per_page).all()

        self.pages = ceil(self.total / self.per_page) if self.per_page > 0 else 0
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None

    def _cursor_paginate(self):
        # 处理基于游标的分页
        if self.limit is None:
            self.limit = 20
        if self.cursor is None:
            # 没有游标，获取第一页
            self.items = self.query.limit(self.limit).all()
        else:
            # 根据游标获取下一页
            # 假设游标是最后一个元素的ID
            self.items = self.query.filter(self.query.model.id > self.cursor).limit(self.limit).all()

        self.has_next = len(self.items) > 0
        self.next_cursor = self.items[-1].id if self.has_next else None

    def to_dict(self):
        data = {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            'meta': {
                'total': self.total,
                'pagination_type': self.pagination_type
            }
        }

        if self.pagination_type == 'offset':
            data['meta'].update({
                'page': self.page,
                'per_page': self.per_page,
                'pages': self.pages,
                'has_prev': self.has_prev,
                'has_next': self.has_next
            })

            # 添加导航链接
            data['links'] = {
                'self': self._url_for_page(self.page),
                'first': self._url_for_page(1),
                'last': self._url_for_page(self.pages)
            }

            if self.has_prev:
                data['links']['prev'] = self._url_for_page(self.prev_num)
            if self.has_next:
                data['links']['next'] = self._url_for_page(self.next_num)

        else:  # cursor-based
            data['meta'].update({
                'limit': self.limit,
                'has_next': self.has_next
            })

            # 添加导航链接
            data['links'] = {
                'self': self._url_for_cursor(self.cursor)
            }

            if self.has_next:
                data['links']['next'] = self._url_for_cursor(self.next_cursor)

        return data

    def _url_for_page(self, page):
        return url_for(
            self.resource, 
            page=page, 
            per_page=self.per_page, 
            _external=True
        )

    def _url_for_cursor(self, cursor):
        return url_for(
            self.resource, 
            cursor=cursor, 
            limit=self.limit, 
            _external=True
        )

def paginate(func):
    def wrapper(*args, **kwargs):
        # 从请求参数中获取分页参数
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int)
        offset = request.args.get('offset', type=int)
        limit = request.args.get('limit', type=int)
        cursor = request.args.get('cursor', type=int)

        # 调用原始函数获取查询对象
        result = func(*args, **kwargs)
        if isinstance(result, tuple) and len(result) == 2:
            query, model = result
        else:
            query = result

        # 创建分页对象
        pagination = Pagination(
            query=query,
            resource=request.endpoint,
            resource_args=args,
            resource_kwargs=kwargs,
            page=page,
            per_page=per_page,
            offset=offset,
            limit=limit,
            cursor=cursor
        )

        return pagination.to_dict()
    return wrapper