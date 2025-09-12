import asyncio
async def A(): print("A"); await asyncio.sleep(1)
async def wait_util_time(time):
    for i in range(time):
        await asyncio.sleep(1)
        
asyncio.run(A())
asyncio.run(wait_util_time(10))