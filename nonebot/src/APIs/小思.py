from nonebot import on_startswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
import aiohttp


mode = 1    #0:语音 1:文字

robot = on_startswith("小思小思")

async def talk(msg):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.ownthink.com/bot?spoken={msg}") as r:
            data = await r.json(content_type=None)
    return data["data"]["info"]["text"]

async def getOutput(msg):
    output = await talk(msg)
    print(output)
    if mode:
        return output
    else:
        return Message(f"[CQ:tts,text={output}]")

@robot.handle()
async def handle_first_receive(bot:Bot, event:Event, state:T_State):
    await robot.send(await getOutput(str(event.get_message())))

@robot.receive()
async def got_text(bot:Bot, event:Event, state:T_State):
    msg = str(event.get_message())
    for i in ["再见","退出"]:
        if i in msg:
            await robot.send(await getOutput(msg))
            await robot.finish("已退出")
    global mode
    if msg=="文字模式":
        mode = 1
        await robot.reject("已切换到文字模式")
    elif msg=="语音模式":
        mode = 0
        await robot.reject("已切换到语音模式")
    else:
        await robot.reject(await getOutput(msg))