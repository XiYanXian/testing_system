import urllib.request
import urllib
import json
import logging
logger = logging.getLogger('apis')


def send_sms(mobile, captcha, out_time=300):
    # flag用于标记短信是否发送成功
    flag = True
    # 短信API信息
    url = 'https://open.ucpaas.com/ol/sms/sendsms'
    # 头部信息，声明body的格式
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    # 准备用Post传的值，用字典格式
    values = {
        'sid': 'c9ad0777826afbba2b3e158ff78f7a6e',
        "token": "07c272b13aa6bf65db6ae860199b0e63",
        "appid": "9782493b57e940e08f495d993778e040",
        "templateid": "488990",
        "param": f'{str(captcha)}, {out_time}',
        "mobile": mobile,

    }

    try:
        # 将字典格式化成bytes格式
        data = json.dumps(values).encode('utf-8')
        logger.info(f'即将发送短信：{data}')
        # 创建一个Request，放入我们的地址、数据和头
        request = urllib.request.Request(url, data, headers)
        html = urllib.request.urlopen(request)
        html = html.read().decode('utf-8')
        code = json.loads(html)["code"]
        if code == '000000':
            logger.info(f'短信发送成功：{html}')
            flag = True
        else:
            logger.info(f"短信发送失败：{html}")
            flag = False
    except Exception as ex:
        logger.info(f"出错了，错误原因：{ex}")
        flag = False
    return flag


if __name__ == '__main__':
    # 测试短信接口是否管用
    send_sms("18307392010", "123456")
