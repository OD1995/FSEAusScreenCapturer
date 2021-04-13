import logging
from UsefulFunctions import (
    get_driver
)
import os
from azure.storage.blob import BlockBlobService
from azure.storage.blob.models import ContentSettings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    driver = get_driver()
    logging.info("Driver created")
    driver.get("https://vimeo.com/38098859")
    logging.info("Navigated to website")
    actions = ActionChains(driver)
    actions.send_keys(Keys.SPACE).perform()
    logging.info("Space pressed, video should be playing..")
    ## Create ffmpeg command
    vidName = "13Apr21test1"
    outpath = f"/tmp/{vidName}.mp4"
    ffmpegCommand = f'./ffmpeg -t 60 -f x11grab -s 1280x1024  -r 25 -i :0.0+0,0 {outpath}'
    result = os.popen(ffmpegCommand).read()
    logging.info("command run")

    ## Upload MP4 to Azure
    block_blob_service = BlockBlobService(
        connection_string=os.getenv("fsecustomvisionimagesCS")
    )
    block_blob_service.create_blob_from_path(
        container_name="test",
        blob_name=vidName,
        file_path=outpath,
        content_settings=ContentSettings(
            content_type="video/mp4"
        )
    )
    logging.info("blob created")
    driver.quit()
    return func.HttpResponse(
             outpath,
             status_code=200
    )