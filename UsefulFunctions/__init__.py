from selenium import webdriver
import pyodbc
from time import sleep, time
from datetime import datetime, timedelta
import requests
import threading
from azure.storage.blob import BlockBlobService
import logging
import os

def get_driver():
    ## Create the driver with options
    chrome_options = webdriver.ChromeOptions()
    ## Commenting out the below causes Selenium to fail
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    return driver

def run_sql_command(
    sqlQuery,
    database
):
    ## Create connection string
    connectionString = get_connection_string(database)
    ## Run query
    with pyodbc.connect(connectionString) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sqlQuery)

def get_connection_string(database):
    username = 'matt.shepherd'
    password = "4rsenal!PG01"
    driver = '{ODBC Driver 17 for SQL Server}'
    # driver = 'SQL Server Native Client 11.0'
    server = "fse-inf-live-uk.database.windows.net"
    # database = 'AzureCognitive'
    ## Create connection string
    connectionString = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
    return connectionString


def get_driver_and_login_to_kayo():
    ## Get driver
    driver = get_driver()
    logging.info("driver got")
    ## Navigate to Kayo website
    driver.get('https://kayosports.com.au/')
    ## Wait till login button is clickable then click it
    counter=0
    while counter < 1:
        try:
            driver.find_element_by_css_selector('.gGZPNT').click()
            counter=1
        except:
            counter=0
    sleep(5)
    ## Login
    driver.find_element_by_xpath("//input[@name='email']").send_keys('futuressport@gmail.com')
    driver.find_element_by_xpath("//input[@name='password']").send_keys('Goldwing1')
    driver.find_element_by_xpath("//button[@type='submit']").click()
    sleep(3)
    logging.info("logged in")
    ## Select the Futures account
    counter=0
    while counter < 1: #Select account once clickable
        try:
            # driver.find_element_by_css_selector('.IrALQ:nth-child(1) .fulUIE').click()
            driver.find_element_by_xpath("//span[text()='Futures']").click()
            counter=1
        except:
            counter=0
    sleep(6)
    logging.info("account chosen")
    
    return driver

def get_prog_url_and_id(
    startUTC_dt,
    sport,
    channel
):
    dtFormat = "%Y-%m-%dT%H:%MZ"
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"

    fromStr = startUTC_dt.strftime(dtFormat)
    toStr = (startUTC_dt + timedelta(days=1)).strftime(dtFormat)

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

    ## Collect the needed information for each stream
    infoList = []
    for panel in urrJS:
        for content in panel['contents']:
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
            tba['url'] = dataDict['clickthrough']['url']
            infoList.append(tba)
    ## Get just the unique progs
    uniqueInfoList = list({v['id']:v for v in infoList}.values())

    dtFormat2 = "%Y-%m-%dT%H:%M:%SZ"

    relProg = [x
                for x in uniqueInfoList
                if (x['sport'] == sport) &
                    (x['linearProvider'] == channel) &
                    (datetime.strptime(x['transmissionTime'],dtFormat2) == startUTC_dt)][0]
    logging.info(f"relProg: {relProg}")

    return f"https://kayosports.com.au{relProg['url']}",relProg['id']

def save_image_to_blob_storage(
        driver,
        i,
        progID,
        block_blob_service
    ):
    blobName = f"{progID}\{str(i).zfill(6)}.png"
    block_blob_service.create_blob_from_bytes(
        container_name="test",
        blob_name=blobName,
        blob=driver.get_screenshot_as_png()
    )
    logging.info(f"{blobName} created")

def take_screenshots(
        startUTC_dt,
        endUTC_dt,
        progID,
        driver,
        block_blob_service
    ):
    ## Sleep until the screenshotting should begin
    initialSleepTime = (startUTC_dt - datetime.utcnow()).total_seconds()
    if initialSleepTime > 0:
        sleep(initialSleepTime)
    ## Calculate total length of recording
    # recordingLengthSecs = int((endUTC_dt - startUTC_dt).total_seconds())
    ## Create variable which will be altered each loop
    nexttime = time()
    i = 1
    while True:
        logging.info(f"i: {i}")
        thr = threading.Thread(
                target=save_image_to_blob_storage,
                args=(driver,i,progID,block_blob_service),
                kwargs={}
            )
        thr.start()
    #    print(datetime.now())
    #    save_image_to_blob_storage(
    #        driver,
    #        i,
    #        progID,
    #        block_blob_service
    #    )
        if datetime.utcnow() > endUTC_dt:
            sleep(5)
            break
        else:
            i += 1
        nexttime += 1
        sleeptime = nexttime - time()
    #    print((sleeptime/1)-1)
    #    print("time taken: ",time() - (nexttime - 1))
        if sleeptime > 0:
            sleep(sleeptime)

def get_kayo_screenshots(
    startUTC_dt,
    endUTC_dt,
    sport,
    channel
):
    ## Login to Kayo and get the driver
    driver = get_driver_and_login_to_kayo()
    ## Get programme's URL
    url,progID = get_prog_url_and_id(
        startUTC_dt,
        sport,
        channel
    )
    ## Navigate to URL
    driver.get(url)
    sleep(5)
    logging.info("navigated to URL")
    ## Start video (from start)
    driver.find_element_by_xpath("//span[text()='From Start']").click()
    sleep(5)
    logging.info("video started")
    ## Go full screen
    driver.find_element_by_css_selector("[aria-label='Toggle Fullscreen']").click()
    logging.info("full screen turned on")
    ## Create BBS
    block_blob_service = BlockBlobService(
        connection_string=os.getenv("fsecustomvisionimagesCS")
    )
    take_screenshots(
        startUTC_dt,
        endUTC_dt,
        progID,
        driver,
        block_blob_service
    )