import logging
from bs4 import BeautifulSoup as BS
import azure.functions as func
from azure.storage.blob import BlockBlobService
import uuid
import os
from UsefulFunctions import (
    get_driver,
    run_sql_command,
    get_connection_string
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    ## Get driver
    driver = get_driver()
    logging.info("Driver created")
    ## Go to time.is and get the time
    driver.get("https://time.is/")
    logging.info("site navigated to")
    soup = BS(driver.page_source,'html.parser')
    logging.info("soup retrieved")
    clock0_bg = soup.find("div",{"id" : "clock0_bg"})
    currentTime = "".join([
        x.text
        for x in clock0_bg.find_all("span")
        ])
    ## Take screenshot and save it
    block_blob_service = BlockBlobService(
        connection_string=os.getenv("fsecustomvisionimagesCS")
    )
    block_blob_service.create_blob_from_bytes(
        container_name="test",
        blob_name=str(uuid.uuid4()) + ".png",
        blob=driver.get_screenshot_as_png()
    )
    ## Send to SQL
    Q = f"""INSERT INTO DockerTesting ([Value]) VALUES ('{currentTime}')"""
    logging.info(f"Q: {Q}")
    run_sql_command(
        sqlQuery=Q,
        database="TestDb"
    )
    ## This is a tiny and pointless change
    logging.info("command run")
    driver.quit()
    return func.HttpResponse(
             currentTime,
             status_code=200
    )
