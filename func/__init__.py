import logging
import azure.functions as func
import json
import requests
import pathlib
import threading

from .models.stock import stock
from .crawler import stock_available_volume_cvm_code_crawler
from configuration_manager.reader import reader

SETTINGS_FILE_PATH = pathlib.Path(__file__).parent.parent.__str__() + "//local.settings.json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('sosi_func0004_crawler_stock_volume_cvm_code function processed a request.')

    try:
        stock_obj: stock = stock()
        det_crawler: stock_available_volume_cvm_code_crawler = stock_available_volume_cvm_code_crawler()
        config_obj = reader(SETTINGS_FILE_PATH, "Values")

        stock_obj.__dict__ = req.get_json()
        
        logging.info("Crawling the details for '{}'".format(stock_obj.code))

        if not (det_crawler.enrich(stock_obj)):
            logging.warning("'{}' was not enriched!".format(stock_obj.code))
        
        logging.info("Calling next function for '{}'".format(stock_obj.code))
        json_obj = json.dumps(stock_obj.__dict__)

        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'postman-token': "652ec406-7b16-40ca-8436-5baf1d36b793"
        }

        url_to_call = config_obj.get_value("NEXT_SERVICE_TO_CALL")

        if (url_to_call == ''):
            msg = "No service URL found. {} was processed but no further action was taken. This service is ready for another request.".format(stock_obj.code)

            logging.warning(msg)    
            return func.HttpResponse(body=msg, status_code=200)
        else:
            
            # At this time, we are not looking for HTTP response
            threading.Thread(target=invoke_url, args=(url_to_call, json_obj)).start()
            msg = "'{}' was sent to next step. This service is ready for another request".format(stock_obj.code)
            
            logging.info(msg)
            return func.HttpResponse(body=msg, status_code=200)
    except Exception as err:
        logging.error(str(err))
        return func.HttpResponse(body=str(err), status_code=500)
        pass

def invoke_url(url, json):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }

    requests.request("POST", url, data=json, headers=headers)
    pass