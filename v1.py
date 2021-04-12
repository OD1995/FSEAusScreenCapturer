from selenium import webdriver
from azure.storage.blob import BlockBlobService
from time import sleep, time
import pyautogui
from datetime import datetime
import threading

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
chromePath = r"K:\Technology Team\Python\Web Scraping\ChromeDrivers\v89\chromedriver.exe"
driver = webdriver.Chrome(chromePath, options=options)
driver.get("https://www.bbc.co.uk/iplayer/live/bbcone")
sleep(1)
if "You now need to sign in to watch. It's quick & easy." in driver.page_source:
#    print("this")
    ## Click sign-in button
    signInButton = driver.find_element_by_xpath("//body/div[@id='orb-modules']/div[@id='blq-content']/div[@id='tviplayer']/div[@id='main']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/p[1]/span[1]/a[1]")
    signInButton.click()
    sleep(1)
    ## Enter username and password
    driver.find_element_by_xpath("//input[@id='user-identifier-input']").send_keys('oliverdernie1@googlemail.com')
    driver.find_element_by_xpath("//input[@id='password-input']").send_keys('Goldwing1!')
    ## Sign in
    signInButton2 = driver.find_element_by_xpath("//body[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/form[1]/button[1]/span[1]")
    signInButton2.click()
    sleep(1)
    
if "I have a TV Licence. Watch now." in driver.page_source:
#    print("that")
    watchNowButton = driver.find_element_by_xpath("//span[contains(text(),'I have a TV Licence. Watch now.')]")
    watchNowButton.click()
    sleep(1)
    
## Make video full size
pyautogui.moveTo(1650,875)
pyautogui.scroll(clicks=-300)
pyautogui.click()
sleep(0.5)
pyautogui.click()

cs="DefaultEndpointsProtocol=https;AccountName=fsecustomvisionimages;AccountKey=0gbOTBrl68MCGXlu6vHRK6DyQOIjRI5HRgTmfReCDW2cTmUnkCITP7DBRme9zI2yRsdWOrPxkDdz3v8Ti5Q3Zw==;EndpointSuffix=core.windows.net"

block_blob_service = BlockBlobService(connection_string=cs)


def save_image_to_blob_storage(
        driver,
        i,
        progID,
        block_blob_service
    ):
#    block_blob_service.create_blob_from_bytes(
#            container_name="test",
#            blob_name=f"{progID}\{str(i).zfill(6)}.png",
#            blob=driver.get_screenshot_as_png()
#        )
    imageRoot = r"C:\Users\oli.dernie\Documents\Automation tests\Aus\ScreenCapturer"
    filename = fr"{imageRoot}\{progID}\{str(i).zfill(6)}.png"
    print(i,datetime.now().time())#,time())
    driver.get_screenshot_as_file(filename)
    sleep(5)

def take_screenshots(
        startDT,
        endDT,
        progID,
        driver,
        block_blob_service
    ):
    ## Sleep until the screenshotting should begin
    initialSleepTime = (startDT - datetime.now()).total_seconds()
    print(f"\nfunc:ts initialSleepTime: {initialSleepTime}")
    if initialSleepTime > 0:
        sleep(initialSleepTime)
    ## Calculate total length of recording
    recordingLengthSecs = int((endDT - startDT).total_seconds())
    ## Create variable which will be altered each loop
    nexttime = time()
    i = 1
    while True:
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
        if i >= recordingLengthSecs:
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
            

from pyaudio import paInt16, PyAudio
import wave

def record_audio(
        startDT,
        endDT,
        progID,
        block_blob_service
    ):
    ## Sleep until the audio recording should begin
    initialSleepTime = (startDT - datetime.now()).total_seconds()
    print(f"\nfunc:ra initialSleepTime: {initialSleepTime}")
    if initialSleepTime > 0:
        sleep(initialSleepTime)
    ## Calculate total length of recording
    recordingLengthSecs = int((endDT - startDT).total_seconds())
    imageRoot = r"C:\Users\oli.dernie\Documents\Automation tests\Aus\ScreenCapturer"
    startStr = startDT.strftime("%H%M")
    endStr = endDT.strftime("%H%M")
    filename = fr"{imageRoot}\{progID}\{startStr} to {endStr}.mp3"
    
    CHUNK = 1024
    CHANNELS = 2
    RATE = 48000

    p = PyAudio()

    stream = p.open(format=paInt16,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(int(RATE / CHUNK * recordingLengthSecs)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(paInt16))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


H = 14
M1,M2 = 5,6

startDT = datetime(
        day=9,
        month=4,
        year=2021,
        hour=H,
        minute=M1
    )
endDT = datetime(
        day=9,
        month=4,
        year=2021,
        hour=H,
        minute=M2
    )
progID = "9Apr21_2"

take_screenshots(
        startDT,
        endDT,
        progID,
        driver,
        block_blob_service
    )

#record_audio(
#        startDT,
#        endDT,
#        progID,
#        block_blob_service
#    )

#if __name__ == '__main__':
#    imageThread = threading.Thread(
#            target=take_screenshots,
#            args=(
#                startDT,
#                endDT,
#                progID,
#                driver,
#                block_blob_service
#            )
#        )
#    audioThread = threading.Thread(
#            target=record_audio,
#            args=(
#                startDT,
#                endDT,
#                progID,
#                block_blob_service
#            )
#        )
#    
#    imageThread.start()
#    audioThread.start()
#    
#    imageThread.join()
#    audioThread.join()
    
driver.quit()