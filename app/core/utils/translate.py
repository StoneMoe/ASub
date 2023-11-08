import time
from pprint import pprint
from typing import Optional
from uuid import uuid4
import requests

from app.core.utils.hash import sha256


def youdao_translate(text: str, _from='ja', _to='zh-CHS',
                     vocab_id: Optional[str] = None,
                     app_key: Optional[str] = None, app_secret: Optional[str] = None) -> str:
    api = 'https://openapi.youdao.com/api'
    app_key = app_key or 'DEFAULT_KEY'
    app_secret = app_secret or 'DEFAULT_SECRET'
    query = {
        'q': text,
        'from': _from,
        'to': _to,
        'appKey': app_key,
        'salt': str(uuid4()),
        'sign': None,  # sha256(应用ID+input+salt+curtime+应用密钥)
        'signType': 'v3',
        'curtime': str(int(time.time())),
        'vocabId': vocab_id
    }
    if not query['vocabId']:
        del query['vocabId']
    # sign
    sign_input = query['q'] if len(query['q']) <= 20 else query['q'][:10] + str(len(query['q'])) + query['q'][-10:]
    query['sign'] = sha256(app_key + sign_input + query['salt'] + query['curtime'] + app_secret)
    # req
    resp = requests.post(api, data=query).json()
    if resp['errorCode'] != '0':
        pprint(resp)
        raise ValueError("Translate failed")
    result = resp['translation'][0]
    return result
