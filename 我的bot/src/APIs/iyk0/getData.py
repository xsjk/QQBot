from json import dump,load
from os.path import join,dirname

def get_detail(url):
    d.get(url)
    detail = dict(i.text.split("： ") for i in d.find_elements_by_class_name("simpleTable"))
    tables = d.find_elements_by_class_name('layui-table')
    for i,n in enumerate(["请求参数","返回参数"]):
        detail[n] = [l.split(" ",3) for l in tables[i].text.split("\n")[1:]]
    detail["请求参数"] = [a for a in detail["请求参数"] if a[1]=="是"]+[a for a in detail["请求参数"] if a[1]=="否"]
    return detail

json_path = join(dirname(__file__),"iyk0ApiData.json")

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
    # with Driver() as d:
        d.get("https://api.iyk0.com/")
        d.get("https://api.iyk0.com/api.php?list")
        apiDict = {}
        for frame in d.find_elements_by_xpath("/html/body/*"):
            e = frame.find_element_by_xpath("./*")
            url = e.get_attribute("href")
            text = e.text.split("\n")
            apiDict[text[1]]={"地址":url,"状态":text[0][-2:],"简介":'\n'.join(text[2:])}
        for apiName in apiDict:
            print(apiName)
            apiDict[apiName]["详细"] = get_detail(apiDict[apiName]["地址"])

    #部分API漏了请求参数说明，故在此手动添加
    apiDict["搜狗百科"]["详细"]['请求参数'].append(["msg","是","String","搜索关键词"])
    apiDict["在线ping网址"]["详细"]['请求参数'].append(["url","是","String","网址"])
    #部分API的返回格式错误，在此手动修正
    apiDict["关键词斗图"]["详细"]['返回格式']="TXT"
    #部分API有无用参数，在此删除
    apiDict["新闻查询"]["详细"]["请求参数"].pop()
        
    with open(json_path,"w") as f:
        dump(apiDict,f,indent=2)
