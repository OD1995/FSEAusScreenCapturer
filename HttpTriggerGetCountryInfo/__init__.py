import logging

import azure.functions as func
from UsefulFunctions import (
    get_driver,
    get_bbs
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    driver = get_driver()
    driver.get("https://www.iplocation.net/")
    bbs = get_bbs()
    dtGCI = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    bbs.create_blob_from_text(container_name="test",
                            blob_name=f"GCI {dtGCI}.txt",
                            text=driver.page_source
    )
    driver.close()

    return func.HttpResponse(
            "Done",
            status_code=200
    )
