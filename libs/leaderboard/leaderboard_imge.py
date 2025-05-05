import os
import imgkit
import asyncio
from config import config
medal_emojis = {
    1: "🥇",
    2: "🥈",
    3: "🥉"
}

medal_emoji_others = "🪙"

async def get_leaderboard(data):
    # 配置 wkhtmltoimage 路径
    if os.name == "nt":
        wkhtmltoimage_path = r"D:\Tool Software\wkhtmltopdf\bin\wkhtmltoimage.exe"
        wkhtml_config = imgkit.config(wkhtmltoimage=wkhtmltoimage_path)
    elif os.name == "posix":
        wkhtml_config = None

    rows = ""
    for rank, uid, username, count, amount in data:
        emoji = medal_emojis.get(rank, medal_emoji_others)
        medal_img = f'{emoji} TOP{rank}'
        rows += f"""
        <tr>
            <td>{medal_img}</td>
            <td>{uid}</td>
            <td>{username}</td>
            <td>{count}</td>
            <td>{amount}</td>
        </tr>
        """

    html_str = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid #999;
                padding: 6px;
                text-align: center;
            }}
            thead {{
                background-color: #4a72b2;
                color: white;
            }}
            caption {{
                caption-side: top;
                font-size: 16px;
                font-weight: bold;
                background-color: #4a72b2;
                color: white;
                padding: 6px;
                border: 1px solid #999;
            }}
        </style>
    </head>
    <body>
        <table>
            <caption>🌟🏅🎉 {config.MY_NAME}哥的个人打赏榜 🎉🏅🌟</caption>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>TGID</th>
                    <th>用户名</th>
                    <th>打赏次数</th>
                    <th>打赏金额</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """

    # 保存 HTML 到文件
    html_file = "libs/leaderboard/temp_leaderboard.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_str)

    # 生成图片
    imgkit.from_file(html_file, 'libs/leaderboard/leaderboard.png', config=wkhtml_config, options={
        'encoding': 'UTF-8',
        'format': 'png',
        'width': 512,
        'enable-local-file-access': ''
    })
    os.remove(html_file)
    return 'libs/leaderboard/leaderboard.png'
