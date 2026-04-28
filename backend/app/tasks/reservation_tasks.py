"""
预约定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from ..services.rider_service import RiderService


reservation_scheduler = BackgroundScheduler()


def _check_expired_reservations_job(app):
    """扫描并处理超时预约"""
    with app.app_context():
        timeout_count = RiderService.check_reservation_timeout()
        if timeout_count > 0:
            app.logger.info(f'自动处理超时预约数量: {timeout_count}')


def init_reservation_scheduler(app):
    """
    初始化预约任务调度器
    """
    if reservation_scheduler.running:
        return

    # 每分钟检查一次超时预约
    interval_seconds = app.config.get('RESERVATION_TIMEOUT_SCAN_INTERVAL_SECONDS', 60)
    reservation_scheduler.add_job(
        func=_check_expired_reservations_job,
        trigger=IntervalTrigger(seconds=interval_seconds),
        args=[app],
        id='check_expired_reservations',
        replace_existing=True
    )
    reservation_scheduler.start()
    app.logger.info('预约超时扫描任务已启动')
