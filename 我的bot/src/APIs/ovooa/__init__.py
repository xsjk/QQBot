from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from os.path import join,dirname
from pprint import pprint

import json,re,asyncio,aiohttp

from .getData import apiDict

IGNORE_OPTIONAL = False

imgLabels = {"图片链接",'Cover','image','img'}
videoLabels = {"视频链接"}
musicLabels = set()
splitLabels = {"data"}
speclabels = imgLabels|musicLabels|splitLabels
ignoreLables = {"code","msg","状态码"}
retainLables = {}

ignoreArgs = {"p","Skey","Pskey","format","bol"}
retainArgs = {"n","c"}

defaultArgs = {
    "输出方式默认json可选text/web/image":"image",
    "输出类型可填json/xml/text":"json",
    "默认json可选text":"json",
    "返回格式默认json可选text":"json",
    "输出格式默认json可选text":"json",
    "输出方式默认json可选text":"json",
    "提供Skey的账号":"",
    "换行符默认撇n":"",
    '输出类型mp3/amr/xml/json':"xml",
    "不填返回JSON格式有音频文件填tion返回文本":"json",
    "输出类型，为空时返回图片直链，为json时返回json格式，为all时返回标题+图片+地址+第几张，为1时返回标题+图片+地址":"all"
    }



callAPI = on_command("ovooa",priority=5)

def get_input(event):
    return ["" if a=="\\" else a.replace("_"," ") for a in str(event.message).replace("&amp;","&").replace("&#91;","[").replace("&#93;","]").split()]


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
            state["kargs"] = {}

            if "音乐" in apiName:
                state["kargs"]["type"] = "xml"
                for a in state["请求参数"]:
                    if a[0] in ["type","h","sc"]:
                        state["请求参数"].remove(a)

            for a in state["请求参数"]:
                if a[-1] in defaultArgs:
                    state["请求参数"].remove(a)
                    state["kargs"][a[0]] = defaultArgs[a[-1]]
            state["请求参数"] = [a for a in state["请求参数"] if (a[2]=="是" or a[0] in retainArgs or not IGNORE_OPTIONAL) and a[0] not in ignoreArgs]
            state["kargs"].update((k[0],v) for k,v in zip(state["请求参数"],args))

            print(state["kargs"])
            await output(state,True)
    else:
        await send([
            "可用的API名称：\n\n"+"\n".join(apiDict),
            "输入格式：\n/ovooa API名称 参数1 参数2 ...",
            "多参数可用空格分隔一次性填写，也可以分成多条消息，输入'\\'表示跳过该参数",
            "若参数中含有空格，请用下划线代替，否则将被识别为多个参数",
            "若在参数输完之前已经获得需要的到的结果，可输'退出'以结束",
            f"使用举例：\n[CQ:image,file=file:///{join(dirname(__file__),'使用举例1.jpg')}][CQ:image,file=file:///{join(dirname(__file__),'使用举例2.jpg')}]"])
        await callAPI.finish()

@callAPI.receive()
async def got_argsInfo(bot: Bot, event: Event, state: T_State):
    args = get_input(event)
    if args[0]=="退出":
        await callAPI.finish("完成")
    else:
        state["args"].extend(args)
        state["kargs"].update((k[0],v) for k,v in zip(state["请求参数"],state["args"]))
        await output(state)
    
def preprocess(text):
    # if "{" in text or "[" in text:
    #     if text[0] not in "{[":
    #         text = "\n".join(text.split("\n")[1:])
    #         return preprocess(text)
    #     elif text[-1] not in "]}":
    #         text = "\n".join(text.split("\n")[:-1])
    #         return preprocess(text)
    #     else:
    #         try:
    #             json.loads(text)
    #         except:
    #             return "[{}]".format(','.join(text.split('\n')))
    #         else:
    #             return text
    # else:
    #     return text
    return text

async def get_output(state,done=False):
    # url = state["请求地址"]+'?'+'&'.join(f"{i[0]}={v}" for i,v in zip(state["请求参数"],state["args"]))#'&'.join(f"{a}={ignoreArgs[a]}" for a in set(a[0] for a in state["请求参数"])&set(ignoreArgs))
    url = state["请求地址"]
    if done:
        url+='?'+'&'.join(f"{k}={v}" for k,v in state["kargs"].items())
    elif ("type","xml") in state["kargs"].items():
        url+='?'+'&'.join(f"{k}={v}" for k,v in state["kargs"].items() if k!="type")
    elif state["kargs"]:
        url+='?'+'&'.join(f"{k}={v}" for k,v in state["kargs"].items())

    print(url)
    ext = state["返回格式"].upper()
    if ext in ["IMG","JSON/TEXT/IMG"]:
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
            if done:
                return "获取失败"
            else:
                return
        text = re.sub("±img=(.*?)±",lambda u:f"[CQ:image,file={u.group(1)},cache=0]",text.replace("±img=±",""))
        text = re.sub('<!\[CDATA\[(.*?)\]\]>',lambda u:u.group(1),text.strip())
    if ext in ["JSON","JSON/TEXT","JSON/TEXT/IMG"]:
        if text[0]!="{":
            print("!")
            return text
        for i in state["返回参数"]:
            if i[0] not in speclabels:
                text = text.replace(f'"{i[0]}"',f'"{i[2]}"')
        if "url" not in [a[0] for a in state["返回参数"]]:
            text = text.replace('"url"','"链接"')

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
    elif ext=="JSON/TEXT/XML":
        i = text.find("<?xml")
        if i!=-1:
            text = text[i:].replace(',','&#44;').replace('[','&#91;').replace(']','&#93;')
            return f"[CQ:xml,data={text}]"
        for a in state["返回参数"]:
            if a[0] not in speclabels:
                text = text.replace(f'"{a[0]}"',f'"{a[2]}"')
        try:
            return process_data(json.loads(text))
        except:
            return text
    elif ext=="TEXT/JSON":
        if done:
            # if "img" in [a[0] for a in state["返回参数"]]:#随机视频API
            #     text = text.replace("url",'视频链接')
            for i in state["返回参数"]:
                if i[0] not in speclabels:
                    print("i",i)
                    text = text.replace(f'"{i[0]}"',f'"{i[2]}"')
            data =  process_data(json.loads(preprocess(text)),state["返回参数"])
            return data

    elif ext in ["TEXT","TEXT/IMG"]:
        if text[0] not in "<{":
            return text.replace("\\n","\n").replace("\\r","\n")
    elif ext=="HTML":
        if done:
            from urllib.parse import urlencode
            return state["请求地址"]+"?"+urlencode(state["kargs"])
    else:
        print(ext)
        print(text)
        return text




def argInfo(state):
    d,s = {"是":"必填","否":"选填"},len(state["args"])
    # return "\n".join(f"参数{i}({d[arg[2]]})：{arg[3]}" for i,arg in enumerate(state["请求参数"][s:],s+1) if arg[0] not in ignoreArgs)
    return "\n".join(f"参数{i}({d[arg[2]]})：{arg[3]}" for i,arg in enumerate(state["请求参数"][s:],s+1))



async def send(out):
    if out:
        if isinstance(out,str):
            try:
                print(out)
                try:
                    await callAPI.send(Message(out))
                except Exception as e:
                    if "\n" in out:
                        await send(out.split("\n"))
                    else:
                        await send(str(e))
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
        l = [process_data(i,False,split) for i in j]
        if all(isinstance(i,str) for i in l):
            return '\n'.join(l)
        else:
            return l
    elif isinstance(j,dict):
        for k in musicLabels:
            if k in j:
                l = [f"[CQ:record,file={j.pop(k)}]"]
                l = [process_data(j)]+l
                print("l",l)
                return l

        for k in videoLabels:
            if k in j:
                return f"[CQ:video,file={j[k]}]"

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
