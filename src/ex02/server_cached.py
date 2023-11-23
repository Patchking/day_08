import asyncio, httpx, pydantic, uvicorn, logging
from fastapi import FastAPI, Request
from redis import asyncio as aioredis
import redis
from uuid import uuid4



#----------- Options
answers = {}
app = FastAPI()


#----------- Pydamic models
class Task(pydantic.BaseModel):
    id_: str = str(uuid4())
    status: str = "running"
    result: dict = {}

async def get_code(lnk):
    async with httpx.AsyncClient() as client:
        resp = await client.get(lnk)
        return resp.status_code
    
async def delete_task(links, timeout):
    await asyncio.sleep(timeout)
    redis_connection = await aioredis.from_url("redis://localhost")
    for link in links:
        await redis_connection.delete(link)
    await redis_connection.close()
    
async def get_codes(urls, curuuid):
    redis_connection = await aioredis.from_url("redis://localhost")

    unkown_urls = []
    for url in urls:
        ret = await redis_connection.get(url)
        if ret is None:
            logging.info(f"site {url} is unkonwn.")
            unkown_urls.append(url)
        else:
            logging.info(f"site {url} is in redis.")
            answers[curuuid]["result"][url] = ret

    tasks = []
    async with asyncio.TaskGroup() as tg:
        for lnk in unkown_urls:
            tasks.append(tg.create_task(get_code(lnk)))
    for url, task in zip(unkown_urls, tasks):
        answers[curuuid]["result"][url] = task.result()
        await redis_connection.set(url, answers[curuuid]["result"][url])
    answers[curuuid]["status"] = "ready"
    await redis_connection.close()
    asyncio.create_task(delete_task(unkown_urls, 10))


@app.post("/api/v1/tasks/", status_code=201)
async def get_urls(request: Request):
    content_type = request.headers.get('Content-Type')
    if content_type is None:
        return 'No Content-Type provided.'
    elif content_type == 'application/json':
        urls = await request.json()
        task = Task()
        answers[task.id_] = {'status': task.status, 'result': task.result}
        if urls is None:
            return task
        asyncio.create_task(get_codes(urls, task.id_))
        return task
    else:
        return 'Content-Type not supported.'
    

@app.get("/api/v1/tasks/{received_task_id}")
async def check_task(received_task_id):
    if received_task_id not in answers:
        return {'id_': received_task_id, 'status': 'wrong_id'}
    return answers[received_task_id]

    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    redis_connection = redis.Redis()
    redis_connection.flushall()
    uvicorn.run(
        'server_cached:app',
        host='127.0.0.1',
        port=8888,
        log_level='info',
        loop='asyncio'
    )