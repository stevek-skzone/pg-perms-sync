from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

# Configure Redis as the job store
jobstores = {
    "redis": RedisJobStore(host="localhost", port=6379, db=1)
}

# Create a background scheduler with Redis as the job store
scheduler = AsyncIOScheduler(jobstores=jobstores)

# # Schedule the task to run on startup
# scheduler.add_job(call_api, "date")

# # Schedule the task to run every 15 minutes
# scheduler.add_job(call_api, "interval", minutes=15)

# # Start the scheduler
# scheduler.start()