from datetime import datetime, timedelta
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"


###### INPUTS
startUTC = datetime(
        year=2021,
        month=4,
        day=23,
        hour=10,
        minute=20
    )
sport = "football"
channel = "bein3"
########


dtFormat = "%Y-%m-%dT%H:%MZ"

fromStr = startUTC.strftime(dtFormat)
toStr = (startUTC + timedelta(days=1)).strftime(dtFormat)

urlRetrieveReq = requests.get(
        url="https://vccapi.kayosports.com.au/v1/fixtures/panels",
        headers={"user-agent" : UA},
        params={
                "from" : fromStr,
                "withLive" : True,
                "to" : toStr
            }
    )
urrJS = urlRetrieveReq.json()

x = urrJS[0]

## Collect the needed information for each stream
infoList = []
for panel in urrJS:
    section = panel['title']
    for content in panel['contents']:
#        for dataDict in content['data']:
        dataDict = content['data']
        tba = {}
        for a in ['id',
                  'title',
                  'sport',
                  'linearProvider',
                  'timestamp',
                  'transmissionTime',
                  'preCheckTime',
                  "live",
                  ]:
            tba[a] = dataDict['asset'][a]
        tba['section'] = section
        tba['url'] = dataDict['clickthrough']['url']
        infoList.append(tba)
print(len(infoList))
uniqueInfoList = list({v['id']:v for v in infoList}.values())
print(len(uniqueInfoList))

dtFormat2 = "%Y-%m-%dT%H:%M:%SZ"

import pandas as pd;df=pd.DataFrame(uniqueInfoList);df.to_clipboard()

#for b in uniqueInfoList:
#    tt = datetime.strptime(b['transmissionTime'],dtFormat2)
#    pct = datetime.strptime(b['preCheckTime'],dtFormat2)
#    tms = datetime.strptime(b['timestamp'],dtFormat2)
#    print(tms)
##    print((tt - pct).total_seconds())

#relProg = [x
#            for x in uniqueInfoList
#            if (x['sport'] == sport) &
#                (x['linearProvider'] == channel) &
#                (datetime.strptime(x['transmissionTime'],dtFormat2) == startUTC)][0]
#
#returnMe = f"https://kayosports.com.au{relProg['url']}"
