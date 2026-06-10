import urllib.request, json, os, configparser, urllib.parse as up

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.openclaw/config.toml"))
aid = cfg["provider.feishu"]["appId"].strip('"')
sec = cfg["provider.feishu"]["appSecret"].strip('"')
bd = json.dumps({"app_id": aid, "app_secret": sec}).encode()
rq = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=bd, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(rq, timeout=10) as f:
    jd = json.loads(f.read().decode())
    TOK = jd["tenant_access_token"]

def api(method, url, body_obj=None):
    h = {"Authorization": "Bearer " + TOK, "Content-Type": "application/json"}
    d = json.dumps(body_obj).encode() if body_obj else None
    rq2 = urllib.request.Request(url, data=d, headers=h, method=method)
    with urllib.request.urlopen(rq2, timeout=15) as f:
        return json.loads(f.read().decode())

APP = "Pnk9bARvQaVUh5sUMjIcyhF8n4b"
TID = "tblpZpUDxLu2ahph"

# 先获取记录ID
r = api("GET", "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/records?page_size=50")
items = r.get("data", {}).get("items", [])

# 名称 -> 官网链接
official_links = {
    "墨西哥城四季酒店": "https://www.fourseasons.com/mexico/",
    "墨西哥城W酒店": "https://www.marriott.com/en-us/hotels/mexcw-w-mexico-city/",
    "坎昆希尔顿酒店": "https://www.hilton.com/en/hotels/cunhihi-hilton-cancun/",
    "洛杉矶比弗利华尔道夫": "https://www.hilton.com/en/hotels/bxhwhwa-waldorf-astoria-beverly-hills/",
    "纽约时代广场万豪": "https://www.marriott.com/en-us/hotels/nycmq-new-york-marriott-marquis/",
    "阿兹特克体育场": "https://www.estadioazteca.com.mx/",
    "奇琴伊察玛雅金字塔": "https://www.chichenitza.com/",
    "坎昆加勒比海滩": "https://www.visitmexico.com/en/destinations/quintana-roo/cancun",
    "洛杉矶好莱坞/环球影城": "https://www.universalstudioshollywood.com/",
    "正宗墨西哥Taco/龙舌兰": "https://www.visitmexico.com/en/",
    "弗里达博物馆": "https://www.museofridakahlo.org.mx/",
    "2026世界杯观赛套餐": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026",
}

cnt = 0
for item in items:
    fld = item.get("fields", {})
    name = fld.get("名称", "")
    rid = item["record_id"]
    if name in official_links:
        link = official_links[name]
        api("PUT",
            "https://open.feishu.cn/open-apis/bitable/v1/apps/" + APP + "/tables/" + TID + "/records/" + rid,
            {"fields": {"\u8be6\u60c5\u94fe\u63a5": link}})
        cnt += 1
        print("  " + name + " -> " + link)
    else:
        print("  ??? " + name)

print("Done: " + str(cnt) + "/" + str(len(items)))
