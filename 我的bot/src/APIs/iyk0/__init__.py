from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from os.path import join,dirname

import json,re,asyncio,aiohttp

from . import getData
apiDict = getData.apiDict

imgLabels = {"img","nocLogo","face","top_photo","live_cover","cover","imgurl","icon","img1","img2","SongPic","avatarUrl","avatar","card","imageUrl"}
splitLabels = {"data","data_img","forecast","ganmao",}
speclabels = imgLabels|splitLabels
ignoreLables = {"code","tips","gq","near_danmaku","msg","city","wendu","状态码","状态","status","api","ftime"}
retainLables = {"baidu","sogou","haoso"}

ignoreArgs = {"type","sum","return"}


callAPI = on_command("iyk0",priority=5)

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
        elif apiDict[apiName]['状态']=="维护":
            await callAPI.finish("该接口正在维护")
        elif apiDict[apiName]['状态']=="正常":
            state |= apiDict[apiName]["详细"]
            state["args"] = args
            state["api"] = apiName
            await output(state,True)
    else:
        await send([
            "可用的API名称：\n\n"+"\n".join(apiDict),
            "输入格式：\n/iyk0 API名称 参数1 参数2 ...",
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
    url = state["接口地址"]+'?'+'&'.join(f"{i[0]}={v}" for i,v in zip(state["请求参数"],state["args"]))
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
    if ext=="TXT":
        text = re.sub('(http.*?)[.](jpg|png|gif|jpeg)',lambda u:f'[CQ:image,file={u.group()}]',text)
        if done or text[-1]=="1":
            return text.replace("提示：发送以上序号选择，例：选 1",'').strip()
        
    elif ext=="JSON":
        text = text.replace("提示：发送以上序号选择，例：选 1",'').replace('"{"version":1}"','""')
        for i in state["返回参数"]:
            if i[0] not in speclabels:
                text = text.replace(f'"{i[0]}"',f'"{i[2]}"').replace('"url"','"链接"')
        if text:
            try:
                r = process_data(json.loads(preprocess(text)),state["返回参数"])
                if r:
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
    elif ext=="HTML":
        text = re.sub("\[img=(.*?)\]",lambda u:f"[CQ:image,file={u.group(1)}]",text)
        return text.strip().replace("<br>",'')
    elif ext=="MP3":
        return re.sub("(http.*?)[.](mp3)",lambda u:f'[CQ:record,file={u.group()}]',text)
    elif ext=="TXT/JSON" or ext=="JSON/TXT":
        for i in state["返回参数"]:
            if i[0] not in speclabels:
                text = text.replace(f'"{i[0]}"',f'"{i[2]}"')
        try:
            r = json.loads(text)
        except:
            return text
        else:
            return process_data(r)
    elif ext=="HTML/JSON":
        try:
            return process_data(json.loads(text))
        except:
            from bs4 import BeautifulSoup
            text = "\n".join(BeautifulSoup(await resp.read(),"html.parser").strings)
            text = re.sub("±img=(.*?)±",lambda u:f"[CQ:image,file={u.group(1)}]",text.replace("±img=±",""))
            return text.split("\n")
    elif ext=="无":
        if done:
            return url
    else:
        print(ext)
        print(text)
        return text




def argInfo(state):
    d,s = {"是":"必填","否":"选填"},len(state["args"])
    return "\n".join(f"参数{i}({d[arg[1]]})：{arg[3]}" for i,arg in enumerate(state["请求参数"][s:],s+1) if arg[0] not in ignoreArgs or arg[1]=="是")


async def send(out):
    if out:
        if isinstance(out,str):
            try:
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
    n = len([arg for arg in state["请求参数"] if arg[0] not in ignoreArgs or arg[1]=="是"])
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


def process_data(j,ignore=True):
    if isinstance(j,list):
        return [process_data(i,False) for i in j]
    elif isinstance(j,dict):
        for k in imgLabels:
            if k in j and j[k]:
                if j[k][-1]!="]":
                    j[k]=f'[CQ:image,file={j[k]}]'
        for i in splitLabels:
            if i in j:
                d = process_data(j.pop(i))
                r = process_data(j)
                if isinstance(d,list) and r:
                    return [r]+d
                else:
                    return d
        if any(isinstance(v,list) or isinstance(v,dict) for v in j.values()):
            try:
                return ["\n".join([f"{k}:"]+process_data(v)) if isinstance(v,list) else process_data(v) if isinstance(v,dict) else f"{k}:{str(process_data(v))[2:-2]}" for k,v in j.items() if k not in ignoreLables or k in retainLables]
            except Exception as e:
                return print(e)
        if ignore:
            return "\n".join(v if k in imgLabels else f"{k}:{v}" for k,v in j.items() if (not 65<=ord(k[-1])<=122 or k in imgLabels) and k not in ignoreLables or k in retainLables)
        else:
            return "\n".join(str(v) if 65<=ord(k[-1])<=122 else f"{k}:{v}" for k,v in j.items() if k not in ignoreLables)
    elif isinstance(j,str):
        return [j.replace(";","\n")]
    else:
        return str(j)
