import asyncio
import json
import httpx
import sys


async def main(urls: list[str]):
    async with httpx.AsyncClient() as client:
        r = await client.post('http://localhost:8888/api/v1/tasks/', json=urls)
        task = json.loads(r.text)
        print(task['id_'])
        while True:
            r = await client.get(
                'http://localhost:8888/api/v1/tasks/' + task['id_']
            )
            res = json.loads(r.text)
            if res['status'] == 'ready':
                for r in res['result']:
                    print(res['result'][r], r, sep="\t")
                break
            await asyncio.sleep(2)


if __name__ == "__main__":
    urls = sys.argv[1:]
    asyncio.run(main(urls))

