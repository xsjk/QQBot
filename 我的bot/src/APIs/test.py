from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
import nonebot


from nonebot.rule import Rule,command
from nonebot.typing import T_State

async def async_checker(bot: Bot, event: Event, state: T_State) -> bool:
    return True

def sync_checker(bot: Bot, event: Event, state: T_State) -> bool:
    return True

def check(arg1, arg2):

    async def _checker(bot: Bot, event: Event, state: T_State) -> bool:
        return bool(arg1 + arg2)

    return Rule(_checker)

Rule(async_checker)

shell = on_command("test")

@shell.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # bot= nonebot.get_bots()#['2514633574']
    # print(bot)
    # for i in range(10):
    #     await shell.send(str(i))
    # dataText = '{"app":"com.tencent.structmsg","config":{"autosize":True,"forward":True,"type":"normal"},"desc":"随机音乐","meta":{"music":{"action":"","android_pkg_name":"","app_type":1,"appid":100497308,"desc":"李承铉","jumpUrl":"https://qq.com/","musicUrl":"http://music.163.com/song/media/outer/url?id=1869728598","preview":"http://p3.music.126.net/DmRmH7TzcQsxLAatUWXuhg==/109951166287247371.jpg","sourceMsgId":0,"source_icon":"","source_url":"","tag":"网易云随机音乐","title":"天上飞"}},"prompt":"[分享]天上飞","ver":"0.0.0.1","view":"music"}'
    dataText = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="2" templateID="1" action="web" brief="[分享]QQ热歌榜" sourceMsgId="0" url="" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2"><audio cover="http://y.gtimg.cn/music/photo_new/T002R300x300M000000CVCqK4aEW0M_2.jpg?max_age=2592000" src="http://aqqmusic.tc.qq.com/amobile.music.tc.qq.com/C400000Bo5hE1s2hNe.m4a?guid=3385512494&vkey=8E0026CB63C470F159F24E58000D425F7C9FABA94E6369801A6BDDE3225F1E4A0589FC4644A07D4A0ED8A8B97D0BEF39E014F2410F5941E4&uin=&fromtag=38" /><title>起风了</title><summary>周深</summary></item><source name="QQ音乐" icon="https://url.cn/53tgeq7" url="" action="app" a_actionData="com.tencent.qqmusic" i_actionData="tencent1101079856://" appid="1101079856" /></msg>'''
    dataText = dataText.replace('&','&amp;').replace(',','&#44;').replace('[','&#91;').replace(']','&#93;')
    print(dataText)
    # await shell.send(Message('[CQ:json,data={"app":"com.tencent.miniapp"&#44;"desc":""&#44;"view":"notification"&#44;"ver":"0.0.0.1"&#44;"prompt":"&#91;应用&#93;"&#44;"appID":""&#44;"sourceName":""&#44;"actionData":""&#44;"actionData_A":""&#44;"sourceUrl":""&#44;"meta":{"notification":{"appInfo":{"appName":"全国疫情数据统计"&#44;"appType":4&#44;"appid":1109659848&#44;"iconUrl":"http:\/\/gchat.qpic.cn\/gchatpic_new\/719328335\/-2010394141-6383A777BEB79B70B31CE250142D740F\/0"}&#44;"data":&#91;{"title":"确诊"&#44;"value":"80932"}&#44;{"title":"今日确诊"&#44;"value":"28"}&#44;{"title":"疑似"&#44;"value":"72"}&#44;{"title":"今日疑似"&#44;"value":"5"}&#44;{"title":"治愈"&#44;"value":"60197"}&#44;{"title":"今日治愈"&#44;"value":"1513"}&#44;{"title":"死亡"&#44;"value":"3140"}&#44;{"title":"今**亡"&#44;"value":"17"}&#93;&#44;"title":"中国加油, 武汉加油"&#44;"button":&#91;{"name":"病毒 : SARS-CoV-2, 其导致疾病命名 COVID-19"&#44;"action":""}&#44;{"name":"传染源 : 新冠肺炎的患者。无症状感染者也可能成为传染源。"&#44;"action":""}&#93;&#44;"emphasis_keyword":""}}&#44;"text":""&#44;"sourceAd":""}]'))
    # await shell.send(Message(f'[CQ:xml,data={dataText}]'))
    await shell.send(Message("[CQ:video,file=http://fs.mv.web.kugou.com/202109011148/56ee67363668ae0f8c0277a86522b53f/G091/M00/09/18/O5QEAFtqHEeAClq3B2HfvZDGLBw796.mp4]"))
    # await shell.finish(Message("[CQ:image,file=https://i.im5i.com/2021/02/08/hhFW4.png]"))


