import asyncio, httpx, pydantic, logging, uvicorn
from fastapi import FastAPI, Request
from uuid import uuid4

answers = {}
app = FastAPI()

class Task(pydantic.BaseModel):
    id_: str = str(uuid4())
    status: str = "running"
    result: dict = {}

async def get_code(lnk):
    async with httpx.AsyncClient() as client:
        resp = await client.get(lnk)
        return resp.status_code

async def get_codes(urls, curuuid):
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for lnk in urls:
            tasks.append(tg.create_task(get_code(lnk)))
    for url, task in zip(urls, tasks):
        answers[curuuid]["result"][url] = task.result()
    answers[curuuid]["status"] = "ready"

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
    uvicorn.run(
        'server:app',
        host='127.0.0.1',
        port=8888,
        log_level='info',
        loop='asyncio'
    )