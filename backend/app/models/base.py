"""
基础模型类
"""
from datetime import datetime
from flask import g
from .. import db

class BaseModel(db.Model):
    """
    基础模型类，包含所有模型的公共字段和方法
    """
    __abstract__ = True

    # 基础字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    tenant_id = db.Column(db.Integer, default=1, nullable=False, comment='租户ID')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果有租户ID，从g对象获取
        if hasattr(g, 'tenant_id'):
            self.tenant_id = g.tenant_id

    def to_dict(self):
        """
        转换为字典格式
        """
        from decimal import Decimal
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, Decimal):
                value = float(value) if value is not None else None
            result[column.name] = value
        return result

    def update_from_dict(self, data_dict):
        """
        从字典更新模型
        """
        for key, value in data_dict.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'updated_at', 'is_deleted']:
                setattr(self, key, value)

    @classmethod
    def get_by_id(cls, id):
        """
        根据ID获取记录
        """
        tenant_id = getattr(g, 'tenant_id', 1)
        return cls.query.filter_by(id=id, tenant_id=tenant_id, is_deleted=False).first()

    @classmethod
    def get_list(cls, page=1, per_page=20, filters=None, order_by=None):
        """
        获取列表，支持分页、筛选、排序
        """
        tenant_id = getattr(g, 'tenant_id', 1)
        query = cls.query.filter_by(tenant_id=tenant_id, is_deleted=False)

        # 应用筛选条件
        if filters:
            for key, value in filters.items():
                if hasattr(cls, key):
                    query = query.filter(getattr(cls, key) == value)

        # 应用排序
        if order_by:
            query = query.order_by(order_by)
        else:
            query = query.order_by(cls.created_at.desc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    def soft_delete(self):
        """
        软删除
        """
        self.is_deleted = True
        db.session.commit()

    def save(self):
        """
        保存到数据库
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        更新到数据库
        """
        db.session.commit()

