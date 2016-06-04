# codeing:utf-8
import subprocess
import requests
import re
import codecs
import time
from PIL import Image
from PIL import ImageOps
from StringIO import StringIO
from hbk_crawler import hbk_crawler


class Hbk_ex05(hbk_crawler):
    def __init__(self):
        self.img_base_url = 'http://www.heibanke.com/captcha/image/'
        self.ex04url = 'http://www.heibanke.com/lesson/crawler_ex04/'

    def cleanImage(self, imagePath):
        print u'清洗图片:{}...'.format(imagePath),
        image = Image.open(imagePath)
        image = image.point(lambda x: 0 if x < 143 else 255)
        borderImage = ImageOps.expand(image, border=20, fill='white')
        borderImage.save(imagePath)
        print 'Done'
        return self.get_captcha(imagePath)

    def saveImage(self, url, imagePath):
        # n:Image数量
        r = self.s.get(url)
        i = Image.open(StringIO(r.content))
        i.save(imagePath)
        print 'Done'
        return self.cleanImage(imagePath)

    def get_img(self, n):
        # n:Image数量
        for i in range(1, n + 1):
            pattern = r'img src="/captcha/image/(.*)/" alt="captcha" '
            r = self.s.get(self.ex04url)
            if r.ok:
                self.img_src = re.findall(pattern, r.text)
                self.payload['captcha_0']=str(self.img_src[0])
                self.img_src = self.img_base_url + self.img_src[0]
                print u'开始下载第{}张图片...'.format(i),
                self.img_sum+=1
                captcha=self.saveImage(self.img_src, str(i) + '.png')
                if captcha:
                    self.payload['captcha_1']=captcha
                    break
            else:
                print u'网络连接错误，等待20秒重新连接...'
                time.sleep(18)
            time.sleep(2)

    def get_captcha(self, imagePath):
        print u'开始识别{}中的验证码:'.format(imagePath),
        try:
            p = subprocess.Popen(["tesseract", imagePath, 'captcha'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except:
            print 'subprocess error'
        with open('captcha.txt', "r") as f:
            captchaResponse = f.read().replace(" ", "").replace("\n", "")

        if len(captchaResponse) == 4 and captchaResponse.isupper() and captchaResponse.isalnum():
            print u'识别结果:{},尝试登录'.format(captchaResponse)
            return captchaResponse
        else:
            print captchaResponse,u'识别失败...'
            return 0

    def ex05(self):
        local_time = time.time()
        self.login('04')
        self.img_sum=0
        self.captcha_ok=0
        isfind_pw=False
        f=codecs.open('log.txt','a','utf-8')        
        for  n in range(31):
            while True:
                self.get_img(20) #尝试获取验证码次数
                self.payload['password'] = n
                response= self.s.post(self.ex04url,self.payload)
                if response.ok:
                    pattern = r'<h3>(.*)</h3>'
                    result = re.findall(pattern, response.text)                    
                    print self.payload
                    print result[0]
                    if u'密码错误' in result[0]:
                        self.captcha_ok+=1
                        f.writelines(str(n)+'\t,'+result[0]+'\n')
                        break
                    elif u'成功' in result[0]:
                        self.captcha_ok+=1
                        isfind_pw=True
                        break
                else:
                    print response
            if isfind_pw:                
                f.writelines(str(n)+'\t,'+result[0]+'\n')
                break
        f.writelines(u'共下载了{}张图片,其中{}张识别正确\n'.format(self.img_sum,self.captcha_ok))
        f.close()
        print 'run time is {:.2f}:'.format(time.time() - local_time)


if __name__ == '__main__':
    hbk_ex05 = Hbk_ex05()
    hbk_ex05.ex05()
