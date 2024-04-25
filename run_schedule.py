from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

# ON_DAYS = 'mon,tue,wed,thu,fri,sat,sun' # Every day
ON_DAYS = 'sat'

AT_HOUR = 5
AT_MINUTE = 15

def run_arrow_scraper():
    subprocess.call(["scrapy", "crawl", "arrow_spider"])

sched = BlockingScheduler()

sched.add_job(run_arrow_scraper, 'cron', day_of_week=ON_DAYS, hour=AT_HOUR, minute=AT_MINUTE)
sched.start()
