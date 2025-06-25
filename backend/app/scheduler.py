from apscheduler.schedulers.background import BackgroundScheduler
from .market_scan import generate_daily_report
from .config import settings

def start_scheduler(api_key, demo=True):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: generate_daily_report(
            api_key,
            demo,
            do_auto_trade=settings.auto_trade_enabled,
            trade_amount=settings.trade_amount
        ),
        'cron',
        hour=0,
        minute=10
    )
    scheduler.start()
    return scheduler