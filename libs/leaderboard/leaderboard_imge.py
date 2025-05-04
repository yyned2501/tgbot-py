import os
import imgkit
import asyncio

# 奖牌图标路径
medal_icons = {
    1: "./emoj_imges/1st.png",
    2: "./emoj_imges/2nd.png",
    3: "./emoj_imges/3rd.png"    
}

async def get_leaderboard(data):

    # 配置 wkhtmltoimage 路径
    if os.name == "nt":
        wkhtmltoimage_path = r"D:\Tool Software\wkhtmltopdf\bin\wkhtmltoimage.exe"
        config = imgkit.config(wkhtmltoimage=wkhtmltoimage_path)
    elif os.name == "posix":
        config = None

    rows = ""
    for rank, uid, username, count, amount in data:
        if rank in medal_icons:
            medal_img = f'<img src="{medal_icons[rank]}" width="20"> TOP{rank}'
        else:
            medal_img = f'<img src="./emoj_imges/4th.png" width="20"> TOP{rank}'
        rows += f"""
        <tr>
            <td>{medal_img} </td>
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
            <caption>🏆💰 Lucky的个人打赏榜单 🎁📊</caption>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>ID</th>
                    <th>用户名</th>
                    <th>次数</th>
                    <th>金额</th>
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
    imgkit.from_file(html_file, 'libs/leaderboard/leaderboard.png', config=config, options={
        'encoding': 'UTF-8',
        'format': 'png',
        'width': 512,
        'enable-local-file-access': ''  # 添加这行
    })
    os.remove(html_file)    
    return 'libs/leaderboard/leaderboard.png'




