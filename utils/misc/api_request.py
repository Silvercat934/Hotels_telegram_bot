import json
import re
from typing import Dict, Union

import requests

from config_data.config import api_key


def request_to_api(api_url: str, querystring: Dict[str, Union[str, int]], pattern: str) -> dict:
    """
    Функция. Делает запросы к API
    """

    headers = {'X-RapidAPI-Host': 'hotels4.p.rapidapi.com',
               "X-RapidAPI-Key": api_key}

    response = requests.get(api_url, headers=headers, params=querystring, timeout=30)

    if response.status_code == requests.codes.ok:
        find = re.search(pattern, response.text)
        if find:
            result = json.loads(f"{{{find[0]}}}")
            return result

