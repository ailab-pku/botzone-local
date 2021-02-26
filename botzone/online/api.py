import getpass
import os
import requests
import zipfile

class BotzoneAPI:
    '''
    Botzone API used.
    '''

    cookies = None

    def login():
        email = input('Input email:')
        password = getpass.getpass('Input password:')
        try:
            r = requests.post('https://botzone.org.cn/login', data = dict(email = email, password = password))
        except:
            raise RuntimeError('Failed to connect to botzone.org!')
        if not r.ok:
            raise RuntimeError('Failed to connect to botzone.org, Reason: ' + r.reason)
        d = r.json()
        if not d['success']:
            print('Failed to log in to botzone.org, Reason:', d['message'])
            return False
        BotzoneAPI.cookies = r.cookies
        return True

    def get_bot(ver_id):
        try:
            r = requests.get('https://botzone.org.cn/mybots/detail/version/' + ver_id, cookies = BotzoneAPI.cookies)
        except:
            raise RuntimeError('Failed to connect to botzone.org!')
        if not r.ok:
            raise RuntimeError('Failed to connect to botzone.org, Reason: ' + r.reason)
        d = r.json()
        if not d['success']:
            raise RuntimeError('Failed to get bot %s, Reason: %s' % (ver_id, d['message']))
        if d['bot'] is None:
            # mistakenly use bot_id as ver_id
            raise RuntimeError('Failed to get bot %s, please use ver_id instead of bot_id!' % ver_id)
        return d['bot']

    def download_bot(bot_id, ver, target):
        try:
            r = requests.get('https://botzone.org.cn/mybots/viewsrc/%s/%d?download=true' % (bot_id, ver), cookies = BotzoneAPI.cookies)
        except:
            raise RuntimeError('Failed to connect to botzone.org!')
        if not r.ok:
            raise RuntimeError('Failed to connect to botzone.org, Reason: ' + r.reason)
        try:
            # Try to decode by json in case of failure
            d = r.json()
        except:
            # success
            with open(target, mode = 'wb') as f:
                f.write(r.content)
            return True
        if d['message'] == '你还没有登录，无法访问此页。':
            # allowing caller to request login
            return False
        raise RuntimeError('Failed to download bot, Reason: ' + d['message'])
    
    def download_userfile(user_id, path):
        try:
            r = requests.get('https://botzone.org.cn/downloaduserfiles/?uid=%s' % user_id, cookies = BotzoneAPI.cookies, stream = True)
        except:
            raise RuntimeError('Failed to connect to botzone.org!')
        if not r.ok:
            raise RuntimeError('Failed to connect to botzone.org, Reason: ' + r.reason)
        if r.url == 'https://botzone.org.cn/?msg=notlogin':
            # allowing caller to request login
            return False
        target = os.path.join(path, 'tmp.zip')
        print('Downloading...')
        cnt = 0
        with open(target, mode = 'wb') as f:
            for chunk in r.iter_content(chunk_size = 4096):
                f.write(chunk)
                cnt += len(chunk)
                print(cnt, 'bytes downloaded', end = '\r')
        print()
        if not zipfile.is_zipfile(target):
            os.remove(target)
            raise RuntimeError('Failed to download userfile, Reason: ' + r.json()['message'])
        with zipfile.ZipFile(target) as f:
            for item in f.namelist():
                print('Extracting', item)
                f.extract(item, path)
        os.remove(target)
        return True