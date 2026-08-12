import requests
import json
import os
import sys
import hashlib
import base64

# Windows 控制台默认 GBK 编码无法打印 emoji，统一为 UTF-8 输出
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

requests.packages.urllib3.disable_warnings()

SCKEY = os.environ.get('SCKEY')
TG_BOT_TOKEN = os.environ.get('TGBOT')
TG_USER_ID = os.environ.get('TGUSERID')


def checkin_sspanel(base_url, email, password):
    """SSPanel 机场面板：表单登录 + /user/checkin"""
    email = email.split('@')
    email = email[0] + '%40' + email[1]
    session = requests.session()
    session.get(base_url, verify=False)

    login_url = base_url + '/auth/login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/56.0.2924.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    post_data = 'email=' + email + '&passwd=' + password + '&code='
    post_data = post_data.encode()
    response = session.post(login_url, post_data, headers=headers, verify=False)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/56.0.2924.87 Safari/537.36',
        'Referer': base_url + '/user'
    }
    response = session.post(base_url + '/user/checkin', headers=headers, verify=False)
    response = json.loads(response.text)
    return response['msg']


def checkin_wjkc(base_url, email, password):
    """网际快车面板：MD5 密码 + base64 包裹请求 + session cookie"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
    }

    def enc(payload):
        raw = json.dumps(payload, separators=(',', ':')).encode()
        return base64.b64encode(raw).decode()

    def dec(data):
        raw = data.replace('-', '+').replace('_', '/')
        raw += '=' * (-len(raw) % 4)
        return json.loads(base64.b64decode(raw).decode())

    session = requests.session()
    session.get(base_url, verify=False, timeout=15)

    md5_pwd = hashlib.md5(password.encode()).hexdigest()
    body = {'data': enc({'email': email, 'password': md5_pwd})}
    r = session.post(base_url + '/api/user/login', json=body, headers=headers, verify=False, timeout=15)
    d = dec(r.json()['data'])
    if d.get('code') != 0:
        raise RuntimeError('登录失败：%s' % d.get('msg'))

    r = session.post(base_url + '/api/user/sign_use', json={'data': enc({})},
                     headers=headers, verify=False, timeout=15)
    d = dec(r.json()['data'])
    if d.get('code') != 0:
        msg = str(d.get('msg') or '')
        # 今日已签到 / 重复签到 → 视为成功（浏览器手动点过也算）
        if any(k in msg for k in ('SIGN_USE_MULTY_TIMES', 'HAS_SIGNED', 'ALREADY_SIGN', '已签到', '已经签到')):
            return '今日已签到（%s）' % msg
        raise RuntimeError('签到失败：%s' % msg)
    add = d.get('data', {}).get('addTraffic', 0)
    return '签到成功，获得 %s 流量' % fmt_traffic(add)


def fmt_traffic(n):
    """把字节数格式化为可读的 GB/MB"""
    n = float(n or 0)
    if n >= 1024 * 1024 * 1024:
        return '%.2f GB' % (n / (1024 * 1024 * 1024))
    if n >= 1024 * 1024:
        return '%.2f MB' % (n / (1024 * 1024))
    return '%.0f KB' % (n / 1024)


PANELS = {
    'sspanel': checkin_sspanel,
    'wjkc': checkin_wjkc,
}


def collect_sites():
    """收集所有待签到的站点配置。

    第一站：EMAIL / PASSWORD / BASE_URL / PANEL（保持原配置兼容，默认 sspanel）
    后续站点：BASE_URL2 / BASE_URL3 ...，账号与面板类型 PANEL2 缺省时复用第一站
    """
    sites = []
    email1 = os.environ.get('EMAIL')
    password1 = os.environ.get('PASSWORD')

    base_url = os.environ.get('BASE_URL')
    if base_url and email1 and password1:
        sites.append({
            'base_url': base_url,
            'email': email1,
            'password': password1,
            'panel': (os.environ.get('PANEL') or 'sspanel'),
        })

    index = 2
    while True:
        base_url_n = os.environ.get('BASE_URL' + str(index))
        if not base_url_n:
            break
        sites.append({
            'base_url': base_url_n,
            'email': (os.environ.get('EMAIL' + str(index)) or email1),
            'password': (os.environ.get('PASSWORD' + str(index)) or password1),
            'panel': (os.environ.get('PANEL' + str(index)) or 'sspanel'),
        })
        index += 1

    return sites


def main():
    sites = collect_sites()
    if not sites:
        print('未配置任何站点，请在 .env 或环境变量中设置 BASE_URL / EMAIL / PASSWORD')
        return

    results = []
    for i, site in enumerate(sites, 1):
        fn = PANELS.get(site['panel'])
        if not fn:
            msg = '未知面板类型：%s（支持 sspanel / wjkc）' % site['panel']
        else:
            try:
                msg = fn(site['base_url'], site['email'], site['password'])
            except Exception as e:
                msg = '签到失败：%s' % e
        print('站点%d [%s] %s' % (i, site['base_url'], msg))
        results.append('站点%d [%s] %s' % (i, site['base_url'], msg))

    result = '\n'.join(results)

    if SCKEY:
        sendurl = 'https://sctapi.ftqq.com/' + SCKEY + '.send?title=机场签到&desp=' + result
        requests.get(url=sendurl)

    if TG_USER_ID and TG_BOT_TOKEN:
        sendurl = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?chat_id={TG_USER_ID}&text={result}&disable_web_page_preview=True'
        requests.get(url=sendurl)


if __name__ == '__main__':
    main()
