API_ID = 123
API_HASH = '456'

my_name = "xxxxxx"    #  tg用户名榜单显示作用
my_id = 12345   # 自己的telegram id
my_ptid = "xxxxx" #PT用户名 作为抽奖领奖用
FINSTA_ID = 12346 # 小号 的的telegram id 用于监听小号发的指令

ZHUQUE_COOKIE = ""
ZHUQUE_X_CSRF = ""

audiences_COOKIE = ""

file_path = '/DonneFile/mytgbot/firetime.txt' #文件保存路径
auto_choujiang = False # 是否开启自动抽奖功能，默认关闭

#自动抽奖开启时间段
start_time1 = '09:00:00+08:00'
start_time2 = '12:30:00+08:00'
end_time1 = '14:30:00+08:00'
end_time2 = '23:00:00+08:00'

proxy_set = {
    'proxy_enable':True,#如果需要使用代理登录则设为true 反之False
    'proxy':{
        'scheme': 'socks5',  # "socks4", "socks5" and "http" are supported
        "hostname": '127.0.0.1', #代理服务器地址
        'port': 10000, #代理端口
        'username': "", #账号 未设置账号密码则保持""
        'password': "" #密码 未设置账号密码
        }
    }

banned_group_ID = {
                   "SSD_ID":-1002014253433,
                   "HY_ID":-1001873711923,
                   "HYSTAFF_ID":-1001788987573,
                   "DOLBY_ID":-1002131053667,
                   }

GROUP_ID = {"ZHUQUE_ID": -1,
            "SSD_ID":-2,
            "HY_ID":-3,
            "HYSTAFF_ID":-4,
            "DOLBY_ID":-5,
            "PRIVATE_ID": -6,
            }
GROUP_NAME = {"ZHUQUE_ID":"zhuque_KeepAccounts",
            "SSD_ID":"ssd_KeepAccounts",
            "HY_ID":"redleaves_KeepAccounts",
            "HYSTAFF_ID":"redleaves_KeepAccounts",
            "DOLBY_ID":"hddolby_KeepAccounts",
            "PRIVATE_ID":"private_KeepAccounts",
            }

target_group = [GROUP_ID['ZHUQUE_ID'],
                GROUP_ID['DOLBY_ID'],
                GROUP_ID['HY_ID'],
                GROUP_ID['HYSTAFF_ID'],
                GROUP_ID['SSD_ID'],
                GROUP_ID['HY_ID']
                -1002245697979,
                ]

prize_list = {"ZHQUE_ID":['灵石','零食','LS'],
              "DOLBY_ID":['鲸币','🐳币'],
              "SSD":['茉莉'],
              "audiences":['爆米花'],              
              "PTclub":['猫粮'],
              "HHclub":['憨豆'],
              }   #

db_info = {"address":"192.168.2.11", #mysql ip
           "db_name":"jizhang", #mysql ip 数据库名称
           "port":3306, #mysql ip
           "user":"root", #mysql 用户名
           "password":"77……"#mysql 密码
           }



