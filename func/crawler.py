import urllib3
import datetime

from typing import List
from .models.stock import stock
from bs4 import (BeautifulSoup, ResultSet)

class stock_available_volume_cvm_code_crawler():
    url = "https://br.advfn.com/bolsa-de-valores/bovespa/{}/empresa"

    def __init__(self):
        pass

    def enrich(self, stock_ref: stock) -> bool:
        if not hasattr(stock_ref, "stock_type"):
            return False

        if not hasattr(stock_ref, "available_volume"):
            return False  

        if not hasattr(stock_ref, "cvm_code"):
            return False  

        url_det = str(self.url).format(stock_ref.code)
        req = urllib3.PoolManager()
        res = req.request('GET', url_det)
        soup = BeautifulSoup(res.data, 'html.parser')
        res_url = res.geturl()

        if str(res_url).__contains__('cotacao'):
            return False

        # CVM code
        cvm_row = soup.find("td", text=" Código CVM ")

        if cvm_row is not None:
            cvm_code_aux = cvm_row.find_next("td").text
            stock_ref.cvm_code = str(cvm_code_aux).strip()
        else:
            return False

        # Stock volume

        on_share_row = soup.find("td", text="Ações Ordinárias")
        pn_share_row = soup.find("td", text="Ações Preferenciais")

        if on_share_row is not None and pn_share_row is not None:
            on_share = on_share_row.find_next(
                "td").text.strip().replace('.', '')
            pn_share = pn_share_row.find_next(
                "td").text.strip().replace('.', '')

            if(stock_ref.stock_type.upper() == 'PN'):
                stock_ref.available_volume = int(pn_share)
            else:
                stock_ref.available_volume = int(on_share)
            pass
        else:
            return False


        return True
    pass