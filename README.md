# USTC 出校报备与健康打卡

之前的一个项目使用的包过多，使得配置环境时很麻烦，查看了一下网页，发现可以使用爬虫直接进行打卡，因而有了此项目。

#### 主要功能

* 健康打卡: 每天不打卡, 学校会发邮件, 挺烦的
* 出校报备: 2022-09-19更新, 授权安徽电信和安徽移动获取行程码信息后, 可以实现出校报备

* 添加了打卡失败邮件提醒, 需添加发件人信息, 收件人信息, 但由于邮件有延迟, 不建议使用
* 添加了打卡失败微信提醒, 只需添加`wx_appToken`,`wx_uids`即可



#### 运行方式

1. 直接运行下面命令即可

   ```shell
   python3 ustc_report.py data_test.json # 调整为自己的路径
   ```

2. 通过crontab, schedule(python)等周期工具, 根据个人习惯和偏好打卡时间定时上报. 如将上述命令写进一脚本文件 autoreport.sh 中, 通过crontab调用此文件实现定时打卡. 或者使用如下的脚本, 后台运行

   ```python
   # 如使用schedule: 将下面的代码保存为autoreport.py, 然后运行。个人不习惯这种方式，所以没有加进 ustc_report.py 中
   import os
   try:
       import schedule
   except ModuleNotFoundError:
       print('package Not find')
       os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple schedule')
       import schedule
       
   ustc_rep = "/" # 调整为自己的路径
   def daka():
       os.system("python3 %s/ustc_report.py %s/data_test.json"%(ustc_rep,ustc_rep))
   
   schedule.every().day.at("6:25").do(daka)
   schedule.every().day.at("22:25").do(daka)
   while True:
       schedule.run_pending()
       time.sleep(60)
   ```

### data.json

```json
{
    "STUID"            : "SA2122",             //学号
    "STUPW"            : "PassWord",           //密码
    "LOCATION"         : "南校区",              //所在校区
    "DORM_BUILDING"    : "1",                  //宿舍楼号
    "DORM"             : "129",                //宿舍号
    "EMERGENCY_CONTACT": "严济慈",              //紧急联系人姓名
    "RELATIONSHIP"     : "校长",                //紧急联系人关系
    "PHONE_NUMBER"     : "12345678901",        //紧急联系人电话
    "REASONOFOUTING"   : {                     //报备原因,周一到周日
        "1" : "实验室往返",
        "2" : "实验室往返",
        "3" : "实验室往返",
        "4" : "课题组组会",
        "5" : "南北区往返",
        "6" : "游泳",
        "7" : "吃夜宵"
    },
    "CAMPUS_TRANSFER"  : "东校区,西校区,中校区,南校区,北校区",  //跨校区,不要有空格

    "mail_alert"       : 0,                    //是否邮件提醒
    "mail_receivers"   : "demo@qq.com",        //收件人
    "mail_senderhost"  : "smtp.qq.com",        //发件服务器
    "mail_senderuser"  : "mylove@qq.com",      //发件人邮箱
    "mail_senderpass"  : "",                   //发件人密码

    "wx_alert"         : 0,                    //是否微信提醒 WxPusher
    "wx_appToken"      : "",                   //程序单发, 与下面二选一
    "wx_topicIds"      : "",                   //话题群发, 可不填
    "wx_uids"          : "UID_"                //微信关注UID号
}
```



### 版本更新

##### Version 3

* v3.0  2022-09-19 v3.0 changelog: pass info was updated using Anhui phone number by school



##### Version 2

* v2.7 changelog: post address was modified by school
* v2.6 changelog: get more requirement code by the official document release by school
* v2.5 changelog: add different reasons for weekday and weekend
* v2.4 changelog: add reason of outgoing
* v2.3 changelog: add WxPusher alert
* v2.2 changelog: add dorm and dorm building
* v2.1 changelog: add multi-mail receivers
* v2.0 changelog: divide file into script and data



##### Version 1

* v1.3 changelog: out update

* v1.2 changelog: add email alert

* v1.1 modified by chopong 2022.03.18 changelog: locale data form was updated by school
* version 1.0 2022.03.17 changelog: in and out of school record
