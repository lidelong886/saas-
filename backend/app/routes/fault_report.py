"""
故障报修路由
"""
from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required

from ..utils.auth_helpers import get_current_user_id
from ..models.fault_report import FaultReport
from ..models import Station, User
from ..utils.response import success_response, error_response, paginate_response

fault_report_bp = Blueprint('fault_report', __name__)


@fault_report_bp.route('', methods=['POST'])
@jwt_required()
def submit_fault_report():
    """提交故障报修"""
    try:
        data = request.get_json()
        user_id = get_current_user_id()

        fault_type = data.get('fault_type')
        description = data.get('description', '').strip()
        images = data.get('images', [])
        station_id = data.get('station_id')
        battery_id = data.get('battery_id')
        contact_phone = data.get('contact_phone')

        if fault_type not in ('battery', 'cabinet', 'station', 'other'):
            return error_response('故障类型不正确', 400)

        if not description or len(description) < 10:
            return error_response('故障描述至少10个字符', 400)

        if len(description) > 200:
            return error_response('故障描述不能超过200个字符', 400)

        if not contact_phone:
            user = User.get_by_id(user_id)
            if user:
                contact_phone = user.phone

        report = FaultReport(
            user_id=user_id,
            station_id=station_id,
            battery_id=battery_id,
            fault_type=fault_type,
            description=description,
            images=images,
            contact_phone=contact_phone
        )
        report.save()

        return success_response({
            'report_no': report.report_no,
            'id': report.id
        }, '报修提交成功')

    except Exception as e:
        return error_response(f'提交报修失败: {str(e)}', 500)


@fault_report_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_fault_reports():
    """获取我的报修列表"""
    try:
        user_id = get_current_user_id()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = FaultReport.query.filter_by(
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).order_by(FaultReport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return paginate_response(
            [r.to_dict() for r in pagination.items],
            {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            },
            '获取报修列表成功'
        )

    except Exception as e:
        return error_response(f'获取报修列表失败: {str(e)}', 500)


@fault_report_bp.route('/<report_no>', methods=['GET'])
@jwt_required()
def get_fault_report_detail(report_no):
    """获取报修详情"""
    try:
        user_id = get_current_user_id()

        report = FaultReport.query.filter_by(
            report_no=report_no,
            user_id=user_id,
            tenant_id=g.tenant_id,
            is_deleted=False
        ).first()

        if not report:
            return error_response('报修记录不存在', 404)

        return success_response(report.to_dict(), '获取报修详情成功')

    except Exception as e:
        return error_response(f'获取报修详情失败: {str(e)}', 500)
