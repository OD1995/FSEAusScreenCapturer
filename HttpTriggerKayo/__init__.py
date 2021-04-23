import logging
from datetime import datetime
import azure.functions as func
from UsefulFunctions import get_kayo_screenshots


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"
    startUTC = req.params.get('startUTC')
    startUTC_dt = datetime.strptime(startUTC,dateFormat)
    endUTC = req.params.get('endUTC')
    endUTC_dt = datetime.strptime(endUTC,dateFormat)
    sport = req.params.get('sport')
    channel = req.params.get('channel')

    get_kayo_screenshots(
        startUTC_dt,
        endUTC_dt,
        sport,
        channel
    )

    return func.HttpResponse(
            "Done",
            status_code=200
    )
