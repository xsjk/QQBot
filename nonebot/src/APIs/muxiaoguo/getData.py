from json import dump,load
from os.path import join,dirname

def get_detail(url):
    d.get(url)
    detail = dict(i.text.split("： ") for i in d.find_elements_by_class_name("simpleTable"))
    if detail["接口地址"][-1]=="/":
        detail["接口地址"]=detail["接口地址"][:-1]
    tables = d.find_elements_by_class_name('layui-table')
    for i,n in enumerate(["请求参数","返回参数"]):
        detail[n] = [l.split(" ",3) for l in tables[i].text.split("\n")[1:]]
    detail["请求参数"] = [a for a in detail["请求参数"] if a[1]=="是"]+[a for a in detail["请求参数"] if a[1]=="否"]
    if detail["请求参数"]:
        if detail["请求参数"][0][0]=="null":
            detail["请求参数"]=[]
    if detail["返回参数"]:
        if detail["返回参数"][0][0]=="null":
            detail["返回参数"]=[]
        elif detail["返回参数"][0][0]=="Comment":
            detail["返回参数"][0][0]="comment"
    return detail

json_path = join(dirname(__file__),"muxiaoguoApiData.json")

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
        d.get("https://api.muxiaoguo.cn/")
        apiDict = {}
        for frame in d.find_element_by_id("listApi").find_elements_by_xpath("./*"):
            e = frame.find_element_by_xpath("./*")
            url = e.get_attribute("href")
            text = e.text.split("\n")
            apiDict[text[1]]={"地址":url,"简介":text[2]}
        for apiName in apiDict:
            print(apiName)
            apiDict[apiName]["详细"] = get_detail(apiDict[apiName]["地址"])

    #部分API漏了请求参数说明，故在此手动添加
    apiDict["表情包搜索"]["详细"]['请求参数'].append(["tuname","是","String","搜索关键词"])
    #部分API的返回格式错误，在此手动修正
    apiDict["二维码生成"]["详细"]['返回格式']="IMG"
    #部分API的返回参数有误，在此手动修正
    apiDict["一言"]["详细"]["返回参数"][0][0] = "constant"

    with open(json_path,"w") as f:
        dump(apiDict,f,indent=2)
