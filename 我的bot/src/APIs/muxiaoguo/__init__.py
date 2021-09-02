from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from os.path import join,dirname
from pprint import pprint

import json,re,asyncio,aiohttp

from .getData import apiDict

imgLabels = {"imageurl","imgurl","songPic","avatar","ImgUrl","albumPicurl","OlympicCommitteeImg","icon","imagelink","视频封面","用户头像链接","smallLogo","xiaoyaGradeIcon","歌曲封面","用户头像"}
splitLabels = {"data","cities"}
speclabels = imgLabels|splitLabels
ignoreLables = {"code","msg"}
retainLables = {}

ignoreArgs = {'返回类型 json，img (img类型会直接跳转)':"json"}

callAPI = on_command("muxiaoguo",priority=5)

def get_input(event):
    return ["" if a=="\\" else a for a in str(event.message).replace("&amp;","&").replace("&#91;","[").replace("&#93;","]").split()]


@callAPI.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = get_input(event)
    # args = [re.sub("&#.*?;",lambda u:chr(int(u.group()[2:-1])),a) for a in args]
    print(args)
    if args:
        apiName, *args = args
        if apiName not in apiDict:
            await callAPI.finish("输入的API不存在")
        else:
            state |= apiDict[apiName]["详细"]
            state["args"] = args
            state["api"] = apiName
            for i,a in enumerate(state["请求参数"]):
                if a[-1] in ignoreArgs:
                    args.insert(i,ignoreArgs[a[-1]])
            await output(state,True)
    else:
        await send([
            "可用的API名称：\n\n"+"\n".join(apiDict),
            "输入格式：\n/muxiaoguo API名称 参数1 参数2 ...",
            "多参数可用空格分隔一次性填写，也可以分成多条消息，输入'\\'表示跳过该参数",
            f"使用举例：\n[CQ:image,file=file:///{join(dirname(__file__),'使用举例1.jpg')}][CQ:image,file=file:///{join(dirname(__file__),'使用举例2.jpg')}]"])
        await callAPI.finish()

@callAPI.receive()
async def got_argsInfo(bot: Bot, event: Event, state: T_State):
    args = get_input(event)
    if args[0]=="退出":
        await callAPI.finish("完成")
    else:
        state["args"].extend(args)
        await output(state)
    
def preprocess(text):
    if "{" in text or "[" in text:
        if text[0] not in "{[":
            text = "\n".join(text.split("\n")[1:])
            return preprocess(text)
        elif text[-1] not in "]}":
            text = "\n".join(text.split("\n")[:-1])
            return preprocess(text)
        else:
            try:
                json.loads(text)
            except:
                return "[{}]".format(','.join(text.split('\n')))
            else:
                return text
    else:
        return text

async def get_output(state,done=False):
    url = state["接口地址"]+'?'+'&'.join(f"{i[0]}={ignoreArgs[i[-1]]}" if i[-1] in ignoreArgs else f"{i[0]}={v}" for i,v in zip(state["请求参数"],state["args"]))#'&'.join(f"{a}={ignoreArgs[a]}" for a in set(a[0] for a in state["请求参数"])&set(ignoreArgs))
    print(url)
    ext = state["返回格式"].upper()
    if ext in ["IMG","PNG","JPG"]:
        if done:
            return f'[CQ:image,file={url},cache=0]'
        else:
            return 
    else:
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(url,timeout=30)
                text = await resp.text()
        except:
            return "获取失败"
        text = re.sub('<!\[CDATA\[(.*?)\]\]>',lambda u:u.group(1),text.strip())
    if ext=="JSON":
        for i in state["返回参数"]:
            if i[0] not in speclabels:
                text = text.replace(f'"{i[0]}"',f'"{i[2]}"').replace('"url"','"链接"')
        if text:
            try:
                r = process_data(json.loads(preprocess(text)),state["返回参数"])
                if r and r!="None":
                    return r
            except Exception as e:
                pass
        if done:
            try:
                data = await resp.json()
                return data["msg"]
            except:
                try:
                    data = await resp.json()
                    return data["data"]["msg"]
                except:
                    return text
    else:
        print(ext)
        print(text)
        return text




def argInfo(state):
    d,s = {"是":"必填","否":"选填"},len(state["args"])
    return "\n".join(f"参数{i}({d[arg[1]]})：{arg[3]}" for i,arg in enumerate(state["请求参数"][s:],s+1) if arg[0] not in ignoreArgs)


async def send(out):
    if out:
        if isinstance(out,str):
            try:
                print(out)
                await callAPI.send(Message(out))
            except Exception as e:
                print(e)
                await callAPI.finish('获取失败')
        elif isinstance(out,list):
            for o in out:
                await send(o)
                await asyncio.sleep(0.1)
        

async def output(state,first=False):
    print(state["args"],state["请求参数"])
    n = len(state["请求参数"])
    out = await get_output(state,len(state["args"])==n)
    if len(state["args"])>n:
        await callAPI.finish("参数过多！")
    elif len(state["args"])==n:
        await send(out)
        await callAPI.finish()
        # await callAPI.finish("完成")
    if out:
        await send(out)
    if state["args"] and not first:
        await callAPI.reject("请输入以下参数(多参数可用空格分隔一次性填写，也可以分成多条消息，输入'\\'表示跳过该参数)：\n"+argInfo(state))
    else:
        await callAPI.send("请输入以下参数(多参数可用空格分隔一次性填写，也可以分成多条消息，输入'\\'表示跳过该参数)：\n"+argInfo(state))


def process_data(j,ignore=True,split=True):
    if isinstance(j,list):
        return [process_data(i,False,split) for i in j]
    elif isinstance(j,dict):
        for k in imgLabels:
            if k in j and j[k]:
                if j[k][-1]!="]":
                    if "," in j[k]:
                        j[k] = j[k].split("?")[0]
                    j[k]=f'[CQ:image,file={j[k]}]'
        for i in splitLabels:
            if i in j:
                d = j.pop(i)
                d = process_data(d,ignore,isinstance(d,dict))
                r = process_data(j)
                if isinstance(d,list) and r:
                    return [r]+d
                else:
                    return d
        
        l = [v if k in imgLabels or all(map(lambda c:65<=ord(c)<=122,k)) and ignore else f"{k}:{v}" for k,v in j.items() if k not in ignoreLables or k in retainLables]
        l = [v if v else "None" for v in l]
        if not any(isinstance(v,list) or isinstance(v,dict) for v in j.values()):
            return "\n".join(l)
        elif split:
            l = [f"{k}:\n{process_data(v,False,False)}" if "\n" in process_data(v,False,False) else f"{k}:{v}" for k,v in j.items() if not isinstance(v,list)]
            for k,v in j.items():
                if isinstance(v,list):
                    l.extend([k]+process_data(v,ignore,False))
            return l
        else:
            return "\n".join(l)
    elif isinstance(j,str):
        return j
    else:
        return str(j)
