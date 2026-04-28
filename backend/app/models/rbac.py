"""
RBAC 模型
"""
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from .. import db


admin_user_roles = db.Table(
    'admin_user_roles',
    db.Column('admin_user_id', db.Integer, db.ForeignKey('admin_users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)


class Permission(BaseModel):
    """权限模型"""
    __tablename__ = 'permissions'

    code = db.Column(db.String(100), nullable=False, unique=True, comment='权限编码')
    name = db.Column(db.String(100), nullable=False, comment='权限名称')
    module = db.Column(db.String(50), nullable=False, comment='所属模块')
    action = db.Column(db.String(50), nullable=False, comment='动作')
    description = db.Column(db.String(255), comment='权限说明')


class Role(BaseModel):
    """角色模型"""
    __tablename__ = 'roles'

    code = db.Column(db.String(50), nullable=False, unique=True, comment='角色编码')
    name = db.Column(db.String(100), nullable=False, comment='角色名称')
    scope = db.Column(db.String(20), default='tenant', comment='作用域 tenant/system')
    description = db.Column(db.String(255), comment='角色描述')

    permissions = db.relationship(
        'Permission',
        secondary=role_permissions,
        lazy='subquery',
        backref=db.backref('roles', lazy=True)
    )

    def to_dict(self):
        data = super().to_dict()
        data['permissions'] = [p.code for p in self.permissions]
        return data


class AdminUser(BaseModel):
    """后台管理员模型"""
    __tablename__ = 'admin_users'

    username = db.Column(db.String(50), nullable=False, unique=True, comment='用户名')
    phone = db.Column(db.String(20), nullable=False, unique=True, comment='手机号')
    email = db.Column(db.String(120), comment='邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(50), comment='昵称')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    is_super_admin = db.Column(db.Boolean, default=False, comment='是否系统超管')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')

    roles = db.relationship(
        'Role',
        secondary=admin_user_roles,
        lazy='subquery',
        backref=db.backref('admin_users', lazy=True)
    )

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, code):
        if self.is_super_admin:
            return True
        return any(code == perm.code for role in self.roles for perm in role.permissions)

    def to_dict(self):
        data = super().to_dict()
        data.pop('password_hash', None)
        data['roles'] = [role.code for role in self.roles]
        data['permissions'] = sorted({perm.code for role in self.roles for perm in role.permissions})
        return data
