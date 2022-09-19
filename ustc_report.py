# ----------------------------------------------------------
# coding=utf-8
# Copyright © 2022 Chopong All rights reserved.
# version 1.0 2022.03.17 changelog: in and out of school record
# v1.1 modified by chopong 2022.03.18 changelog: locale data form was updated by school
# v1.2 changelog: add email alert
# v1.3 changelog: out update
# v2.0 changelog: divide file into script and data
# v2.1 changelog: add multi-mail receivers
# v2.2 changelog: add dorm and dorm building
# v2.3 changelog: add WxPusher alert
# v2.4 changelog: add reason of outgoing
# v2.5 changelog: add different reasons for weekday and weekend
# v2.6 changelog: get more requirement code by the official document release by school
# v2.7 changelog: post address was modified by school
# 2022-09-19 v3.0 changelog: pass info was updated using Anhui phone number by school
# ----------------------------------------------------------

import re,os,datetime
import argparse
import json
from email.mime.text import MIMEText
import smtplib
import requests
# from requests.sessions import session
requests.packages.urllib3.disable_warnings()
try:    
    import json5
except ModuleNotFoundError:
    print('package Not find')
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple json5')
    import json5

parser = argparse.ArgumentParser(description="USTC daily report and auto registering.")
parser.add_argument('data_path', help="path to your data for auto report", type=str)
args = parser.parse_args()

# with open(args.data_path,'r+') as f:
#     data = f.read()
#     data = json.loads(data)

with open(args.data_path,'r+') as f:
    data = json5.load(f)

# ------ 用户在运行前需更改的变量 ------ #
USR               = data['STUID']             # 学号
PWD               = data['STUPW']             # 密码
LOCATION          = data['LOCATION']          # 所在校区
DORMBUILDING      = data['DORM_BUILDING']     # 所在宿舍楼
DORM              = data['DORM']              # 所在宿舍
EMERGENCY_CONTACT = data['EMERGENCY_CONTACT'] # 紧急联系人姓名
RELATIONSHIP      = data['RELATIONSHIP']      # 本人与紧急联系人关系
PHONE_NUMBER      = data['PHONE_NUMBER']      # 紧急联系人电话
REASONOFOUTING    = data['REASONOFOUTING']    # 报备信息
CAMPUS_TRANSFER   = data['CAMPUS_TRANSFER']   # 跨哪些校区
# ------------------------------------ #

# Step0: 设置打卡失败邮件或微信提醒
# 邮件
def sent_mail(data=data,message="打卡失败"):
    if data['mail_alert'] == 1: # 是否添加邮件提醒
        receivers              = data["mail_receivers"].split(',') # 多个收件人，使用逗号隔开，如“1@mail1,2@mail2”
        senderhost             = data['mail_senderhost'] # 发件服务器
        senderuser             = data['mail_senderuser'] # 发件人邮箱
        senderpass             = data['mail_senderpass'] # 发件人密码
        mailmessage            = MIMEText(data['STUID']+message,'plain','utf-8') # 邮件内容      
        mailmessage['Subject'] = message   # 邮件主题
        mailmessage['From']    = data['mail_senderuser'] # 发件人
        mailmessage['To']      =  ','.join(receivers)    # 收件人
        try:
            smtpObj = smtplib.SMTP() 
            smtpObj.connect(senderhost,25)
            smtpObj.login(senderuser,senderpass) 
            smtpObj.sendmail(senderuser,receivers,mailmessage.as_string())
            smtpObj.quit() 
            print('success')
        except smtplib.SMTPException as e:
            print('error',e)

# WxPusher
def sent_wxpusher(data=data,message="打卡失败"):
    if data['wx_alert'] == 1: # 是否添加微信提醒
        wxpusher_url     = 'http://wxpusher.zjiecode.com/api/send/message'
        wxpusher_header  = { 'Content-Type': "application/json", }
        wxpusher_data    = {
            "appToken"   : data['wx_appToken'],   # 微信提醒token
            "content"    : data['STUID']+message, # 微信提醒内容
            "summary"    : message, # 微信提醒主题
            "contentType": 1,
            "topicIds"   : [data['wx_topicIds']], # 微信关注主题，群发用
            "uids"       : [data['wx_uids']],     # 微信关注用户UID
            "url"        : "https://weixine.ustc.edu.cn/2020/login"
            }
        wxpusher_data = json.dumps(wxpusher_data)
        session.post(wxpusher_url,data=wxpusher_data,headers=wxpusher_header)

def sent_alert(report_res,data=data,message="打卡失败"):
    report_html = report_res.content.decode('utf-8')
    report_alert = re.findall('(?<=<p class="alert alert-success">)(.*?)(?=<a)', report_html)
    if (len(report_alert) == 0):
        print(message)
        sent_mail(data,message)
        sent_wxpusher(data,message)
        exit(0)
    else:
        print(report_alert[0])

def get_token():
    # 需要在同一session下执行
    session = requests.Session()

    # Step1: 获取CAS_LT
    CAS_LT_url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    CAS_LT_res = session.get(CAS_LT_url)
    CAS_LT_html = CAS_LT_res.content.decode()
    CAS_LT = re.findall('(?<=name="CAS_LT" value=")(.*?)(?=")', CAS_LT_html)[0]
    # print(CAS_LT)


    #Step2: 获取token
    login_url = 'https://passport.ustc.edu.cn/login'
    login_data = {
        'model': 'uplogin.jsp',
        'CAS_LT': CAS_LT,
        'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
        'warn': '',
        'showCode': '',
        'username': USR,
        'password': PWD,
        'button': ''
    }
    login_res = session.post(login_url, data=login_data)
    login_html = login_res.content.decode('utf-8')
    token_temp = re.findall('(?<=name="_token" value=")(.*?)(?=")', login_html)
    # 检查返回值是否正确
    if (len(token_temp) == 0):
        logininfo = "登录失败"
        print(logininfo)
        sent_mail(data,message=logininfo)
        sent_wxpusher(data,message=logininfo)
        exit(0)
    _token = token_temp[0]
    return session, _token

#Step3: 健康打卡上报
def health_report(session,_token):
    post_url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
    post_data = {
        '_token': _token,
        'juzhudi': LOCATION,
        'dorm_building': DORMBUILDING,
        'dorm': DORM,
        'body_condition': '1',
        'body_condition_detail': '',
        'now_status': '1',
        'now_status_detail': '',
        'has_fever': '0',
        'last_touch_sars': '0',
        'last_touch_sars_date': '',
        'last_touch_sars_detail': '',
        'is_danger': '0',
        'is_goto_danger': '0',
        'jinji_lxr': EMERGENCY_CONTACT,
        'jinji_guanxi': RELATIONSHIP,
        'jiji_mobile': PHONE_NUMBER,
        'other_detail': ''
    }
    health_res = session.post(post_url, data=post_data)
    sent_alert(health_res,data,message="健康打卡失败")


# Step4: 出校报备
def outgoing_report(session,_token):
    curr_date = datetime.datetime.now().strftime("%Y-%m-%d %T")
    print(curr_date)
    if datetime.datetime.now().hour >= 20:
        next_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %T")
    else:
        next_date = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime("%Y-%m-%d") + " 23:59:59"
    print(next_date)
    next_date_time = datetime.datetime.strptime(next_date,"%Y-%m-%d %H:%M:%S")

    # 申请报备第一页面,可以不打
    report_url1 = 'https://weixine.ustc.edu.cn/2020/apply/daliy'
    report_data1 = {
        '_token': _token,
        'lived':"2",
        'reason':"3"
    }
    #report_res = session.get(report_url1, data=report_data1)

    # 申请报备第二页面,必打,这里有复选框,使用json只能传递一个参数return_college
    report_url2 = 'https://weixine.ustc.edu.cn/2020/apply/daliy/ipost'
    wkd = next_date_time.isoweekday()
    report_data2 = [
        ('_token', _token),
        ('start_date', curr_date),
        ('end_date', next_date),
        # ('return_college[]','东校区'),
        # ('return_college[]','西校区'),
        # ('return_college[]','中校区'),
        ('reason', REASONOFOUTING[str(wkd)]),
        ('t', '3')
    ]
    for campus in CAMPUS_TRANSFER.split(","):
        report_data2.insert(3,('return_college[]',campus))
    outgoing_res = session.post(report_url2, data=report_data2)
    sent_alert(outgoing_res,data,message="出校报备失败")

if __name__ == "__main__":
    session,_token = get_token()
    health_report(session,_token)
    outgoing_report(session,_token)