#######################登录基础配置########################

API_ID = 11111
API_HASH = '1111111'
BOT_TOKEN_TEST = "转发bot的API暂时未写"
MY_NAME = 'dddd'    #  tg昵称榜单显示作用
NY_USERNAME = 'ssssss'   # tg 用户名
MY_TGID = 123344 # 自己的telegram id


############## movie_monitor_for115配置(将115分享群的电影进行TMDb检索并emby查询是否含有) #################

ADMIN_ID = [
    1111111111,
    1111111111,
    1111111111
]   
 #这是我为CMS建了一个群，然后将群里的消息转发给CMSbot，这是群里有权限的ID

M115_GROUP_ID = {
    "CMS_BOT_ID":111111,  #CMS的BOT的 ID（不是API）
    "CMS_TRANS_CHAT":-1111111  #自检的转发群
}

EMBY_API_KEY = "11111111111111"  # EMBY 的 API 密钥 用于检索enby
EMBY_SERVER = "http://192.168.1.1:8096/"  # EMBY 服务器地址
TMDB_API_KEY = "1111111111111111"  # TMDB 的 API 密钥


#####################朱雀Cookie##############################

ZHUQUE_COOKIE = "sssss"
ZHUQUE_X_CSRF = "xxxxxxxd"




########################运行代理配置########################

proxy_set = {
    'proxy_enable':True,#如果需要使用代理登录则设为true 反之False
    #tg登录的代理
    'proxy':{
        'scheme': 'socks5',  # "socks4", "socks5" and "http" are supported
        "hostname": '127.0.0.1',
        'port': 10801,
        'username': "",
        'password': ""
        },
    #网页访问用代理
    'PROXY_URL': 'http://127.0.0.1:10801'
}



PT_GROUP_ID = {
    "ZHUQUE_ID":-11111111, 
    "ZHUQUEBOCAI_ID":-111111111,
    "SSD_ID":-11111111,
    "SSDPUBLIC_ID":-11111111,
    "HY_ID":-1111111111,
    "HYSTAFF_ID":-11111111,
    "DOLBY_ID":-11111111,
    "AUDIENCES_ID":-1111111,
    "BOT_MESSAGE_CHAT":-1111111,
}


###################################auto_lotttery配置#############################

auto_choujiang = True # 是否开启自动抽奖功能
MY_PTID = 'LuckyDonne'
#抽奖开启时段
TIME_RANGES = [
    ("08:00", "12:00"),
    ("14:00", "22:00")
]

#参与抽奖的群组
LOTTERY_TARGET_GROUP = [
    PT_GROUP_ID['ZHUQUE_ID'],
    PT_GROUP_ID['DOLBY_ID'],
    PT_GROUP_ID['HY_ID'],
    PT_GROUP_ID['HYSTAFF_ID'],
    PT_GROUP_ID['SSD_ID'],
    PT_GROUP_ID['AUDIENCES_ID']
]
#参与抽奖的奖品
PRIZE_LIST = {
    "ZHUQUE_ID":['灵石','零食','LS'],            
    "DOLBY_ID":['鲸币','🐳币','JB'],
    "SSD_ID":['茉莉'],
    "AUDIENCES_ID":['爆米花'],
    "PTclub":['猫粮'],
    "HHclub":['憨豆'],
    "Test_ID":['test']
}   #设置需要参数的奖品名 暂不支持修改新增key




################################数据库配置##############################


DB_INFO = {
    "dbset":"mySQL", #mySQL/SQLite
    "address":"111.111.1.11",
    "db_name":"数据库名称",    
    "port":3306,
    "user":"用户名",
    "password":"密码"
}







