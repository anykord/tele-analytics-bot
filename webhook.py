# Simple aiohttp webhook receiver for Tribute payments
import json
import logging
from aiohttp import web
import config
from db import DB

db = DB(config.DB_PATH)
routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.post('/webhook/tribute')
async def tribute_webhook(request):
    try:
        data = await request.json()
    except Exception:
        data = await request.post()
    secret = request.headers.get("X-TRIBUTE-SECRET") or request.query.get("secret")
    if secret != config.TRIBUTE_SECRET:
        logger.warning("Bad tribute secret")
        return web.Response(status=403, text="forbidden")
    user_id = int(data.get("user_id"))
    plan = data.get("plan")
    db.set_plan(user_id, plan)
    logger.info(f"Activated plan {plan} for {user_id}")
    return web.Response(text="ok")

def run_app():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=8000)

if __name__ == "__main__":
    run_app()
