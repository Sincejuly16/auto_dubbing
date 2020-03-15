import base64
import datetime
import hashlib
import hmac
import json

import requests


class Translator(object):
    def __init__(self, host):
        # 应用ID（到控制台获取）
        self.APPID = "5e2952b0"
        # 接口APIKey（到控制台机器翻译服务页面获取）
        self.APIKey = "414ea9ed44eda8363fbc10a5d6483ebc"
        # 接口APISercet（到控制台机器翻译服务页面获取）
        self.Secret = "9b7d258ee7d3bfbb014e0d2aa956652c"

        # 以下为POST请求
        self.Host = host
        self.RequestUri = "/v2/its"
        # 设置url
        # print(host)
        self.url = "https://" + host + self.RequestUri
        self.HttpMethod = "POST"
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"

        # 设置当前时间
        curTime_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(curTime_utc)
        # 设置业务参数
        # 语种列表参数值请参照接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html
        self.Text = ""
        self.BusinessArgs = {
            "from": "en",
            "to": "cn",
        }

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).

        The supplied date must be in UTC.

        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest):
        signatureStr = "host: " + self.Host + "\n"
        signatureStr += "date: " + self.Date + "\n"
        signatureStr += self.HttpMethod + " " + self.RequestUri \
                        + " " + self.HttpProto + "\n"
        signatureStr += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode(encoding='utf-8')),
                             bytes(signatureStr.encode(encoding='utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data):
        digest = self.hashlib_256(data)
        # print(digest)
        sign = self.generateSignature(digest)
        authHeader = 'api_key="%s", algorithm="%s", ' \
                     'headers="host date request-line digest", ' \
                     'signature="%s"' \
                     % (self.APIKey, self.Algorithm, sign)
        # print(authHeader)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": authHeader
        }
        return headers

    def get_body(self):
        content = str(base64.b64encode(self.Text.encode('utf-8')), 'utf-8')
        postdata = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgs,
            "data": {
                "text": content,
            }
        }
        body = json.dumps(postdata)
        # print(body)
        return body

    def call_url(self):
        if self.APPID == '' or self.APIKey == '' or self.Secret == '':
            print('Appid 或APIKey 或APISecret 为空！请打开demo代码，填写相关信息。')
        else:
            code = 0
            body = self.get_body()
            headers = self.init_header(body)
            # print(self.url)
            response = requests.post(self.url, data=body, headers=headers, timeout=8)
            status_code = response.status_code
            # print(response.content)
            if status_code != 200:
                # 鉴权失败
                print("Http请求失败，状态码：" + str(status_code) + "，错误信息：" + response.text)
                print("请根据错误信息检查代码，接口文档：https://www.xfyun.cn/doc/nlp/xftrans/API.html")
            else:
                # 鉴权成功
                respData = json.loads(response.text)
                print(respData)
                # 以下仅用于调试
                code = str(respData["code"])
                if code != '0':
                    print("请前往https://www.xfyun.cn/document/error-code?code=" + code + "查询解决办法")

    def get_translation(self, text):
        if not text:
            return ''
        self.Text = text
        body = self.get_body()
        headers = self.init_header(body)
        response = requests.post(self.url, data=body, headers=headers, timeout=8)
        status_code = response.status_code
        if status_code != 200:
            print("Http Error: " + str(status_code))
            print(headers)
            print(body)
        else:
            respData = json.loads(response.text)
            code = str(respData['code'])
            if code != '0':
                print('Error ' + code)
            return respData['data']['result']['trans_result']['dst']
