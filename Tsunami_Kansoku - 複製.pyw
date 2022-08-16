from multiprocessing import Value
import re
import time
import requests
import urllib3
import xmltodict
from bs4 import BeautifulSoup
urllib3.disable_warnings()

#xml = requests.get("https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml")

headers = dict() #測試
headers["Cookie"]="__test=eb3f55df3488e2eb5ad76e961a3d8e90" #測試

xml = requests.get("https://mcsm.stevened7246.cf/eqvol.xml",headers=headers) #測試
#xml = requests.get("http://www.yoyo0901.byethost16.com/eqvol.xml",headers=headers) #測試
xml.encoding = "utf-8"
sp = BeautifulSoup(xml.text, 'xml')
#取得気象庁XML(地震/火山相關)


if xml.status_code == 200:
    print("資料取得正常")
else:
    print("資料取得失敗，請檢查網路或氣象廳網站是否正常")
    exit()
#判定資料是否取得正常


logfile = open("log.txt", encoding="utf8")
logid1 = logfile.read()
logfile.close
#讀取上次情報ID


z = ""
for i in sp.select("entry"): #搜尋標題為"津波警報・注意報・予報a"的XML
    if i.title.text == "津波情報a" or i.title.text == "津波情報a" and "津波観測" in i.content.text: #沖合の津波観測に関する情報 津波情報a
        url = i.id.text #若取得海嘯觀測的資料 設定URL
        # logid2 = i.update.text
        # if logid1 == logid2: #判定情報是否為新的
        #   exit()
        # f = open("D:\地震\Tsunami\jmalog.txt", "w",encoding="utf8")
        # f.write(logid2)
        # f.close()
        # #寫入情報ID
        z = "a"
        break

if z == "": #如果未在XML取得海嘯資訊則退出
    print("未取得海嘯資訊")
    exit()


def log(): #讀取Log檔ID 若跟此次ID不一樣則退出
    logfile = open('log.txt', encoding="utf8")
    logid3 = logfile.read()
    logfile.close
    if logid2 != logid3:
        exit()

def file(y=8): #寫入資料到output文字檔
    f = open("output.txt", "w",encoding="utf8")
    f.write(output)
    f.close()
    print(output)
    time.sleep(y)

# url = "http://www.yoyo0901.byethost16.com/津波観測/32-39_12_06_191025_VTSE51.xml"

xml2 = requests.get(url) #取得資料

headers1 = dict() #測試用網站需cookie
headers1["Cookie"]="__test=eb3f55df3488e2eb5ad76e961a3d8e90"

xml2 = requests.get(url,headers=headers1)

xml2.encoding = "utf-8"
xml2=xmltodict.parse(xml2.text) #XML轉JSON

data = xml2["Report"] #資料主體
title = data["Control"]["Title"] #資料標題
head = data["Head"] #基本資料
body = data["Body"]
tsunami = body["Tsunami"] #海嘯觀測資訊
item = tsunami["Observation"]["Item"]

# if data["Control"]["Status"] == "訓練": #判定是否為訓練報
#     print("これは訓練です")
#     exit()

cancel = ""
if "取消" in data["Head"]["InfoType"]: #判定是否取消
    cancel = "取消"

oki = ""
if "沖合" in title: #判定是否為"沖合津波観測"
    oki = "（沖合）"
    

print(title)



a = 0
n = 0
dic1 = {}
list2 = []
for i in item:
    if type(i) == str:
        i = tsunami["Observation"]["Item"]
        a = 1
    b = 0
    for j in i["Station"]:
        if type(j) == str:
            j = i["Station"]
            b = 1
        name = j["Name"]
        ampm = ""
        try:
            maxheitime = j["MaxHeight"]["DateTime"]
            maxheitimeh = maxheitime[11:13]
            if int(maxheitimeh) > 12:
                maxheitimeh = int(maxheitimeh) - 12
                ampm = "午後"
            else:
                ampm = "午前"
            if str(maxheitimeh)[:1] == "0":
                maxheitimeh = str(maxheitimeh).replace("0","",1)
        
            maxheitimem = maxheitime[14:16]
            if maxheitimem[:1] == "0":
                maxheitimem = maxheitimem.replace("0","",1)

            maxheitime = f"{maxheitimeh}時{maxheitimem}分　"
        except:
            maxheitime = ""
        try:
            height = j["MaxHeight"]["jmx_eb:TsunamiHeight"]["@description"]
            heightcm = height.split("．")[1].replace("ｍ","０ｃｍ")
            heightcm = heightcm.replace("００ｃｍ","")
            heightm = height.split("．")[0] + "ｍ"
            if heightm == "０ｍ":
                heightm = ""
            height = heightm + heightcm
            heightsor = j["MaxHeight"]["jmx_eb:TsunamiHeight"]["#text"]
        except:
            height = j["MaxHeight"]["Condition"]
            heightsor = j["MaxHeight"]["Condition"]
        try:
            if j["MaxHeight"]["jmx_eb:TsunamiHeight"]["@condition"] == "上昇中":
                rising = "(上昇中)"
                n = 0.01
        except:
            rising = ""
        try:
            dic1[f"津波観測{oki}　{name}　{ampm}{maxheitime}{height}{rising}"] = (float(heightsor)+n)
        except:
            dic1[f"津波観測{oki}　{name}　{ampm}{maxheitime}{height}{rising}"] = (0.0)
        if b == 1:
            break
    if a == 1:
        break


# print(dic1)
height = sorted(dic1.items(), reverse=True, key = lambda d: d[1])

if oki == "（沖合）":
    output = "沖合で津波を観測"
    file(1)
else:
    output = "各検潮所で観測された津波の高さは次の通りです"
    file(1)

for i in height:
    output = i[0]
    file(1)