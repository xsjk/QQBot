from json import dump,load
from os.path import join,dirname

def get_detail(url):
    d.get(url)
    while True:
        s = [f.text.replace("：\n","：").split("\n") for f in d.find_elements_by_class_name("mdui-col-sm-6")]
        if s[0][0].split("：")[1]!="API/":
            break
    detail = dict(i.split("：") for i in s[0] if "：" in i)
    detail["请求参数"] = [i.split() for i in s[2][3:]]
    try:
        detail["请求参数"] = [a for a in detail["请求参数"] if a[2]=="是"]+[a for a in detail["请求参数"] if a[2]=="否"]
    except Exception as e:
        detail["请求参数"] = []
    detail["返回参数"] = [i.split() for i in s[3][3:] if i[0]!="无"]
    return detail

json_path = join(dirname(__file__),"ovooaApiData.json")

try:
    with open(json_path) as f:
        apiDict = load(f)
except:
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    opts=Options()
    opts.add_argument("--headless")
    opts.add_argument('--disable-gpu')

    with Chrome(chrome_options=opts) as d:
        d.get("http://ovooa.com/")
        apiDict = {}
        for frame in d.find_element_by_class_name("mdui-row").find_elements_by_xpath("./*"):
            url = frame.find_element_by_link_text("MORE").get_attribute("href")
            text = frame.text.split()
            apiDict[text[0]]={"地址":url,"简介":text[4]}
        for apiName in apiDict:
            print(apiName)
            apiDict[apiName]["详细"] = get_detail(apiDict[apiName]["地址"])
            if "音乐" in apiName:
                apiDict[apiName]["详细"]['返回格式']="JSON/TEXT/XML"

    #部分API的返回格式错误，在此手动修正
    apiDict["随机验证码"]["详细"]['返回格式']="IMG"
    apiDict["自定义验证码生成"]["详细"]['返回格式']="IMG"
    apiDict["个人主页生成"]["详细"]['返回格式']="HTML"
    apiDict["语音点歌"]["详细"]['返回格式']="JSON"
    apiDict["初音解压"]["详细"]['返回格式']="HTML"
    apiDict["高清壁纸"]["详细"]['返回格式']="JSON/TEXT"
    apiDict["酷狗MV"]["详细"]["返回格式"]="TEXT/JSON"

    #部分API的返回参数错误，在此手动修正
    apiDict["随机头像"]["详细"]["返回参数"][1][-1] = "图片链接"
    apiDict["随机cosplay"]["详细"]["返回参数"][-1][0] = "text"
    apiDict["随机视频"]["详细"]["返回参数"][-1][-1] = "视频链接"
    apiDict["酷狗MV"]["详细"]["返回参数"][-1][-1] = "视频链接"
    apiDict["酷狗MV"]["详细"]["返回参数"].append(["text",'string','搜索结果'])
    
    #部分API漏了请求参数说明，故在此手动添加
    apiDict["酷狗音乐"]["详细"]["请求参数"].insert(1,['n', 'int', '是', '序号选择'])
    apiDict["语音点歌"]["详细"]["请求参数"].insert(1,['n', 'int', '是', '序号选择'])
    apiDict["三日天气"]["详细"]["请求参数"].append(['msg', 'string', '是', '城市地区名'])
    apiDict["QQ音乐VIP版"]["详细"]["请求参数"].insert(0,['msg', 'string', '是', '歌名'])
    


    with open(json_path,"w") as f:
        dump(apiDict,f,indent=2)
