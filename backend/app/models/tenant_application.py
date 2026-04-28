"""
租户入驻申请模型
"""
from .base import BaseModel
from .. import db


class TenantApplication(BaseModel):
    """小程序端提交的运营商/租户入驻申请"""
    __tablename__ = 'tenant_applications'

    applicant_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='申请用户ID')
    name = db.Column(db.String(100), nullable=False, comment='公司/个人名称')
    contact_name = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    city = db.Column(db.String(100), comment='意向城市')
    fund_level = db.Column(db.String(50), comment='预计投入资金')
    message = db.Column(db.String(500), comment='留言')
    status = db.Column(db.String(20), default='pending', comment='状态 pending/approved/rejected')
    review_remark = db.Column(db.String(500), comment='审核备注')
    approved_tenant_id = db.Column(db.Integer, comment='审批创建的租户ID')

    applicant = db.relationship('User', backref='tenant_applications')
