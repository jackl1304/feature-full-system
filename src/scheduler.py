import os, asyncio, logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fetcher.manager import load_plugins
from models.db import init_db, get_session
from models.log import FetchLog
from utils.scraper import human_fetch
from renderer.email import render_newsletter
from sender.mail import send_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

async def job():
    load_dotenv()
    init_db()
    session = next(get_session())

    specs = os.getenv("SOURCE_SPECS", "").split(";")
    all_items = []
    for spec in specs:
        module, cls, selector = spec.split("|")
        items = await human_fetch(module, selector)
        all_items.extend(items)
        # Log erstellen
        log = FetchLog(source_spec=spec, status="success", details=str(len(items)))
        session.add(log)
    session.commit()

    # speichern und senden analog vorher, mark_as_sent etc. 

def start_scheduler():
    sched = AsyncIOScheduler()
    interval = int(os.getenv("POLL_INTERVAL_MINUTES", 15))
    sched.add_job(job, "interval", minutes=interval, next_run_time=datetime.now())
    sched.start()
    asyncio.get_event_loop().run_forever()
