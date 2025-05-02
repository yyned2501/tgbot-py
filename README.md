# pyrogram_mytgbot
个人tg脚本:

1.使用前需要安装依赖包:

    1.1 pyrogram    
    1.2 tgcrypto    
    1.3 aiohttp    
    1.4 pymysql     
    1.5 apscheduler    
    1.6 openai

2.将下载后的所有*_example文件文件名里面的"_example"删除 如config_example.py改成config.py

3.配置config文件:

    3.1 config内有举例说明则不再赘述

4.配置完成后首次登录运行请用python3 mybotmain.py,不要使用nohup python3 mybotmain.py，登录完后生成.session文件后则无关可以直接./tgpu启动

5.请妥善保管您的.session文件，这是您tg的登录信息。

6.之后每次运行只需要运行mybotmain.py文件，或者使用./tgpu

7各文件说明:

    7.1 libs文件夹中的都是一些被引用的函数型方法      
        7.1.1 spinThePrizeWheel.py 是朱雀的大转盘抽奖方法函数       
        7.1.2 zhuque_getInfo.py 是朱雀的个人信息获取方法       
        7.1.3 zhuque_listBackpack.py 是朱雀的背包清单查询       
        7.1.4 zhuque_recycleMagicCard.py 是朱雀背包卡片回收       
        7.1.5 others.py中是自定义的一些函数，方便程序引用        
        7.1.6 database.py 是Mysql数据库访问的一些方法    
    7.2 filters文件夹中是自定义的tg消息过滤    
    7.3 scrpts文件中是针对tg的脚本      
        7.3.1 normal.py 转发抽奖信息到个人群组作为提醒       
        7.3.2 testmessage.py 测试使用       
        7.3.3 zhuque_aiohttp 是将libs中的一些朱雀操作方法整合至tg内使用       
        7.3.4 zhuque_ firegenshinmagic.py 朱雀tg群内自动释放脚本        
        7.3.5 zhuque_function_summary.py 目前为朱雀群内转账记录 后续会将7.3.3 7.3.4都整合至里面
    7.4 repy_message.py 是tg群内作为回复的一些内容整个内有具体说明

