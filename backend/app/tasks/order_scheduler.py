"""
订单定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from ..services.order_service import OrderService


scheduler = BackgroundScheduler()


def _cancel_expired_pending_orders_job(app):
    """扫描并取消超时未支付订单"""
    with app.app_context():
        timeout_minutes = app.config.get('ORDER_PENDING_TIMEOUT_MINUTES', 15)
        cancelled_count = OrderService.cancel_expired_pending_orders(timeout_minutes)
        if cancelled_count > 0:
            app.logger.info(f'自动取消超时订单数量: {cancelled_count}')


def init_order_scheduler(app):
    """
    初始化订单任务调度器
    """
    if scheduler.running:
        return

    interval_seconds = app.config.get('ORDER_TIMEOUT_SCAN_INTERVAL_SECONDS', 60)
    scheduler.add_job(
        func=_cancel_expired_pending_orders_job,
        trigger=IntervalTrigger(seconds=interval_seconds),
        args=[app],
        id='cancel_expired_pending_orders',
        replace_existing=True
    )
    scheduler.start()
    app.logger.info('订单超时扫描任务已启动')
