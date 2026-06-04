#region ==================== 插件导入库 ====================
from astrbot.api.all import *
from astrbot.api.message_components import Image, Plain
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig
from datetime import datetime, timedelta
import yaml
import json
import copy
from collections import OrderedDict
import os
import httpx
import pytz
import re
import random
import logging
import shutil
import time
import asyncio
from PIL import ImageColor, Image as PILImage
from PIL import ImageDraw, ImageFont, ImageOps
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple
#endregion

#region ==================== 插件配置 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
# 路径配置
    #基础目录
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
WAC_DATA_DIR= os.path.join('data', 'plugins_WealthAndContract_data')

    #配置文件
DATA_FILE = os.path.join(WAC_DATA_DIR, 'WAC_data.json')
PROP_DATA_FILE = os.path.join(WAC_DATA_DIR, 'WAC_propdata.json')
SOCIAL_DATA_FILE = os.path.join(WAC_DATA_DIR, 'WAC_social_data.json')  # 社交数据文件
TIME_DATA_FILE = os.path.join(WAC_DATA_DIR, 'WAC_time_data.json')  # 时间数据文件
STOCK_DATA_FILE = os.path.join(WAC_DATA_DIR, 'stock_data.json')
STOCK_USER_DATA_FILE = os.path.join(WAC_DATA_DIR, 'stock_user_data.json')
AUTH_DATA_FILE = os.path.join(WAC_DATA_DIR, 'WAC_auth_data.json')
BLACKLIST_DATA_FILE = os.path.join(WAC_DATA_DIR, 'blacklist_data.json')
ASSET_DATA_FILE = os.path.join(WAC_DATA_DIR, 'asset_data.json')  # 资产数据文件路径
CERTIFICATE_DATA_FILE = os.path.join(WAC_DATA_DIR, 'certificate_data.json')  # 证件数据文件路径

    #插件依赖
IMAGE_DIR = os.path.join(PLUGIN_DIR, 'images')
FONT_PATH = os.path.join(PLUGIN_DIR, 'miaowu_cute_font.ttf')

    #插件工作初始值
STOCK_REFRESH_INTERVAL = 300    # 5分钟刷新一次股票
TRADING_HOURS = (8, 18)  # 交易时间：8:00-18:00

# API配置
AVATAR_API = "http://q.qlogo.cn/headimg_dl?dst_uin={}&spec=640&img_type=jpg"

# 授权等级定义
AUTH_LEVELS = {
    1: "查阅管理员",
    2: "股票管理员",
    3: "操作管理员",
    4: "数据管理员"
}

#region 资产与证件系统配置
# 资产类型配置
ASSET_TYPES = {
    "房产": {
        "碧桂园": {"price": 50000, "description": "普通住宅"},
        "万科": {"price": 80000, "description": "中档住宅"},
        "恒大": {"price": 120000, "description": "高档住宅"},
        "汤臣一品": {"price": 500000, "description": "顶级豪宅"}
    },
    "车子": {
        "比亚迪": {"price": 100000, "description": "经济型轿车"},
        "丰田": {"price": 200000, "description": "中档轿车"},
        "奔驰": {"price": 500000, "description": "豪华轿车"},
        "保时捷": {"price": 1000000, "description": "跑车"},
        "劳斯莱斯": {"price": 1500000, "description": "顶级豪车"}
    }
}

# 证件类型配置
CERTIFICATE_TYPES = {
    "结婚证": {
        "requirements": ["房产", "车子"],
        "description": "证明夫妻关系的法律文件"
    },
    "房产证": {
        "requirements": ["房产"],
        "description": "证明房产所有权的法律文件"
    },
    "行驶证": {
        "requirements": ["车子"],
        "description": "证明车辆所有权的法律文件"
    },
    "离婚证": {
        "requirements": ["结婚证"],
        "description": "证明解除婚姻关系的法律文件"
    }
}

#endregion

# 经济系统配置
WEALTH_LEVELS = [
    (0,    "平民", 0.25),
    (500,  "小资", 0.5),
    (2000, "富豪", 0.75),
    (5000, "巨擘", 1.0),
    (10000, "成功人士", 1.25)
]
WEALTH_BASE_VALUES = {
    "平民": 100,
    "小资": 500,
    "富豪": 2000,
    "巨擘": 5000,
    "成功人士": 10000
}

BASE_INCOME = 100.0 #基础值

# 初始股票列表
DEFAULT_STOCKS = {
    "茅台科技": {
        "price": 1500.0,
        "volatility": 0.08,
        "trend": "up",
        "trend_count": 0
    },
    "企鹅控股": {
        "price": 450.0,
        "volatility": 0.12,
        "trend": "down",
        "trend_count": 0
    },
    "阿里爸爸": {
        "price": 180.0,
        "volatility": 0.15,
        "trend": "random",
        "trend_count": 0
    },
    "狗东商城": {
        "price": 75.0,
        "volatility": 0.18,
        "trend": "flat",
        "trend_count": 0
    },
    "拼夕夕": {
        "price": 90.0,
        "volatility": 0.20,
        "trend": "up",
        "trend_count": 0
    },
    "美団外卖": {
        "price": 220.0,
        "volatility": 0.10,
        "trend": "down",
        "trend_count": 0
    },
    "小鹏电车": {
        "price": 35.0,
        "volatility": 0.25,
        "trend": "random",
        "trend_count": 0
    },
    "宁德电池": {
        "price": 280.0,
        "volatility": 0.09,
        "trend": "up",
        "trend_count": 0
    },
    "农夫三拳": {
        "price": 45.0,
        "volatility": 0.07,
        "trend": "flat",
        "trend_count": 0
    },
    "中国平安": {
        "price": 55.0,
        "volatility": 0.06,
        "trend": "down",
        "trend_count": 0
    },
    "字节跳动": {
        "price": 300.0,
        "volatility": 0.15,
        "trend": "up",
        "trend_count": 0
    },
    "特斯拉": {
        "price": 250.0,
        "volatility": 0.22,
        "trend": "random",
        "trend_count": 0
    },
    "苹果科技": {
        "price": 180.0,
        "volatility": 0.11,
        "trend": "flat",
        "trend_count": 0
    },
    "微软": {
        "price": 350.0,
        "volatility": 0.13,
        "trend": "up",
        "trend_count": 0
    },
    "谷歌": {
        "price": 280.0,
        "volatility": 0.14,
        "trend": "down",
        "trend_count": 0
    }
}

#region 工作配置
JOBS = {
    "搬砖": {
        "reward": (15.0, 20.0),      # 收益范围
        "success_rate": 1.0,
        "risk_cost": (0.0, 0.0),     # 失败惩罚范围
        "success_msg": "⛏️ {worker_name} 去工地搬了一天砖，累得筋疲力尽。你获得了 {reward:.2f} 金币！",
        "failure_msg": ""
    },
    "送外卖": {
        "reward": (20.0, 25.0),
        "success_rate": 0.9,
        "risk_cost": (1.0, 3.0),
        "success_msg": "🚴 {worker_name} 一天骑车狂奔送外卖，终于赚到 {reward:.2f} 金币！",
        "failure_msg": "🍔 {worker_name} 在送餐路上摔了一跤，赔了客户的订单，损失 {risk_cost:.2f} 金币。"
    },
    "送快递": {
        "reward": (25.0, 30.0),
        "success_rate": 0.8,
        "risk_cost": (3.0, 6.0),
        "success_msg": "📦 {worker_name} 风里雨里送快递，终于赚到了 {reward:.2f} 金币。",
        "failure_msg": "📭 {worker_name} 快递丢件，被客户投诉，赔了 {risk_cost:.2f} 金币。"
    },
    "家教": {
        "reward": (30.0, 35.0),
        "success_rate": 0.7,
        "risk_cost": (6.0, 9.0),
        "success_msg": "📚 {worker_name} 耐心辅导学生，家长满意，赚得 {reward:.2f} 金币。",
        "failure_msg": "😵 {worker_name} 学生成绩没提高，被辞退，损失 {risk_cost:.2f} 金币。"
    },
    "挖矿": {
        "reward": (35.0, 40.0),
        "success_rate": 0.6,
        "risk_cost": (9.0, 12.0),
        "success_msg": "⛏️ {worker_name} 在地下挖矿一整天，挖到了珍贵矿石，获得 {reward:.2f} 金币！",
        "failure_msg": "💥 {worker_name} 不小心引发了塌方事故，受伤并损失 {risk_cost:.2f} 金币。"
    },
    "代写作业": {
        "reward": (40.0, 45.0),
        "success_rate": 0.5,
        "risk_cost": (12.0, 15.0),
        "success_msg": "📘 {worker_name} 偷偷帮人代写作业，轻松赚到 {reward:.2f} 金币。",
        "failure_msg": "📚 {worker_name} 被老师发现代写，被罚 {risk_cost:.2f} 金币。"
    },
    "奶茶店": {
        "reward": (45.0, 50.0),
        "success_rate": 0.4,
        "risk_cost": (15.0, 18.0),
        "success_msg": "🧋 {worker_name} 在奶茶店忙了一天，挣了 {reward:.2f} 金币。",
        "failure_msg": "🥤 {worker_name} 手滑打翻整桶奶茶，赔了 {risk_cost:.2f} 金币。"
    },
    "偷窃苏特尔的宝库": {
        "reward": (500.0, 500.0),          # 固定奖励
        "success_rate": 0.02,      # 5%的成功率
        "risk_cost": (10.0, 10.0),         # 固定惩罚
        "success_msg": "🌟 {worker_name} 偷窃成功，从苏特尔的钱包中获得了难以置信的 {reward:.2f} 金币！",
        "failure_msg": "💫 {worker_name} 偷窃失败，被苏特尔当场抓获，幕后黑手的你赔付了{risk_cost:.2f} 金币了。"
    },
    "当家仆": {
        "reward": (80.0, 350.0),  # 高报酬
        "success_rate": 0.35,     # 65%失败率
        "risk_cost": (30.0, 50.0), # 高额风险
        "success_msg": "💄 {worker_name} 服务客人令客人十分满意，赚取了 {reward:.1f} 金币！",
        "failure_msg": "🩹 {worker_name} 服务客人令客人十分不满，客人恶意针对 {worker_name} ，医药花销 {risk_cost:.1f} 金币。"
    }
}
#endregion

#region 道具系统配置
SHOP_ITEMS = {
    "驯服贴": {
        "price": 10000,
        "description": "永久绑定性奴，防止被制裁/赎身/强制购买，超出限定名额额外费用公式: 2000 * 2 * (当前数量 + 1)",
        "type": "use",
        "command": "驯服贴"
    },
    "强制购买符": {
        "price": 5000,
        "description": "强制购买已有主人的性奴",
        "type": "use",
        "command": "强制购买符"
    },
    "自由身保险": {
        "price": 800,
        "description": "3小时内不被购买为性奴",
        "duration_hours": 3,
        "type": "use",
        "command": "自由身保险"
    },
    "红星制裁": {
        "price": 500,
        "description": "对全群满足条件的用户进行制裁（每人每天限用1次）",
        "type": "use",
        "command": "红星制裁"
    },
    "市场侵袭": {
        "price": 400,
        "description": "对指定用户发起侵袭（每人每小时限用1次）",
        "type": "use",
        "command": "市场侵袭"
    },
    "美式咖啡": {
        "price": 80,
        "description": "减少一次今日约会计数（不能低于0）",
        "type": "use",
        "command": "美式咖啡"
    },
    "卡天亚戒指": {
        "price": 520,
        "description": "缔结恋人关系所需的道具",
        "type": "social",
        "command": "卡天亚戒指"
    },
    "一壶烈酒": {
        "price": 349,
        "description": "缔结兄弟关系所需的道具",
        "type": "social",
        "command": "一壶烈酒"
    },
    "黑金卡": {
        "price": 666,
        "description": "缔结包养关系所需的道具",
        "type": "social",
        "command": "黑金卡"
    },
    "玫瑰花束": {
        "price": 300,
        "description": "赠送可增加5-10点好感度（基础）",
        "type": "gift",
        "command": "玫瑰花束"
    },
    "定制蛋糕": {
        "price": 400,
        "description": "赠送可增加8-15点好感度（基础）",
        "type": "gift",
        "command": "定制蛋糕"
    },
    "永恒钻戒": {
        "price": 1314,
        "description": "升级为夫妻关系所需的道具",
        "type": "social",
        "command": "永恒钻戒"
    },
    "金兰谱": {
        "price": 934,
        "description": "升级为结义兄弟所需的道具",
        "type": "social",
        "command": "金兰谱"
    },
    "白金卡": {
        "price": 888,
        "description": "升级为长期包养所需的道具",
        "type": "social",
        "command": "白金卡"
    },
    "限量版玫瑰": {
        "price": 900,
        "description": "赠送可增加15-25点好感度（升级关系专用）",
        "type": "gift",
        "command": "限量版玫瑰"
    },
    "定制珠宝": {
        "price": 1000,
        "description": "赠送可增加20-35点好感度（升级关系专用）",
        "type": "gift",
        "command": "定制珠宝"
    },
    "百合花蜜": {
        "price": 950,
        "description": "升级为百合所需的道具",
        "type": "social",
        "command": "百合花蜜"
    },
    "百合花种": {
        "price": 590,
        "description": "升级为闺蜜所需的道具",
        "type": "social",
        "command": "百合花种"
    },
    "彩票": {
        "price": 5,
        "description": "购买彩票，有机会获得大奖（每日限用10次）",
        "type": "use",
        "command": "彩票"
    },
    "贿赂券": {
        "price": 300,
        "description": "在红星制裁中免疫制裁（90%概率）",
        "type": "use",
        "command": "贿赂券"
    },
    "媚药": {
        "price": 50,
        "description": "强制社交所需道具（不可直接使用）",
        "type": "special",
        "command": "媚药"
    }
}
#endregion

#region 社交系统配置
DATE_EVENTS = [
    {
        "id": "movie",
        "name": "电影院约会",
        "description": "你们在电影院看了一场感人的电影，相视一笑。",
        "favorability_change": (3, 5)
    },
    {
        "id": "rain",
        "name": "被雨淋湿",
        "description": "约会途中突然下雨，两人被淋湿，气氛有些尴尬。",
        "favorability_change": (-2, 0)
    },
    {
        "id": "restaurant",
        "name": "共进晚餐",
        "description": "你们在一家浪漫的餐厅共进晚餐，氛围很好。",
        "favorability_change": (2, 4)
    },
    {
        "id": "amusement_park",
        "name": "游乐园",
        "description": "在游乐园里，你们勇敢地尝试了各种刺激的项目，留下了美好的回忆。",
        "favorability_change": (2, 5)
    },
    {
        "id": "cooking",
        "name": "一起做饭",
        "description": "你们一起在家做饭，虽然过程有些混乱，但最终做出了美味的菜肴。",
        "favorability_change": (2, 5)
    },
    {
        "id": "star_gazing",
        "name": "观星",
        "description": "在郊外的草地上，你们一起观星，聊着各自的梦想和未来。",
        "favorability_change": (3, 5)
    },
    {
        "id": "argument",
        "name": "争吵",
        "description": "约会过程中，因为一些小事，你们发生了争执，气氛有些紧张。",
        "favorability_change": (-3, -1)
    },
    {
        "id": "open_the_room",
        "name": "住酒店",
        "description": "约会过程中，因为一些原因夜深了，你们去酒店开了房，中途发生了什么就不得而知了，反正两位对对方的好感涨了不少。",
        "favorability_change": (50, 150)
    }
]

RELATION_LIMITS = {
    "lover": 1,       # 恋人关系仅限1个
    "brother": -1,    # 兄弟关系无限制
    "patron": -1,     # 包养关系无限制
    "spouse": 1,      # 夫妻关系仅限1个
    "sworn_brother": -1,  # 结义兄弟无限制
    "long_term_patron": -1, # 长期包养无限制
    "bff": -1,  # 闺蜜无限制
    "yuri": -1  # 百合无限制
}

RELATION_UPGRADES = {
    "lover": "spouse",           # 恋人可升级为夫妻
    "brother": "sworn_brother",  # 兄弟可升级为结义兄弟
    "patron": "long_term_patron", # 包养可升级为长期包养
    "bff": "yuri" # 闺蜜可升级为百合
}

UPGRADE_ITEMS = {
    "spouse": "永恒钻戒",          # 升级夫妻所需道具
    "sworn_brother": "金兰谱",    # 升级结义兄弟所需道具
    "long_term_patron": "白金卡",   # 升级长期包养所需道具
    "yuri": "百合花蜜" # 升级百合所需道具
}

UPGRADE_BONUS = {
    "spouse": 15.0,             # 夫妻关系签到加成
    "sworn_brother": 10.0,      # 结义兄弟签到加成
    "yuri": 10.0,          # 百合签到加成
    "long_term_patron": 20.0    # 长期包养签到加成
}

BASE_RELATION_BONUS = {
    "lover": 5.0,
    "brother": 3.0,
    "patron": 8.0,
    "bff": 4.0
}

# 关系类型名称映射
RELATION_TYPE_NAMES = {
    "lover": "恋人",
    "brother": "兄弟", 
    "patron": "包养关系",
    "spouse": "夫妻",
    "sworn_brother": "结义兄弟",
    "long_term_patron": "长期包养",
    "bff": "闺蜜",
    "yuri": "百合"
}

# 关系礼物加成
RELATION_GIFT_BONUS = {
    "lover": {"玫瑰花束": (10, 15), "定制蛋糕": (15, 25)},
    "spouse": {"限量版玫瑰": (15, 25), "定制珠宝": (20, 35)},
    "brother": {"一壶烈酒": (8, 15)},
    "sworn_brother": {"金兰谱": (15, 25)},
    "patron": {"黑金卡": (10, 20)},
    "long_term_patron": {"白金卡": (20, 30)},
    "bff": {"百合花种": (20, 30)},
    "yuri": {"百合花蜜": (20, 30)},
}

SOCIAL_EVENTS = {
    "看电影": {
        "success_rate": 0.9,
        "favorability_change": (20, 50),
        "min_favorability": 100,
        "success_msgs": [
            "🎬 {inviter_name} 和 {target_name} 在私人影院里越靠越近…黑暗中两人的呼吸声越来越重，好感度 +{change}",
            "💺 {target_name} 的手'不小心'碰到了{inviter_name}的腿，却迟迟没有移开…好感度 +{change}",
            "🍿 共享爆米花时{inviter_name}故意咬到了{target_name}的手指，两人对视一笑，好感度 +{change}",
            "😘 看到浪漫处{inviter_name}突然亲了{target_name}的脸颊，{target_name}脸红到耳根，好感度 +{change}",
            "🛋️ {inviter_name} 把{target_name}搂在怀里，手指轻轻划过对方的腰际，好感度 +{change}",
            "🌙 电影结束后两人在空荡荡的影厅里缠绵亲吻，工作人员都不敢进来打扰，好感度 +{change}",
            "👄 {inviter_name} 借着黑暗悄悄在{target_name}耳边低语：“你好香啊…”好感度 +{change}",
            "💞 看到激情戏时两人不约而同地看向对方，眼神拉丝，好感度 +{change}",
            "🔥 {target_name} 跨坐在{inviter_name}腿上，银幕光影映照着两人交叠的身影，好感度 +{change}",
            "❣️ {inviter_name} 的手不安分地伸进{target_name}的衣服里，被轻轻拍开却笑得更深，好感度 +{change}"
        ],
        "failure_msgs": [
            "😴 {inviter_name} 选的文艺片太闷，{target_name} 睡得打呼噜还流口水，好感度 -{change}",
            "📱 {target_name} 全程和前任发消息，{inviter_name}气得差点砸爆米花，好感度 -{change}",
            "💨 {inviter_name} 不小心放了个屁，整个影厅都在偷笑，{target_name} 假装不认识他，好感度 -{change}",
            "🍫 {inviter_name} 准备的巧克力融化在口袋里，掏出来时黏糊糊一大坨，{target_name} 一脸嫌弃，好感度 -{change}",
            "👻 恐怖片太吓人，{target_name} 一拳打中了{inviter_name}的鼻子，好感度 -{change}"
        ]
    },
    "共进晚餐": {
        "success_rate": 0.8,
        "favorability_change": (30, 60),
        "min_favorability": 150,
        "success_msgs": [
            "🍷 {inviter_name} 喂{target_name}吃草莓时故意舔了下指尖，{target_name} 腿都软了，好感度 +{change}",
            "💋 餐后甜点上写着“我爱你”，{inviter_name} 当着全场面深吻{target_name}，好感度 +{change}",
            "🦵 桌下{inviter_name}用脚轻轻摩擦{target_name}的大腿，{target_name}脸红着夹紧了腿，好感度 +{change}",
            "🍾 香槟酒洒在{target_name}胸口，{inviter_name}俯身去舔…被服务员撞个正着，好感度 +{change}",
            "👠 {target_name} 脱了高跟鞋用脚趾挑逗{inviter_name}的裤裆，一顿饭吃了三小时，好感度 +{change}",
            "🥩 {inviter_name} 切好牛排喂到{target_name}嘴边，却突然转方向喂进自己嘴里，引得对方娇嗔，好感度 +{change}",
            "🔥 两人在餐厅角落热吻到忘我，刀叉掉地上都浑然不觉，好感度 +{change}",
            "💞 {inviter_name} 突然单膝跪地掏出戒指盒…结果里面是奶油，舔掉后吻上{target_name}的唇，好感度 +{change}",
            "👅 {target_name} 吃完冰淇淋后{inviter_name}突然吻上去说“尝尝你的味道”，好感度 +{change}",
            "🪑 {inviter_name} 把{target_name}抱到自己腿上喂饭，一顿饭吃得欲火焚身，好感度 +{change}"
        ],
        "failure_msgs": [
            "🌶️ {inviter_name} 点了变态辣，{target_name} 吃完直接送医洗胃，好感度 -{change}",
            "💸 结账时发现要AA制，{target_name} 翻着白眼掏钱，好感度 -{change}",
            "🐛 沙拉里吃出菜虫，{target_name} 当场呕吐在{inviter_name}名牌西装上，好感度 -{change}",
            "💨 {inviter_name} 吃太多大蒜，接吻时{target_name}被熏晕过去，好感度 -{change}",
            "👨👩👧 吃到一半遇到{target_name}全家来聚餐，尴尬得脚趾抠地，好感度 -{change}"
        ]
    },
    "公园散步": {
        "success_rate": 0.95,
        "favorability_change": (44, 70),
        "min_favorability": 220,
        "success_msgs": [
            "🌸 {inviter_name} 把{target_name}压倒在樱花树下，花瓣飘落中两人忘情亲吻，好感度 +{change}",
            "🌳 小树林里{inviter_name}从背后抱住{target_name}，手悄悄探进衣摆，好感度 +{change}",
            "💫 长椅上{target_name}跨坐在{inviter_name}腿上扭动，远处传来脚步声才慌忙分开，好感度 +{change}",
            "👗 突然下雨，{inviter_name}脱下衬衫裹住{target_name}，发现里面是性感内衣，好感度 +{change}",
            "🛝 滑滑梯上{inviter_name}抱着{target_name}一起滑下，黑暗中被摸遍全身，好感度 +{change}",
            "🌙 月光下{target_name}主动拉开{inviter_name}的裤链，被巡逻的手电筒照到尖叫逃跑，好感度 +{change}",
            "💞 秋千荡到最高点时{inviter_name}吻上{target_name}的唇，两人在空中缠绵，好感度 +{change}",
            "🔥 喷泉旁{target_name}被淋湿透，透明衬衫下的身材让{inviter_name}直接硬了，好感度 +{change}",
            "👅 长椅深吻到{target_name}口红全花，{inviter_name}笑着说“这样更性感”，好感度 +{change}",
            "📸 假装拍照却偷拍{target_name}裙底，被发现后反而被撒娇“删掉啦~”，好感度 +{change}"
        ],
        "failure_msgs": [
            "🐕 被流浪狗追着跑，{target_name} 高跟鞋跑断跟，气哭，好感度 -{change}",
            "💩 {inviter_name} 不小心踩到狗屎，{target_name} 拒绝同车回家，好感度 -{change}",
            "👮 亲热时被保安拿手电筒照脸，社会性死亡，好感度 -{change}",
            "🦟 蚊子包咬满全身，{target_name} 痒到没心情暧昧，好感度 -{change}",
            "🌧️ 暴雨突至两人成落汤鸡，{target_name} 妆花成鬼，好感度 -{change}"
        ]
    },
    "风月": {
        "success_rate": 0.65,
        "favorability_change": (150, 190),
        "min_favorability": 500,
        "success_msgs": [
            "🌙 {inviter_name} 轻轻将 {target_name} 带入帷帐，月光下只余交叠的剪影与细碎的私语，好感度 +{change}",
            "🕯️ 烛光摇曳，{target_name} 的衣带不知何时已松散，{inviter_name} 指尖轻触如抚琴弦，好感度 +{change}",
            "🌺 芙蓉帐暖，{inviter_name} 在 {target_name} 耳边低吟一首只有两人懂得的诗，好感度 +{change}",
            "🎻 如同协奏曲般的夜晚，{target_name} 的喘息与 {inviter_name} 的心跳奏出和谐的旋律，好感度 +{change}",
            "🖼️ 仿佛一幅古典油画，{target_name} 慵懒地倚在锦缎中，{inviter_name} 细细欣赏这私藏的美景，好感度 +{change}",
            "🍷 醇酒般的夜晚令人微醺，{target_name} 在 {inviter_name} 的引导下品尝了禁忌的甘美，好感度 +{change}",
            "🌊 潮汐般的节奏中，{target_name} 如海上扁舟随波荡漾，只能紧紧攀附 {inviter_name}，好感度 +{change}",
            "🎭 这出只有两位观众的戏剧，{inviter_name} 与 {target_name} 共同演绎了最私密的幕间小品，好感度 +{change}",
            "🌄 破晓前的私会，{target_name} 在 {inviter_name} 怀中见证了夜晚最深邃的秘密，好感度 +{change}",
            "🦢 如同天鹅交颈，{inviter_name} 与 {target_name} 在静谧处共享了不为人知的亲密，好感度 +{change}",
            "📜 古老情诗中的场景重现，{inviter_name} 在 {target_name} 身上书写了只有彼此能读的篇章，好感度 +{change}",
            "🎐 风铃轻响的夜晚，{target_name} 发现了 {inviter_name} 温柔表面下隐藏的热情，好感度 +{change}"
        ],
        "failure_msgs": [
            "🌧️ 正当情浓时骤雨突至，{target_name} 匆忙整理衣衫离去，留下 {inviter_name} 独对残局，好感度 -{change}",
            "🕰️ 时光错位，{target_name} 忽然想起重要约定，这场风花雪月只得戛然而止，好感度 -{change}",
            "🍂 秋意突然侵入温暖的室内，{target_name} 感到不适，美好的氛围瞬间消散，好感度 -{change}",
            "🚪 门外不期而至的脚步声让 {target_name} 惊醒，匆忙间整理了凌乱的现场，好感度 -{change}",
            "🎻 原本和谐的旋律突然走音，{target_name} 与 {inviter_name} 发现彼此节奏难以契合，好感度 -{change}",
            "🌫️ 迷雾骤起，{target_name} 忽然看不清眼前人的面容，热情迅速冷却，好感度 -{change}"
        ]
    },
    "卡拉OK": {
        "success_rate": 0.85,
        "favorability_change": (65, 100),
        "min_favorability": 325,
        "success_msgs": [
            "🎤 对唱情歌时{inviter_name}把{target_name}按在墙上假戏真做，麦克风录下喘息声，好感度 +{change}",
            "🍻 交杯酒喝到一半{inviter_name}扯开{target_name}衣领灌进去，酒液顺着胸口流下，好感度 +{change}",
            "💃 disco球下{target_name}热舞磨蹭{inviter_name}胯下，话筒架成了钢管，好感度 +{change}",
            "🎶 唱到“我要吻你”时{inviter_name}真的吻下去，伴奏还在放两人已滚到沙发上，好感度 +{change}",
            "📀 切歌间隙{target_name}蹲下拉开{inviter_name}裤链，黑暗中只有荧幕光映着起伏的头顶，好感度 +{change}",
            "🥃 冰威士忌顺着{target_name}锁骨流下，{inviter_name}趴着舔舐引起阵阵颤抖，好感度 +{change}",
            "🎭 对唱时互相撕扯衣服，唱完时{target_name}胸衣都露在外面，好感度 +{change}",
            "🔇 {inviter_name} 关掉麦克风却关不掉{target_name}的娇喘，隔壁包间开始敲墙，好感度 +{change}",
            "👠 {target_name} 用高跟鞋踩着{inviter_name}大腿唱歌，脚尖轻轻磨蹭敏感部位，好感度 +{change}",
            "🎙️ 话筒被夹在两人身体之间，收音的是激烈心跳和湿吻声，好感度 +{change}"
        ],
        "failure_msgs": [
            "🎤 {inviter_name} 破音堪比杀猪，{target_name} 尴尬到钻茶几底下，好感度 -{change}",
            "🤮 {target_name} 喝多吐在点歌屏上，包间费扣光押金，好感度 -{change}",
            "👮 玩太嗨被报警，警察进来时{inviter_name}正穿着内裤跳舞，好感度 -{change}",
            "💸 结账时发现开了最贵的酒，{target_name} AA制后拉黑联系方式，好感度 -{change}",
            "📱 全程直播忘了关，亲热画面被亲友看光，社会性死亡，好感度 -{change}"
        ]
    }
}
#endregion

# 时区配置
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')
#endregion

#region ==================== ⚠️ 插件核心控件 ⚠️ ====================
@register(
    "astrbot_plugin_WealthAndContract",
    "HINS",
    "集签到、契约、经济与社交系统于一体的群聊插件",
    "1.3.6",
    "https://github.com/WUHINS/astrbot_plugin_WealthAndContract"
)

class ContractSystem(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        # 数据缓存层 - 核心性能优化
        self._cache = {}           # {file_path: data}
        self._dirty = set()        # 需要写入磁盘的文件路径集合
        self._flush_interval = 30  # 每30秒刷新一次脏数据到磁盘
        self._niuniu_cache = None  # 牛牛插件数据缓存
        self._niuniu_cache_time = 0
        # HTTP客户端复用
        self._http_client = None
        # 图片缓存
        self._avatar_cache = {}    # {user_id: (avatar_image, timestamp)}
        self._bg_cache = None      # (bg_image, timestamp)
        self._bg_cache_time = 0
        # 字体缓存
        self._font_cache = {}      # {size: font_object}
        self._init_env()
        self.active_invitations = {}  # 存储活跃的约会邀请
        self.pending_confirmations = {} # 新增：待确认操作存储
        self.date_confirmations = {}   # 新增：约会确认存储
        self.social_invitations = {}  # 存储社交邀请
        self.auth_data = {}  # 存储授权数据 {group_id: {user_id: level}}
        self._load_auth_data() #授权管理员数据
        self.task_token = str(uuid.uuid4()) #token令牌初始化
        self.blacklist_data = self._load_blacklist_data()   #黑名单数据
        self.certificate_applications = {}  # 证件申请存储

        # 初始化股票系统
        self.stocks = {}
        self.stock_user_data = {}
        self._init_stock_system()

        # 启动定期刷新缓存到磁盘的任务
        self._flush_task = asyncio.create_task(self._periodic_flush(self.task_token))

        #region 插件后台任务控件
        self.cleanup_task = asyncio.create_task(self._clean_expired_invitations(self.task_token))
        self.stock_refresh_task = asyncio.create_task(self._refresh_stock_prices(self.task_token))
        #endregion

        #region 插件配置控件
        # 获取背景图API配置
        self.BG_API = self.config.get("BG_API", "https://api.fuchenboke.cn/api/dongman.php")
        
        # 获取彩票配置
        lottery_config = self.config.get("LOTTERY_CONFIG", {})
        self.LOTTERY_WIN_RATE = lottery_config.get("win_rate", 0.02)
        self.LOTTERY_MIN_PRIZE = lottery_config.get("min_prize", 1500)
        self.LOTTERY_MAX_PRIZE = lottery_config.get("max_prize", 50000)
        self.MAX_ASSETS_FOR_LOTTERY = lottery_config.get("max_assets", 500)
        self.MAX_LOTTERY_PER_DAY = lottery_config.get("max_use_per_day", 10)
        self.MAX_CONTRACTORS_FOR_LOTTERY = lottery_config.get("max_contractors", 3)
        
        # 初始化其他变量
        self.active_invitations = {}
        self.pending_confirmations = {}
        self.date_confirmations = {}
        self.social_invitations = {}

        logger.info(f"token令牌初始化为 {self.task_token}")
        #endregion

    #region 插件数据控件
    def _init_env(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(PROP_DATA_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(SOCIAL_DATA_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(TIME_DATA_FILE), exist_ok=True)
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)
        
        # 清空图片目录
        self._clean_image_dir()
        
        # 初始化数据文件（优先JSON，兼容YML迁移）
        for file_path in [DATA_FILE, PROP_DATA_FILE, SOCIAL_DATA_FILE, TIME_DATA_FILE]:
            yml_path = file_path.replace('.json', '.yml')
            self._migrate_yml_to_json(yml_path, file_path)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                    
        if not os.path.exists(FONT_PATH):
            raise FileNotFoundError(f"字体文件缺失: {FONT_PATH}")

    def _clean_image_dir(self):
        """清空图片目录"""
        if os.path.exists(IMAGE_DIR):
            for filename in os.listdir(IMAGE_DIR):
                file_path = os.path.join(IMAGE_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(f"删除图片失败: {file_path} - {str(e)}")

    def _log_operation(self, level: str, message: str):
        """记录操作日志"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        if log_level == logging.INFO:
            logger.info(message)
        elif log_level == logging.WARNING:
            logger.warning(message)
        elif log_level == logging.ERROR:
            logger.error(message)
        else:
            logger.info(message)

    def _get_http_client(self) -> httpx.AsyncClient:
        """获取复用的HTTP客户端"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=15)
        return self._http_client

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """获取缓存字体对象"""
        if size not in self._font_cache:
            if os.path.exists(FONT_PATH):
                self._font_cache[size] = ImageFont.truetype(FONT_PATH, size)
            else:
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def _migrate_yml_to_json(self, yml_path: str, json_path: str):
        """自动迁移YML数据到JSON格式"""
        if os.path.exists(yml_path) and not os.path.exists(json_path):
            try:
                with open(yml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"已迁移 {yml_path} -> {json_path}")
            except Exception as e:
                logger.error(f"迁移数据失败 {yml_path}: {e}")

    def _cached_load(self, file_path: str) -> dict:
        """从缓存加载数据，缓存未命中则从磁盘读取JSON（自动兼容YML）"""
        if file_path in self._cache:
            return self._cache[file_path]
        
        # 自动迁移YML到JSON
        yml_path = file_path.replace('.json', '.yml')
        self._migrate_yml_to_json(yml_path, file_path)
        
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                # JSON读取失败，尝试YML兼容读取
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f) or {}
                except Exception:
                    self._log_operation("error", f"加载数据失败: {file_path} - {e}")
                    data = {}
        
        self._cache[file_path] = data
        return data

    def _cached_save(self, file_path: str, data: dict, immediate: bool = False):
        """保存数据到缓存并标记为脏，可选立即写入磁盘"""
        self._cache[file_path] = data
        self._dirty.add(file_path)
        if immediate:
            self._flush_file(file_path)

    def _flush_file(self, file_path: str):
        """将单个文件刷新到磁盘"""
        if file_path in self._dirty and file_path in self._cache:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._cache[file_path], f, ensure_ascii=False, indent=2)
                self._dirty.discard(file_path)
            except Exception as e:
                self._log_operation("error", f"刷新数据到磁盘失败: {file_path} - {e}")

    async def _periodic_flush(self, token: str):
        """定期将脏数据刷新到磁盘"""
        while True:
            try:
                if token != self.task_token:
                    return
                if self._dirty:
                    dirty_copy = list(self._dirty)
                    for file_path in dirty_copy:
                        self._flush_file(file_path)
                await asyncio.sleep(self._flush_interval)
            except Exception as e:
                self._log_operation("error", f"定期刷新失败: {e}")
                await asyncio.sleep(10)

    def _load_data(self):
        return self._cached_load(DATA_FILE)

    def _save_data(self, data, immediate: bool = False):
        self._cached_save(DATA_FILE, data, immediate=immediate)

    def _load_time_data(self):
        return self._cached_load(TIME_DATA_FILE)

    def _save_time_data(self, data, immediate: bool = False):
        self._cached_save(TIME_DATA_FILE, data, immediate=immediate)

    def _load_prop_data(self):
        return self._cached_load(PROP_DATA_FILE)

    def _save_prop_data(self, data, immediate: bool = False):
        self._cached_save(PROP_DATA_FILE, data, immediate=immediate)

    def _load_social_data(self) -> dict:
        return self._cached_load(SOCIAL_DATA_FILE)

    def _save_social_data(self, data, immediate: bool = False):
        self._cached_save(SOCIAL_DATA_FILE, data, immediate=immediate)
    
    def _get_user_time_data(self, group_id: str, user_id: str) -> dict:
        """获取用户时间数据"""
        time_data = self._load_time_data()
        group_time = time_data.setdefault(group_id, {})
        return group_time.setdefault(user_id, {
            "last_sign": None,
            "last_robbery": None,
            "last_work": None,
            "last_red_star_use": None,
            "last_market_invasion_use": None,
            "free_insurance_until": None,
            "lottery_count": 0  # 新增彩票使用计数
        })

    def _save_user_time_data(self, group_id: str, user_id: str, time_data: dict):
        """保存用户时间数据"""
        all_time_data = self._load_time_data()
        group_time = all_time_data.setdefault(group_id, {})
        group_time[user_id] = time_data
        self._save_time_data(all_time_data)

    def _save_user_data(self, group_id: str, user_id: str, user_data: dict):
        """保存用户数据"""
        try:
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
        except Exception as e:
            self._log_operation("error", f"保存用户数据失败: {str(e)}")

    def _get_user_data(self, group_id: str, user_id: str) -> dict:
        """获取用户主数据（使用缓存，避免重复磁盘读取）"""
        data = self._load_data()
        user_data = data.setdefault(group_id, {}).setdefault(user_id, {
            "coins": 0.0,
            "bank": 0.0,
            "contractors": [],
            "contracted_by": None,
            "consecutive": 0,
            "permanent_contractors": [],
            "is_permanent": False
        })
        
        # 加载牛牛插件数据（带缓存，每60秒刷新一次）
        now = time.time()
        if self._niuniu_cache is None or (now - self._niuniu_cache_time) > 60:
            niuniu_data_path = os.path.join('data', 'niuniu_lengths.yml')
            if os.path.exists(niuniu_data_path):
                try:
                    with open(niuniu_data_path, 'r', encoding='utf-8') as f:
                        self._niuniu_cache = yaml.safe_load(f) or {}
                    self._niuniu_cache_time = now
                except Exception as e:
                    self._log_operation("error", f"加载牛牛数据失败: {str(e)}")
                    self._niuniu_cache = {}
            else:
                self._niuniu_cache = {}
                self._niuniu_cache_time = now
        
        niuniu_coins = self._niuniu_cache.get(group_id, {}).get(user_id, {}).get('coins', 0.0)
        user_data['niuniu_coins'] = niuniu_coins
        
        return user_data

    def _get_user_props(self, group_id: str, user_id: str) -> dict:
        """获取用户道具"""
        prop_data = self._load_prop_data()
        group_props = prop_data.setdefault(group_id, {})
        return group_props.setdefault(user_id, {})

    def _update_user_props(self, group_id: str, user_id: str, props: dict):
        """更新用户道具"""
        prop_data = self._load_prop_data()
        prop_data.setdefault(group_id, {})[user_id] = props
        self._save_prop_data(prop_data)

    def _get_group_social_data(self, group_id: str) -> dict:
        """获取群组的社交数据"""
        data = self._load_social_data()
        return data.setdefault(str(group_id), {})
    
    def _get_user_social_data(self, group_id: str, user_id: str) -> dict:
        """获取用户的社交数据"""
        group_data = self._get_group_social_data(group_id)
        user_id_str = str(user_id)
        
        if user_id_str not in group_data:
            # 新的关系数据结构
            group_data[user_id_str] = {
                "relations": {  # 改为字典存储关系类型和数量
                    "lover": [],
                    "brother": [],
                    "patron": [],
                    "spouse": [],
                    "sworn_brother": [],
                    "long_term_patron": [],
                    "bff": [],
                    "yuri": []
                },
                "favorability": {},
                "daily_date_count": 0,
                "last_date_date": ""
            }
        
        return group_data[user_id_str]
    #endregion

    #region 社交系统核心控件
    RELATION_NAME_TO_TYPE = {
        "恋人": "lover",
        "兄弟": "brother",
        "包养": "patron",
        "夫妻": "spouse",
        "结义兄弟": "sworn_brother",
        "长期包养": "long_term_patron",
        "闺蜜": "bff",
        "百合": "yuri"
    }

    def _get_relation_level(self, favorability: int) -> str:
        """根据好感度获取关系等级"""
        if favorability < 20:
            return "陌生人"
        elif favorability < 50:
            return "熟人"
        elif favorability < 90:
            return "朋友"
        elif favorability < 100:
            return "挚友"
        elif favorability < 500:
            return "唯一的你"
        else:
            return "灵魂伴侣"
    
    def get_favorability(self, group_id: str, user_a_id: str, user_b_id: str) -> int:
        """获取用户A对用户B的好感度"""
        user_a_data = self._get_user_social_data(group_id, user_a_id)
        return user_a_data["favorability"].get(str(user_b_id), 0)
    
    def _update_favorability(self, group_id: str, user_a_id: str, user_b_id: str, change: int) -> int:
        """更新好感度（新增500点限制检查）"""
        user_a_data = self._get_user_social_data(group_id, user_a_id)
        current = user_a_data["favorability"].get(str(user_b_id), 0)
        
        # 检查500点限制
        if current >= 500:
            # 检查是否有特殊关系
            has_relation = any(
                str(user_b_id) in user_a_data["relations"][rel_type]
                for rel_type in user_a_data["relations"]
            )
            
            if not has_relation:
                return current  # 达到500点且无特殊关系，不再增加
        
        new_value = max(0, current + change)
        user_a_data["favorability"][str(user_b_id)] = new_value
        
        # 保存数据
        social_data = self._load_social_data()
        social_data.setdefault(str(group_id), {})[str(user_a_id)] = user_a_data
        self._save_social_data(social_data)
        
        # 记录日志
        self._log_operation("info", 
            f"更新好感度: group={group_id}, from={user_a_id}, to={user_b_id}, "
            f"change={change}, new={new_value}"
        )
        
        return new_value
    
    def get_special_relation(self, group_id: str, user_id: str, target_id: str) -> Optional[str]:
        """获取两个用户之间的特殊关系（使用新数据结构）"""
        user_data = self._get_user_social_data(group_id, user_id)
        for rel_type, targets in user_data["relations"].items():
            if str(target_id) in targets:
                return RELATION_TYPE_NAMES.get(rel_type, rel_type)
        return None

    def add_relation(self, group_id: str, user_id: str, target_id: str, relation_type: str):
        """添加新关系"""
        # 将中文关系类型转换为英文标识
        if relation_type in self.RELATION_NAME_TO_TYPE:
            relation_type = self.RELATION_NAME_TO_TYPE[relation_type]
    
        user_data = self._get_user_social_data(group_id, user_id)
        target_data = self._get_user_social_data(group_id, target_id)
    
        # 添加到发起方
        if str(target_id) not in user_data["relations"][relation_type]:
            user_data["relations"][relation_type].append(str(target_id))
    
        # 添加到目标方
        if str(user_id) not in target_data["relations"][relation_type]:
            target_data["relations"][relation_type].append(str(user_id))
        
        # 保存数据
        social_data = self._load_social_data()
        social_data.setdefault(str(group_id), {})[str(user_id)] = user_data
        social_data[str(group_id)][str(target_id)] = target_data
        self._save_social_data(social_data)
        
        # 记录日志
        self._log_operation("info", 
            f"添加关系: group={group_id}, user={user_id}, "
            f"target={target_id}, relation={relation_type}"
        )
    
    def can_add_relation(self, group_id: str, user_id: str, relation_type: str) -> bool:
        """检查是否可以添加新关系（处理中英文关系类型）"""
        # 如果是中文关系类型，转换为英文标识
        if relation_type in self.RELATION_NAME_TO_TYPE:
            relation_type = self.RELATION_NAME_TO_TYPE[relation_type]
    
        user_data = self._get_user_social_data(group_id, user_id)
        limit = RELATION_LIMITS.get(relation_type, 0)
    
        if limit == -1:  # 无限制
            return True
    
        current_count = len(user_data["relations"].get(relation_type, []))
        return current_count < limit

    def get_upgraded_relation(self, group_id: str, user_id: str, target_id: str) -> Optional[str]:
        """获取升级后的特殊关系"""
        basic_relation = self.get_special_relation(group_id, user_id, target_id)
        if basic_relation in RELATION_UPGRADES:
            return RELATION_UPGRADES[basic_relation]
        return None
    
    def get_relation_bonus(self, group_id: str, user_id: str) -> float:
        """获取关系签到加成"""
        user_data = self._get_user_social_data(group_id, user_id)
        bonus = 0.0
        
        # 基础关系加成
        for rel_type in BASE_RELATION_BONUS:
            if user_data["relations"][rel_type]:
                bonus += BASE_RELATION_BONUS[rel_type]
        
        # 升级关系加成
        for rel_type in UPGRADE_BONUS:
            if user_data["relations"][rel_type]:
                bonus += UPGRADE_BONUS[rel_type]
        
        return bonus

    #endregion

    #region 股票系统控件
    def _init_stock_system(self):
        """初始化股票系统（支持黑天鹅事件）"""
        # 确保目录存在
        os.makedirs(os.path.dirname(STOCK_DATA_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(STOCK_USER_DATA_FILE), exist_ok=True)
        
        # 迁移YML到JSON
        for fp in [STOCK_DATA_FILE, STOCK_USER_DATA_FILE]:
            yml_path = fp.replace('.json', '.yml')
            self._migrate_yml_to_json(yml_path, fp)
        
        # 加载股票数据
        self.stocks = self._load_stock_data()
        
        # 加载用户股票数据
        self.stock_user_data = self._load_user_stock_data()
    
    def _load_user_stock_data(self):
        """加载用户股票数据"""
        if os.path.exists(STOCK_USER_DATA_FILE):
            try:
                with open(STOCK_USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_operation("error", f"加载用户股票数据失败: {str(e)}")
                return {}
        return {}

    def _load_stock_data(self):
        """加载股票数据（支持黑天鹅事件）"""
        stocks = {}
        
        if os.path.exists(STOCK_DATA_FILE):
            try:
                with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    
                    for name, info in saved_data.items():
                        # 恢复基础数据
                        stock_info = {
                            "price": info["price"],
                            "volatility": info["volatility"],
                            "trend": info.get("trend", "random"),
                            "trend_count": info.get("trend_count", 0)
                        }
                        
                        # 恢复黑天鹅事件
                        if "last_black_swan_event" in info:
                            event_data = info["last_black_swan_event"]
                            # 转换时间字符串为datetime对象
                            if "time" in event_data and isinstance(event_data["time"], str):
                                event_data["time"] = datetime.fromisoformat(event_data["time"])
                            stock_info["last_black_swan_event"] = event_data
                        
                        stocks[name] = stock_info
            except Exception as e:
                self._log_operation("error", f"加载股票数据失败: {str(e)}")
                stocks = DEFAULT_STOCKS.copy()
        else:
            stocks = DEFAULT_STOCKS.copy()
        
        # 保存数据确保文件存在
        self._save_stock_data(stocks)
        return stocks
    
    def _save_stock_data(self, data=None):
        """保存股票数据（支持黑天鹅事件）"""
        if data is None:
            data = self.stocks
        
        try:
            save_data = {}
            for name, info in data.items():
                save_info = {
                    "price": info["price"],
                    "volatility": info["volatility"],
                    "trend": info.get("trend", "random"),
                    "trend_count": info.get("trend_count", 0)
                }
                
                # 处理黑天鹅事件
                if "last_black_swan_event" in info:
                    event_data = info["last_black_swan_event"].copy()
                    # 转换时间为ISO格式字符串
                    if "time" in event_data and isinstance(event_data["time"], datetime):
                        event_data["time"] = event_data["time"].isoformat()
                    save_info["last_black_swan_event"] = event_data
                
                save_data[name] = save_info
            
            with open(STOCK_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存股票数据失败: {str(e)}")

    def _save_user_stock_data(self):
        """保存用户股票数据（确保数据完整）"""
        try:
            with open(STOCK_USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stock_user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存用户股票数据失败: {str(e)}")

    def _get_user_stock_data(self, group_id: str, user_id: str) -> dict:
        """获取用户股票数据（按群聊隔离）"""
        group_id_str = str(group_id)
        
        # 确保群组数据存在
        if group_id_str not in self.stock_user_data:
            self.stock_user_data[group_id_str] = {}
        
        # 确保用户数据存在
        if user_id not in self.stock_user_data[group_id_str]:
            self.stock_user_data[group_id_str][user_id] = {}
        
        return self.stock_user_data[group_id_str][user_id]

    def is_trading_time(self):
        """检查当前是否在交易时间内"""
        now = datetime.now()
        return TRADING_HOURS[0] <= now.hour < TRADING_HOURS[1]
    #endregion

    #region 用户身价计算
    def _get_wealth_info(self, user_data: dict) -> Tuple[str, float]:
        """获取用户的财富等级和加成率"""
        total_wealth = user_data["coins"] + user_data["bank"] + user_data.get("niuniu_coins", 0.0)
        
        # 查找匹配的财富等级
        wealth_level = "平民"
        wealth_rate = 0.25
        
        for min_coin, level, rate in WEALTH_LEVELS:
            if total_wealth >= min_coin:
                wealth_level = level
                wealth_rate = rate
            else:
                break
        
        return wealth_level, wealth_rate

    def _calculate_wealth(self, user_data: dict) -> float:
        """计算用户身价（基于财富等级）"""
        wealth_level, _ = self._get_wealth_info(user_data)
        return WEALTH_BASE_VALUES.get(wealth_level, 100)
    #endregion

    #region 授权管理员控件
    def _load_auth_data(self):
        """加载授权数据"""
        yml_path = AUTH_DATA_FILE.replace('.json', '.yml')
        self._migrate_yml_to_json(yml_path, AUTH_DATA_FILE)
        if os.path.exists(AUTH_DATA_FILE):
            try:
                with open(AUTH_DATA_FILE, 'r', encoding='utf-8') as f:
                    self.auth_data = json.load(f)
            except Exception as e:
                self._log_operation("error", f"加载授权数据失败: {str(e)}")
                self.auth_data = {}
        else:
            self.auth_data = {}
    
    def _get_user_auth_level(self, group_id: str, user_id: str) -> int:
        """获取用户授权等级（0表示未授权）"""
        group_id_str = str(group_id)
        user_id_str = str(user_id)
        
        if group_id_str in self.auth_data and user_id_str in self.auth_data[group_id_str]:
            return self.auth_data[group_id_str][user_id_str]
        return 0
    
    def _set_user_auth_level(self, group_id: str, user_id: str, level: int):
        """设置用户授权等级"""
        group_id_str = str(group_id)
        user_id_str = str(user_id)
        
        if group_id_str not in self.auth_data:
            self.auth_data[group_id_str] = {}
        
        self.auth_data[group_id_str][user_id_str] = level
        self._save_auth_data()
    
    def _remove_user_auth(self, group_id: str, user_id: str):
        """移除用户授权（修复保存问题）"""
        group_id_str = str(group_id)
        user_id_str = str(user_id)
    
        if group_id_str in self.auth_data and user_id_str in self.auth_data[group_id_str]:
            del self.auth_data[group_id_str][user_id_str]
        
            # 如果群组下没有授权用户，删除整个群组条目
            if not self.auth_data[group_id_str]:
                del self.auth_data[group_id_str]
        
            # 立即保存数据
            self._save_auth_data()
        else:
            self._log_operation("warning", f"尝试移除不存在的授权: group={group_id_str}, user={user_id_str}")

    def _save_auth_data(self):
        """保存授权数据（添加错误处理）"""
        try:
            with open(AUTH_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.auth_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存授权数据失败: {str(e)}")
            # 尝试创建目录后重试
            try:
                os.makedirs(os.path.dirname(AUTH_DATA_FILE), exist_ok=True)
                with open(AUTH_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.auth_data, f, ensure_ascii=False, indent=2)
            except Exception as e2:
                self._log_operation("critical", f"重试保存授权数据失败: {str(e2)}")
                raise
    #endregion

    #region 黑名单控件
    def is_user_blacklisted(self, group_id: str, user_id: str) -> bool:
        """检查用户是否被拉黑"""
        group_id_str = str(group_id)
        user_id_str = str(user_id)
        
        # 检查群组是否被拉黑
        if group_id_str in self.blacklist_data["groups"]:
            return True
        
        # 检查用户是否被拉黑
        if group_id_str in self.blacklist_data["users"]:
            return user_id_str in self.blacklist_data["users"][group_id_str]
        
        return False
            
    def _load_blacklist_data(self):
        """加载黑名单数据"""
        yml_path = BLACKLIST_DATA_FILE.replace('.json', '.yml')
        self._migrate_yml_to_json(yml_path, BLACKLIST_DATA_FILE)
        if os.path.exists(BLACKLIST_DATA_FILE):
            try:
                with open(BLACKLIST_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_operation("error", f"加载黑名单数据失败: {str(e)}")
                return {"groups": [], "users": {}}
        return {"groups": [], "users": {}}
    
    def _save_blacklist_data(self):
        """保存黑名单数据"""
        try:
            with open(BLACKLIST_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.blacklist_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存黑名单数据失败: {str(e)}")
    #endregion

    #region 资产与证件控件
    def _load_asset_data(self) -> dict:
        """加载资产数据"""
        yml_path = ASSET_DATA_FILE.replace('.json', '.yml')
        self._migrate_yml_to_json(yml_path, ASSET_DATA_FILE)
        if os.path.exists(ASSET_DATA_FILE):
            try:
                with open(ASSET_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_operation("error", f"加载资产数据失败: {str(e)}")
                return {}
        return {}

    def _save_asset_data(self, data: dict):
        """保存资产数据"""
        try:
            with open(ASSET_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存资产数据失败: {str(e)}")

    def _load_certificate_data(self) -> dict:
        """加载证件数据"""
        yml_path = CERTIFICATE_DATA_FILE.replace('.json', '.yml')
        self._migrate_yml_to_json(yml_path, CERTIFICATE_DATA_FILE)
        if os.path.exists(CERTIFICATE_DATA_FILE):
            try:
                with open(CERTIFICATE_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_operation("error", f"加载证件数据失败: {str(e)}")
                return {}
        return {}

    def _save_certificate_data(self, data: dict):
        """保存证件数据"""
        try:
            with open(CERTIFICATE_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log_operation("error", f"保存证件数据失败: {str(e)}")
    #endregion

    async def terminate(self):
        """插件卸载时调用"""
        # 刷新所有脏数据到磁盘
        for file_path in list(self._dirty):
            self._flush_file(file_path)
        self._cache.clear()
        self._dirty.clear()
        
        # 关闭HTTP客户端
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
        
        # 生成新的令牌使旧任务自动退出
        self.task_token = str(uuid.uuid4())
        
        # 取消所有后台任务
        tasks_to_cancel = []
        
        if hasattr(self, 'cleanup_task') and not self.cleanup_task.done():
            tasks_to_cancel.append(self.cleanup_task)
        
        if hasattr(self, 'stock_refresh_task') and not self.stock_refresh_task.done():
            tasks_to_cancel.append(self.stock_refresh_task)
        
        if hasattr(self, '_flush_task') and not self._flush_task.done():
            tasks_to_cancel.append(self._flush_task)
        
        # 取消任务
        for task in tasks_to_cancel:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass  # 任务被取消是预期行为

        # 清理内存中的数据
        self.date_confirmations.clear()
        self.pending_confirmations.clear()
        self.active_invitations.clear()
        self.social_invitations.clear()

        # 调用父类的卸载方法
        await super().unload()
#endregion

#region ==================== 插件功能实现 ====================
    #region 图片渲染
    async def text_to_images(self, text: str, title: str = "帮助信息") -> List[str]:
        """将文本渲染为多张图片（自动分页，异步版）"""
        # 固定画布尺寸
        width = 1080
        height = 1920  # 固定高度，确保背景图完整显示
        line_height = 36
        margin = 50
        max_lines = (height - margin * 2 - 100) // line_height  # 计算最大行数
        
        # 分割文本为多页
        lines = text.split('\n')
        pages = []
        current_page = []
        
        for line in lines:
            # 处理超长行（自动换行）
            while line:
                if len(current_page) < max_lines:
                    # 计算当前行能显示的长度
                    max_chars = min(36, len(line))
                    current_page.append(line[:max_chars])
                    line = line[max_chars:]
                else:
                    pages.append(current_page)
                    current_page = [line[:max_chars]]
                    line = line[max_chars:]
        
        if current_page:
            pages.append(current_page)
        
        image_paths = []
        
        # 为每一页生成图片
        for page_num, page_lines in enumerate(pages, 1):
            # 创建背景
            try:
                # 使用异步HTTP客户端获取背景
                client = self._get_http_client()
                bg_response = await client.get(self.BG_API)
                bg_response.raise_for_status()
                bg = PILImage.open(BytesIO(bg_response.content))
                
                # 调整背景图尺寸，保持宽高比
                bg_ratio = bg.width / bg.height
                target_ratio = width / height
                
                if bg_ratio > target_ratio:
                    # 背景图更宽，以高度为基准缩放
                    new_height = height
                    new_width = int(new_height * bg_ratio)
                else:
                    # 背景图更高，以宽度为基准缩放
                    new_width = width
                    new_height = int(new_width / bg_ratio)
                
                bg = bg.resize((new_width, new_height))
                
                # 裁剪背景图居中部分
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                right = left + width
                bottom = top + height
                bg = bg.crop((left, top, right, bottom))
            except Exception:
                # 使用纯色背景
                bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景
            
            # 创建半透明遮罩提高文字可读性
            overlay = PILImage.new("RGBA", (width, height), (0, 0, 0, 128))
            bg = PILImage.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
            
            draw = ImageDraw.Draw(bg)
            
            # 加载字体
            title_font = self._get_font(42)
            text_font = self._get_font(32)
            footer_font = self._get_font(28)
            
            # 绘制标题
            title_width = title_font.getlength(title)
            draw.text(
                ((width - title_width) // 2, margin),
                title,
                font=title_font,
                fill="#FFFFFF",
                stroke_width=2,
                stroke_fill="#000000"
            )
            
            # 绘制文本内容
            y_position = margin + 100
            for line in page_lines:
                draw.text(
                    (margin, y_position),
                    line,
                    font=text_font,
                    fill="#FFFFFF"
                )
                y_position += line_height
            
            # 绘制页码
            if len(pages) > 1:
                page_text = f"第 {page_num}/{len(pages)} 页"
                page_width = footer_font.getlength(page_text)
                draw.text(
                    (width - page_width - margin, height - margin - 50),
                    page_text,
                    font=footer_font,
                    fill="#FFFFFF"
                )
            
            # 保存图片
            filename = f"help_{int(time.time())}_{page_num}.png"
            save_path = os.path.join(IMAGE_DIR, filename)
            bg.save(save_path)
            image_paths.append(save_path)
        
        return image_paths

    async def _get_avatar(self, user_id: str) -> Optional[PILImage.Image]:
        """异步获取用户头像（带缓存，5分钟TTL）"""
        now = time.time()
        if user_id in self._avatar_cache:
            cached_avatar, cache_time = self._avatar_cache[user_id]
            if now - cache_time < 300:  # 5分钟缓存
                return cached_avatar.copy()
        
        try:
            client = self._get_http_client()
            avatar_url = AVATAR_API.format(user_id)
            response = await client.get(avatar_url)
            response.raise_for_status()
            
            avatar = PILImage.open(BytesIO(response.content))
            avatar = avatar.resize((160, 160))
            
            mask = PILImage.new('L', (160, 160), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 160, 160), fill=255)
            avatar.putalpha(mask)
            
            self._avatar_cache[user_id] = (avatar.copy(), now)
            # 限制缓存大小
            if len(self._avatar_cache) > 100:
                oldest = min(self._avatar_cache.items(), key=lambda x: x[1][1])
                del self._avatar_cache[oldest[0]]
            
            return avatar
        except Exception as e:
            self._log_operation("warning", f"获取头像失败: {user_id} - {str(e)}")
            return None
        
    async def _get_background(self, width: int, height: int) -> PILImage.Image:
        """异步获取背景图片（带缓存，2分钟TTL）"""
        now = time.time()
        if self._bg_cache is not None and (now - self._bg_cache_time) < 120:
            bg = self._bg_cache.copy()
            if bg.size != (width, height):
                bg = bg.resize((width, height), PILImage.Resampling.LANCZOS)
            return bg
        
        try:
            client = self._get_http_client()
            response = await client.get(self.BG_API)
            response.raise_for_status()
            
            bg = PILImage.open(BytesIO(response.content))
            target_ratio = width / height
            bg_ratio = bg.width / bg.height
            
            if bg_ratio > target_ratio:
                new_height = height
                new_width = int(new_height * bg_ratio)
            else:
                new_width = width
                new_height = int(new_width / bg_ratio)
            
            bg = bg.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            bg = bg.crop((left, top, right, bottom))
            
            self._bg_cache = bg.copy()
            self._bg_cache_time = now
            
            return bg
        except Exception:
            return PILImage.new("RGB", (width, height), color="#F0F8FF")

    #endregion

    #region 卡片生成
    async def _generate_card(self, **data) -> str:
        """异步生成签到卡片"""
        try:
            # 异步获取背景
            bg = await self._get_background(1080, 720)
        except Exception:
            bg = PILImage.new("RGB", (1080, 720), color="#FFFFFF")

        def create_rounded_panel(size, color):
            """创建圆角面板"""
            panel = PILImage.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(panel)
            draw.rounded_rectangle([(0, 0), (size[0]-1, size[1]-1)], radius=20, fill=color)
            return panel

        canvas = PILImage.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        draw = ImageDraw.Draw(canvas)
        avatar_y = 200
        info_start_y = 230
        
        # 异步获取头像
        avatar = await self._get_avatar(data["user_id"])
        if avatar:
            canvas.paste(avatar, (60, avatar_y), avatar)

        # 基础信息
        info_font = self._get_font(28)
        name_font = self._get_font(36)
        
        draw.text(
            (260, info_start_y), 
            f"QQ：{data['user_id']}", 
            font=info_font, 
            fill="#000000",
            stroke_width=1,      
            stroke_fill="#FFFFFF"
        )
        
        draw.text(
            (260, info_start_y + 40), 
            data["user_name"], 
            font=name_font, 
            fill="#FFA500",
            stroke_width=1,
            stroke_fill="#000000"
        )
        
        # 身份显示
        if data["is_contracted"]:
            # 获取用户数据检查永久绑定
            is_permanent = False
            try:
                user_data = self._get_user_data(data['group_id'], data['user_id'])
                is_permanent = user_data.get("is_permanent", False)
            except:
                pass
            
            status = "永久性奴" if is_permanent else "性奴"
        else:
            status = "自由民"
            
        wealth_level, _ = self._get_wealth_info({
            "coins": data["coins"], 
            "bank": data["bank"]
        })
        
        draw.text(
            (260, info_start_y + 80),
            f"身份：{status} | 等级：{wealth_level}", 
            font=info_font, 
            fill="#333333",
            stroke_width=1,       
            stroke_fill="#FFFFFF"  
        )

        # 左侧时间面板
        PANEL_WIDTH = 510
        PANEL_HEIGHT = 120
        SIDE_MARGIN = 20
        panel_y = 400

        left_panel = create_rounded_panel((PANEL_WIDTH, PANEL_HEIGHT), (255,255,255,150))
        canvas.paste(left_panel, (SIDE_MARGIN, panel_y), left_panel)
        
        time_font = info_font
        time_title = "查询时间" if data.get('is_query') else "签到时间"
        draw.text((SIDE_MARGIN+20, panel_y+20), time_title, font=time_font, fill="#333333")
        
        current_time = datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d %H:%M:%S")
        draw.text((SIDE_MARGIN+20, panel_y+60), current_time, font=time_font, fill="#333333")

        # 右侧收益面板
        right_panel_x = SIDE_MARGIN + PANEL_WIDTH + 20
        right_panel = create_rounded_panel((PANEL_WIDTH, PANEL_HEIGHT), (255,255,255,150))
        canvas.paste(right_panel, (right_panel_x, panel_y), right_panel)
        
        title_font = self._get_font(24)
        title_text = "预计收入" if data.get('is_query') else "今日收益"
        draw.text((right_panel_x+20, panel_y+20), title_text, font=title_font, fill="#333333")

        detail_font = info_font
        line_height = 24
        
        if data.get('is_query'):
            # 计算加成后的基础收益
            base_with_bonus = BASE_INCOME * (1 + data['user_wealth_rate'])
            contract_bonus = sum(
                self._get_wealth_info(
                    self._get_user_data(data['group_id'], c)
                )[1] * base_with_bonus  # 使用加成后的基础收益计算契约加成
                for c in data['contractors']
            )
            consecutive_bonus = 10 * data['consecutive']  # 显示明日可得的连签奖励
            tomorrow_interest = data["bank"] * 0.01
            
            total = base_with_bonus + contract_bonus + consecutive_bonus + tomorrow_interest + data['relation_bonus']
            lines = [
                f"{total:.1f} 金币",
                f"基础{base_with_bonus:.1f}+契约{contract_bonus:.1f}+连签{consecutive_bonus:.1f}+利息{tomorrow_interest:.1f}+关系{data['relation_bonus']:.1f}"
            ]
            
            # 添加彩票预估收益
            if data.get('lottery_earned', 0) > 0:
                lines.append(f"彩票预估收益: {data['lottery_earned']:.1f}金币")
        else:
            lines = [f"{data['earned']:.1f}（含利息{data['interest']:.1f} + 关系加成{data['relation_bonus']:.1f}）"]
        
        start_y = panel_y + 50
        for i, line in enumerate(lines):
            text_bbox = detail_font.getbbox(line)
            text_width = text_bbox[2] - text_bbox[0]
            
            y_position = start_y + i*line_height
            if i == 0:
                draw.text(
                    (right_panel_x + PANEL_WIDTH//2 - text_width//2, y_position),
                    line,
                    font=self._get_font(24),
                    fill="#FF4500"
                )
            else:
                draw.text(
                    (right_panel_x + PANEL_WIDTH//2 - text_width//2, y_position),
                    line,
                    font=detail_font,
                    fill="#333333"
                )

        # 底部数据面板
        BOTTOM_HEIGHT = 150
        BOTTOM_TOP = 720 - BOTTOM_HEIGHT - 20
        bottom_panel = create_rounded_panel((1040, BOTTOM_HEIGHT), (255,255,255,150))
        canvas.paste(bottom_panel, (20, BOTTOM_TOP), bottom_panel)

        # 获取性奴信息
        contractors_count = len(data['contractors'])
        
        # 如果用户被契约，显示主人信息
        master_info = ""
        if data["is_contracted"]:
            try:
                master_id = data["user_data"]["contracted_by"]
                master_name = await self._get_at_user_name(data['event'], master_id)
                master_info = f"主人: {master_name}"
            except:
                master_info = "主人: 未知"
        else:
            master_info = "自由身"

        # 优化后的指标布局
        metrics = [
            ("现金", f"{data['coins']:.1f}", 60),
            ("银行", f"{data['bank']:.1f}", 300),
            ("性奴", f"{contractors_count}人", 560),
            ("连续签到", str(data['consecutive']), 820)
        ]
        
        # 绘制指标
        for title, value, x in metrics:
            # 标题
            draw.text(
                (x, BOTTOM_TOP+30), 
                title, 
                font=self._get_font(28), 
                fill="#333333"
            )
            
            # 值
            draw.text(
                (x, BOTTOM_TOP+80), 
                value, 
                font=self._get_font(28), 
                fill="#000000"
            )
        
        copyright_font = self._get_font(24)
        copyright_text = "by HINS"
        text_bbox = copyright_font.getbbox(copyright_text)
        draw.text(
            (1080 - text_bbox[2] - 20, 720 - text_bbox[3] - 20),
            copyright_text,
            font=copyright_font,
            fill="#666666"
        )

        # 保存图片
        filename = f"sign_{data['user_id']}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        canvas.save(save_path)
        
        return save_path
    
    async def _generate_contract_card(self, **data) -> str:
        """异步生成契约关系卡片"""
        # 固定尺寸
        width = 1080
        height = 720
        
        # 异步获取背景（优化：等比缩放+居中裁剪避免变形）
        try:
            client = self._get_http_client()
            bg_response = await client.get(self.BG_API)
            bg = PILImage.open(BytesIO(bg_response.content))
            
            # 计算目标比例和原始图片比例
            target_ratio = width / height  # 画布宽高比
            bg_ratio = bg.width / bg.height  # 背景图宽高比
            
            # 根据比例差异决定缩放基准
            if bg_ratio > target_ratio:
                # 背景图更宽，以画布高度为基准缩放，保证高度填满
                new_height = height
                new_width = int(new_height * bg_ratio)
            else:
                # 背景图更高，以画布宽度为基准缩放，保证宽度填满
                new_width = width
                new_height = int(new_width / bg_ratio)
            
            # 高质量等比缩放（使用LANCZOS算法）
            bg = bg.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 计算居中裁剪区域（裁剪掉超出画布的部分）
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            # 裁剪到目标画布尺寸
            bg = bg.crop((left, top, right, bottom))
        except Exception:
            bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景兜底
        
        def create_rounded_panel(size, color, radius=20):
            """创建圆角面板"""
            panel = PILImage.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(panel)
            draw.rounded_rectangle([(0, 0), (size[0]-1, size[1]-1)], radius=radius, fill=color)
            return panel
        
        canvas = PILImage.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 主标题
        self._get_font(title_font)
        title = "契约关系"
        text_bbox = title_font.getbbox(title)
        title_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - title_width) // 2, 30), 
            title, 
            font=title_font, 
            fill="#8B4513",  # 深棕色
            stroke_width=2,
            stroke_fill="#FFFFFF"
        )
        
        # 用户信息
        self._get_font(user_font)
        user_info = f"{data['user_name']} ({data['user_id']})"
        draw.text(
            (100, 100), 
            user_info, 
            font=user_font, 
            fill="#000080"  # 深蓝色
        )
        
        # 显示状态
        self._get_font(status_font)
        if data.get('is_permanent', False):
            status_text = "永久性奴"
            status_color = "#FF0000"  # 红色
        elif data['master_info']:
            status_text = "性奴"
            status_color = "#8B0000"  # 深红色
        else:
            status_text = "自由民"
            status_color = "#228B22"  # 森林绿
            
        draw.text((800, 120), f"状态: {status_text}", font=status_font, fill=status_color)
        
        # 主人信息面板
        master_panel = create_rounded_panel((900, 80), (255, 240, 245, 200))  # 浅粉色
        canvas.paste(master_panel, (90, 160), master_panel)
        
        self._get_font(master_font)
        if data['master_info']:
            master_id, master_name = data['master_info']
            master_text = f"主人: {master_name} ({master_id})"
            draw.text((120, 180), "👑", font=master_font, fill="#FFD700")  # 金色皇冠
            draw.text((160, 180), master_text, font=master_font, fill="#8B0000")  # 深红色
        else:
            draw.text((120, 180), "自由之身，暂无主人", font=master_font, fill="#228B22")  # 森林绿
        
        # 性奴标题
        contractor_title = f"性奴列表 ({len(data['contractors'])}人)"
        draw.text((100, 260), contractor_title, font=user_font, fill="#800080")  # 紫色
        
        # 性奴列表面板
        list_panel = create_rounded_panel((900, 350), (240, 255, 240, 200))  # 浅绿色
        canvas.paste(list_panel, (90, 300), list_panel)
        
        # 显示性奴列表（最多8个）
        self._get_font(list_font)
        y_position = 320
        for i, (cid, cname) in enumerate(data['contractors']):
            if i >= 8:  # 最多显示8个
                break
            
            # 交替行颜色
            bg_color = (220, 240, 255, 150) if i % 2 == 0 else (240, 255, 240, 150)
            item_panel = create_rounded_panel((860, 40), bg_color, radius=10)
            canvas.paste(item_panel, (110, y_position), item_panel)
            
            # 序号和用户信息
            draw.text((130, y_position + 8), f"{i+1}.", font=list_font, fill="#333333")
            draw.text((170, y_position + 8), f"{cname} ({cid})", font=list_font, fill="#00008B")  # 深蓝色
            
            # 检查是否为永久绑定
            is_permanent = False
            try:
                # 加载用户数据检查永久绑定
                user_data = self._get_user_data(data['group_id'], cid)
                is_permanent = user_data.get("is_permanent", False)
            except:
                pass
            
            # 添加永久绑定标记
            if is_permanent:
                draw.text((700, y_position + 8), "💞永久", font=list_font, fill="#FF0000")  # 红色
            
            y_position += 45
        
        # 如果超过8个，显示更多提示
        if len(data['contractors']) > 8:
            more_text = f"...等{len(data['contractors'])-8}位未显示"
            draw.text((130, y_position + 10), more_text, font=list_font, fill="#666666")
        
        # 底部信息
        self._get_font(footer_font)
        draw.text((100, 670), "购买性奴: 购买@用户", font=footer_font, fill="#666666")  # 橄榄绿
        draw.text((400, 670), "出售性奴: 出售@用户", font=footer_font, fill="#666666")
        draw.text((700, 670), "解除契约: /赎身", font=footer_font, fill="#666666")
        
        # 版权信息
        self._get_font(copyright_font)
        copyright_text = "by HINS"
        text_bbox = copyright_font.getbbox(copyright_text)
        draw.text(
            (width - text_bbox[2] - 20, height - text_bbox[3] - 10),
            copyright_text,
            font=copyright_font,
            fill="#666666"
        )
    
        # 保存图片
        filename = f"contract_{data['user_id']}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        canvas.save(save_path)
        
        return save_path    
    
    async def _generate_asset_card(self, **data) -> str:
        """异步生成资产核查卡片"""
        # 固定画布尺寸
        width = 1080
        height = 720
        
        # 异步获取背景
        try:
            client = self._get_http_client()
            bg_response = await client.get(self.BG_API)
            bg = PILImage.open(BytesIO(bg_response.content))
            
            # 计算目标比例和原始比例
            target_ratio = width / height
            bg_ratio = bg.width / bg.height
            
            # 根据比例差异决定缩放方式
            if bg_ratio > target_ratio:
                # 背景图更宽，以高度为基准缩放
                new_height = height
                new_width = int(new_height * bg_ratio)
            else:
                # 背景图更高，以宽度为基准缩放
                new_width = width
                new_height = int(new_width / bg_ratio)
            
            # 调整背景图尺寸
            bg = bg.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 计算裁剪区域（确保居中）
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            # 裁剪到目标尺寸
            bg = bg.crop((left, top, right, bottom))
        except Exception:
            bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景

        
        # 定义内部函数：创建圆角面板
        def create_rounded_panel(size, color, radius=20):
            """创建圆角面板"""
            panel = PILImage.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(panel)
            draw.rounded_rectangle([(0, 0), (size[0]-1, size[1]-1)], radius=radius, fill=color)
            return panel
        
        canvas = PILImage.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 主标题
        self._get_font(title_font)
        title = f"{data['user_name']}的资产核查"
        text_bbox = title_font.getbbox(title)
        title_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - title_width) // 2, 30), 
            title, 
            font=title_font, 
            fill="#4169E1",  # 皇家蓝
            stroke_width=2,
            stroke_fill="#FFFFFF"
        )
        
        # 用户信息
        self._get_font(user_font)
        user_info = f"QQ: {data['user_id']}"
        draw.text((100, 100), user_info, font=user_font, fill="#000080")  # 深蓝色
        
        # 财富等级信息
        self._get_font(wealth_font)
        wealth_text = f"财富等级: {data['wealth_level']} (加成率: {data['wealth_rate']*100:.0f}%)"
        draw.text((100, 150), wealth_text, font=wealth_font, fill="#8B4513")  # 深棕色
        
        # 资产面板
        asset_panel = create_rounded_panel((900, 450), (255, 255, 255, 200))  # 半透明白色
        canvas.paste(asset_panel, (90, 200), asset_panel)
        
        # 资产标题
        self._get_font(title_font)
        draw.text((120, 220), "资产类型", font=title_font, fill="#8B0000")  # 深红色
        draw.text((550, 220), "金额", font=title_font, fill="#8B0000")
        
        # 绘制分隔线
        draw.line([(100, 260), (980, 260)], fill="#8B0000", width=2)
        
        # 资产项目
        asset_items = [
            ("💰 钱包现金", data["coins"]),
            ("🏦 银行存款", data["bank"]),
            ("🐮 牛牛金币", data["niuniu_coins"]),
            ("💎 总资产", data["total_assets"])
        ]
        
        # 显示资产项目
        self._get_font(entry_font)
        y_position = 290
        for i, (name, amount) in enumerate(asset_items):
            # 交替行颜色
            bg_color = (220, 240, 255, 150) if i % 2 == 0 else (240, 255, 240, 150)
            item_panel = create_rounded_panel((860, 60), bg_color, radius=10)
            canvas.paste(item_panel, (110, y_position), item_panel)
            
            # 资产名称
            draw.text((130, y_position + 15), name, font=entry_font, fill="#00008B")  # 深蓝色
            
            # 资产金额（总资产特殊显示）
            if name == "💎 总资产":
                amount_color = "#FF4500"  # 橙红色
                self._get_font(amount_font)
            else:
                amount_color = "#228B22"  # 森林绿
                amount_font = entry_font
            
            amount_text = f"{amount:.1f} 金币"
            text_width = amount_font.getlength(amount_text)
            draw.text(
                (860 - text_width + 110 - 20, y_position + 15), 
                amount_text, 
                font=amount_font, 
                fill=amount_color
            )
            
            y_position += 70
        
        # 财富等级描述
        level_desc = ""
        for min_coin, name, rate in WEALTH_LEVELS:
            if data["total_assets"] >= min_coin:
                level_desc = f"达到{name}等级需要资产 ≥ {min_coin}金币"
        
        draw.text(
            (120, y_position + 20), 
            level_desc, 
            font=entry_font, 
            fill="#8B4513"  # 深棕色
        )
        
        # 底部信息
        self._get_font(footer_font)
        draw.text((100, 670), "查询个人资产: /签到查询", font=footer_font, fill="#666666")
        draw.text((400, 670), "金币排行榜: /金币排行榜", font=footer_font, fill="#666666")
        draw.text((700, 670), "性奴排行榜: /性奴排行榜", font=footer_font, fill="#666666")
        
        # 版权信息
        self._get_font(copyright_font)
        copyright_text = "by HINS"
        text_bbox = copyright_font.getbbox(copyright_text)
        draw.text(
            (1080 - text_bbox[2] - 20, 720 - text_bbox[3] - 10),
            copyright_text,
            font=copyright_font,
            fill="#666666"
        )

        # 保存图片
        filename = f"asset_check_{data['user_id']}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        canvas.save(save_path)
        
        return save_path
    
    async def _generate_contractor_leaderboard(self, **data) -> str:
        """异步生成性奴排行榜卡片"""
        # 固定画布尺寸
        width = 1080
        height = 720
        
        # 异步获取背景
        try:
            client = self._get_http_client()
            bg_response = await client.get(self.BG_API)
            bg = PILImage.open(BytesIO(bg_response.content))
            
            # 计算目标比例和原始比例
            target_ratio = width / height
            bg_ratio = bg.width / bg.height
            
            # 根据比例差异决定缩放方式
            if bg_ratio > target_ratio:
                # 背景图更宽，以高度为基准缩放
                new_height = height
                new_width = int(new_height * bg_ratio)
            else:
                # 背景图更高，以宽度为基准缩放
                new_width = width
                new_height = int(new_width / bg_ratio)
            
            # 调整背景图尺寸
            bg = bg.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 计算裁剪区域（确保居中）
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            # 裁剪到目标尺寸
            bg = bg.crop((left, top, right, bottom))
        except Exception:
            bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景

        # 定义内部函数：创建圆角面板
        def create_rounded_panel(size, color, radius=20):
            """创建圆角面板"""
            panel = PILImage.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(panel)
            draw.rounded_rectangle([(0, 0), (size[0]-1, size[1]-1)], radius=radius, fill=color)
            return panel
        
        canvas = PILImage.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 主标题
        self._get_font(title_font)
        title = "性奴排行榜"
        text_bbox = title_font.getbbox(title)
        title_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - title_width) // 2, 30), 
            title, 
            font=title_font, 
            fill="#FF69B4",  # 粉红色
            stroke_width=2,
            stroke_fill="#000000"
        )
        
        # 副标题
        self._get_font(subtitle_font)
        subtitle = "拥有性奴数量"
        text_bbox = subtitle_font.getbbox(subtitle)
        subtitle_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - subtitle_width) // 2, 90), 
            subtitle, 
            font=subtitle_font, 
            fill="#FFFFFF",
            stroke_width=1,
            stroke_fill="#000000"
        )
        
        # 排行榜面板
        list_panel = create_rounded_panel((900, 500), (255, 255, 255, 180))  # 半透明白色
        canvas.paste(list_panel, (90, 150), list_panel)
        
        # 表头
        self._get_font(header_font)
        headers = [("排名", 120), ("用户", 220), ("性奴数量", 700)]
        for text, x in headers:
            draw.text((x, 170), text, font=header_font, fill="#8B0000")  # 深红色
        
        # 绘制分隔线
        draw.line([(100, 200), (980, 200)], fill="#8B0000", width=2)
        
        # 显示排行榜条目
        self._get_font(entry_font)
        y_position = 220
        
        # 排名颜色配置
        rank_colors = {
            1: ("#FFD700", "#FF4500"),    # 金色, 橙红色
            2: ("#C0C0C0", "#FF6347"),    # 银色, 番茄红
            3: ("#CD7F32", "#FF8C00")     # 古铜色, 深橙色
        }
        
        for rank, user_name, count in data['leaderboard']:
            # 获取排名颜色
            rank_color, count_color = rank_colors.get(rank, ("#000000", "#228B22"))
            
            # 创建条目背景面板（交替颜色）
            bg_color = (255, 192, 203, 100) if rank % 2 == 0 else (255, 218, 224, 100)  # 粉色系交替
            item_panel = create_rounded_panel((860, 45), bg_color, radius=10)
            canvas.paste(item_panel, (110, y_position), item_panel)
            
            # 绘制条目
            draw.text((120, y_position + 10), str(rank), font=entry_font, fill=rank_color)
            draw.text((220, y_position + 10), user_name, font=entry_font, fill="#00008B")  # 深蓝色
            
            # 性奴数量（前三名特殊显示）
            if rank <= 3:
                self._get_font(count_font)
            else:
                count_font = entry_font
            
            count_text = f"{count} 人"
            text_width = count_font.getlength(count_text)
            draw.text(
                (860 - text_width + 110 - 20, y_position + 10), 
                count_text, 
                font=count_font, 
                fill=count_color
            )
            
            y_position += 45
        
        # 底部信息
        self._get_font(footer_font)
        draw.text((100, 670), "管理契约: /我的契约", font=footer_font, fill="#666666")
        
        # 版权信息
        self._get_font(copyright_font)
        copyright_text = "by HINS"
        text_bbox = copyright_font.getbbox(copyright_text)
        draw.text(
            (width - text_bbox[2] - 20, height - text_bbox[3] - 10),
            copyright_text,
            font=copyright_font,
            fill="#666666"
        )

        # 保存图片
        filename = f"contractor_leaderboard_{data['group_id']}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        canvas.save(save_path)
        
        return save_path

    async def _generate_wealth_leaderboard(self, **data) -> str:
        """异步生成金币排行榜卡片"""
        # 固定画布尺寸
        width = 1080
        height = 720
        
        # 异步获取背景
        try:
            client = self._get_http_client()
            bg_response = await client.get(self.BG_API)
            bg = PILImage.open(BytesIO(bg_response.content))
            
            # 计算目标比例和原始比例
            target_ratio = width / height
            bg_ratio = bg.width / bg.height
            
            # 根据比例差异决定缩放方式
            if bg_ratio > target_ratio:
                # 背景图更宽，以高度为基准缩放
                new_height = height
                new_width = int(new_height * bg_ratio)
            else:
                # 背景图更高，以宽度为基准缩放
                new_width = width
                new_height = int(new_width / bg_ratio)
            
            # 调整背景图尺寸
            bg = bg.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 计算裁剪区域（确保居中）
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            # 裁剪到目标尺寸
            bg = bg.crop((left, top, right, bottom))
        except Exception:
            bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景

        # 定义内部函数：创建圆角面板
        def create_rounded_panel(size, color, radius=20):
            """创建圆角面板"""
            panel = PILImage.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(panel)
            draw.rounded_rectangle([(0, 0), (size[0]-1, size[1]-1)], radius=radius, fill=color)
            return panel
        
        canvas = PILImage.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 主标题
        self._get_font(title_font)
        title = "金币排行榜"
        text_bbox = title_font.getbbox(title)
        title_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - title_width) // 2, 30), 
            title, 
            font=title_font, 
            fill="#FFD700",  # 金色
            stroke_width=2,
            stroke_fill="#000000"
        )
        
        # 副标题
        self._get_font(subtitle_font)
        subtitle = "总资产（现金+银行+牛牛金币）"
        text_bbox = subtitle_font.getbbox(subtitle)
        subtitle_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - subtitle_width) // 2, 90), 
            subtitle, 
            font=subtitle_font, 
            fill="#FFFFFF",
            stroke_width=1,
            stroke_fill="#000000"
        )
        
        # 排行榜面板
        list_panel = create_rounded_panel((900, 500), (255, 255, 255, 180))  # 半透明白色
        canvas.paste(list_panel, (90, 150), list_panel)
        
        # 表头
        self._get_font(header_font)
        headers = [("排名", 120), ("用户", 220), ("总资产", 700)]
        for text, x in headers:
            draw.text((x, 170), text, font=header_font, fill="#8B0000")  # 深红色
        
        # 绘制分隔线
        draw.line([(100, 200), (980, 200)], fill="#8B0000", width=2)
        
        # 显示排行榜条目
        self._get_font(entry_font)
        y_position = 220
        
        # 排名颜色配置
        rank_colors = {
            1: ("#FFD700", "#FF4500"),    # 金色, 橙红色
            2: ("#C0C0C0", "#FF6347"),    # 银色, 番茄红
            3: ("#CD7F32", "#FF8C00")     # 古铜色, 深橙色
        }
        
        for rank, user_name, wealth in data['leaderboard']:
            # 获取排名颜色
            rank_color, wealth_color = rank_colors.get(rank, ("#000000", "#228B22"))
            
            # 创建条目背景面板（交替颜色）
            bg_color = (220, 240, 255, 100) if rank % 2 == 0 else (240, 255, 240, 100)
            item_panel = create_rounded_panel((860, 45), bg_color, radius=10)
            canvas.paste(item_panel, (110, y_position), item_panel)
            
            # 绘制条目
            draw.text((120, y_position + 10), str(rank), font=entry_font, fill=rank_color)
            draw.text((220, y_position + 10), user_name, font=entry_font, fill="#00008B")  # 深蓝色
            
            # 财富金额（前三名特殊显示）
            if rank <= 3:
                self._get_font(wealth_font)
            else:
                wealth_font = entry_font
            
            wealth_text = f"{wealth:.1f} 金币"
            text_width = wealth_font.getlength(wealth_text)
            draw.text(
                (860 - text_width + 110 - 20, y_position + 10), 
                wealth_text, 
                font=wealth_font, 
                fill=wealth_color
            )
            
            y_position += 45
        
        # 底部信息
        self._get_font(footer_font)
        draw.text((100, 670), "查看个人资产: /签到查询", font=footer_font, fill="#666666")
        
        # 版权信息
        self._get_font(copyright_font)
        copyright_text = "by HINS"
        text_bbox = copyright_font.getbbox(copyright_text)
        draw.text(
            (width - text_bbox[2] - 20, height - text_bbox[3] - 10),
            copyright_text,
            font=copyright_font,
            fill="#666666"
        )

        # 保存图片
        filename = f"wealth_leaderboard_{data['group_id']}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        canvas.save(save_path)
        
        return save_path

    async def _generate_marriage_certificate(self, event, user_id1: str, user_name1: str, user_id2: str, user_name2: str, cert_id: str, cert_type: str) -> str:
        """生成美观版结婚证/离婚证卡片"""
        # 固定尺寸
        width = 800
        height = 600
        
        # 创建背景
        try:
            # 获取背景图
            bg = await self._get_background(width, height)
        except Exception:
            # 使用纯色背景
            bg = PILImage.new("RGB", (width, height), color="#F0F8FF")  # 浅蓝色背景
        
        # 创建半透明遮罩
        overlay = PILImage.new("RGBA", (width, height), (255, 255, 255, 180))  # 白色半透明
        bg = PILImage.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
        
        draw = ImageDraw.Draw(bg)
        
        # 加载字体
        try:
            self._get_font(title_font)
            self._get_font(name_font)
            self._get_font(info_font)
            self._get_font(small_font)
        except:
            # 使用默认字体
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # 绘制标题
        title = cert_type
        text_bbox = title_font.getbbox(title)
        title_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - title_width) // 2, 30), 
            title, 
            font=title_font, 
            fill="#8B0000" if cert_type == "结婚证" else "#00008B",  # 深红/深蓝
            stroke_width=1,
            stroke_fill="#FFFFFF"
        )
        
        # 绘制副标题
        subtitle = "银河月老集团署"
        text_bbox = name_font.getbbox(subtitle)
        subtitle_width = text_bbox[2] - text_bbox[0]
        draw.text(
            ((width - subtitle_width) // 2, 85), 
            subtitle, 
            font=name_font, 
            fill="#8B0000" if cert_type == "结婚证" else "#00008B"
        )
        
        # 创建左右两个大框（半透明圆角）
        box_width = (width - 100) // 2 - 10
        box_height = 300
        box_y = 130
        
        # 创建圆角矩形函数
        def rounded_rectangle(draw, box, radius, fill=None, outline=None, width=1):
            """绘制圆角矩形"""
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=outline, width=width)
            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=outline, width=width)
            draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill, outline=outline)
            draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill, outline=outline)
            draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill, outline=outline)
            draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill, outline=outline)
        
        # 左侧框 - 用户1
        box1 = (50, box_y, 50 + box_width, box_y + box_height)
        rounded_rectangle(draw, box1, 20, fill=(255, 255, 255, 180), outline="#8B0000" if cert_type == "结婚证" else "#00008B", width=2)
        
        # 右侧框 - 用户2
        box2 = (width - 50 - box_width, box_y, width - 50, box_y + box_height)
        rounded_rectangle(draw, box2, 20, fill=(255, 255, 255, 180), outline="#8B0000" if cert_type == "结婚证" else "#00008B", width=2)
        
        # 获取双方头像
        avatar1 = await self._get_avatar(user_id1)
        avatar2 = await self._get_avatar(user_id2)
        
        # 头像尺寸
        avatar_size = 120
        
        # 绘制左侧头像和名字
        if avatar1:
            # 创建圆形头像
            avatar1 = avatar1.resize((avatar_size, avatar_size))
            mask = PILImage.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # 粘贴头像
            bg.paste(avatar1, (50 + (box_width - avatar_size) // 2, box_y + 30), mask)
        
        # 绘制左侧名字
        name1_bbox = name_font.getbbox(user_name1)
        name1_width = name1_bbox[2] - name1_bbox[0]
        draw.text(
            (50 + (box_width - name1_width) // 2, box_y + 170), 
            user_name1, 
            font=name_font, 
            fill="#000000"
        )
        
        # 绘制右侧头像和名字
        if avatar2:
            # 创建圆形头像
            avatar2 = avatar2.resize((avatar_size, avatar_size))
            mask = PILImage.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # 粘贴头像
            bg.paste(avatar2, (width - 50 - box_width + (box_width - avatar_size) // 2, box_y + 30), mask)
        
        # 绘制右侧名字
        name2_bbox = name_font.getbbox(user_name2)
        name2_width = name2_bbox[2] - name2_bbox[0]
        draw.text(
            (width - 50 - box_width + (box_width - name2_width) // 2, box_y + 170), 
            user_name2, 
            font=name_font, 
            fill="#000000"
        )
        
        # 绘制中间连接符
        if cert_type == "结婚证":
            symbol = "❤"
            symbol_color = "#FF0000"
        else:
            symbol = "✖"
            symbol_color = "#000000"
        
        symbol_bbox = title_font.getbbox(symbol)
        symbol_width = symbol_bbox[2] - symbol_bbox[0]
        draw.text(
            ((width - symbol_width) // 2, box_y + box_height // 2 - 15), 
            symbol, 
            font=title_font, 
            fill=symbol_color
        )
        
        # 底部信息条
        info_bar_y = box_y + box_height + 30
        info_bar_height = 60
        
        # 创建圆角信息条
        info_box = (50, info_bar_y, width - 50, info_bar_y + info_bar_height)
        rounded_rectangle(draw, info_box, 10, fill=(255, 255, 255, 200), outline="#8B0000" if cert_type == "结婚证" else "#00008B", width=1)
        
        # 证件信息
        issue_date = datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")
        info_text = f"证件ID: {cert_id} | 发证日期: {issue_date}"
        
        # 绘制证件信息
        info_bbox = info_font.getbbox(info_text)
        info_width = info_bbox[2] - info_bbox[0]
        draw.text(
            ((width - info_width) // 2, info_bar_y + (info_bar_height - info_bbox[3]) // 2), 
            info_text, 
            font=info_font, 
            fill="#000000"
        )
        
        # 底部状态信息
        status_y = info_bar_y + info_bar_height + 15
        status_text = "有效" if cert_type == "结婚证" else "失效"
        status_bbox = info_font.getbbox(status_text)
        status_width = status_bbox[2] - status_bbox[0]
        draw.text(
            ((width - status_width) // 2, status_y), 
            status_text, 
            font=info_font, 
            fill="#8B0000" if cert_type == "结婚证" else "#00008B"
        )
        
        # 版权信息
        copyright_text = "by HINS"
        copyright_bbox = small_font.getbbox(copyright_text)
        draw.text(
            (width - copyright_bbox[2] - 20, height - 30), 
            copyright_text, 
            font=small_font, 
            fill="#666666"
        )
        
        # 保存图片
        filename = f"{cert_type}_{cert_id}.png"
        save_path = os.path.join(IMAGE_DIR, filename)
        bg.save(save_path)
        
        return save_path

    #endregion

    #region 清理任务扩展
    async def _clean_expired_invitations(self, token: str):
        """定期清理过期的约会、社交邀请和证件申请"""
        while True:
            try:
                # 检查任务令牌
                if token != self.task_token:
                    self._log_operation("info", f"清理任务检测到令牌 {token} 失效，自动退出")
                    return

                current_time = datetime.now(SHANGHAI_TZ)
                
                # 清理过期约会邀请
                for group_id_str in list(self.date_confirmations.keys()):
                    group_invites = self.date_confirmations[group_id_str]
                    
                    # 确保是字典类型
                    if not isinstance(group_invites, dict):
                        del self.date_confirmations[group_id_str]
                        continue
                        
                    for target_id in list(group_invites.keys()):
                        invite = group_invites[target_id]
                        
                        # 确保是字典且包含创建时间
                        if not isinstance(invite, dict) or 'created_at' not in invite:
                            del group_invites[target_id]
                            continue
                            
                        # 检查是否过期（约会邀请有效期5分钟）
                        if current_time - invite['created_at'] > timedelta(minutes=5):
                            del group_invites[target_id]
                    
                    # 清理空群组
                    if not group_invites:
                        del self.date_confirmations[group_id_str]
                
                # 清理过期社交邀请
                for group_id_str in list(self.social_invitations.keys()):
                    group_invites = self.social_invitations[group_id_str]
                    
                    # 确保是字典类型
                    if not isinstance(group_invites, dict):
                        del self.social_invitations[group_id_str]
                        continue
                        
                    for target_id in list(group_invites.keys()):
                        invite = group_invites[target_id]
                        
                        # 确保是字典且包含创建时间
                        if not isinstance(invite, dict) or 'created_at' not in invite:
                            del group_invites[target_id]
                            continue
                            
                        # 检查是否过期（社交邀请有效期10分钟）
                        if current_time - invite['created_at'] > timedelta(minutes=10):
                            del group_invites[target_id]
                    
                    # 清理空群组
                    if not group_invites:
                        del self.social_invitations[group_id_str]
                
                # 清理过期证件申请
                for group_id_str in list(self.certificate_applications.keys()):
                    group_applications = self.certificate_applications[group_id_str]
                    
                    # 确保是字典类型
                    if not isinstance(group_applications, dict):
                        del self.certificate_applications[group_id_str]
                        continue
                        
                    for target_id in list(group_applications.keys()):
                        application = group_applications[target_id]
                        
                        # 确保是字典且包含创建时间
                        if not isinstance(application, dict) or 'created_at' not in application:
                            del group_applications[target_id]
                            continue
                            
                        # 检查是否过期（证件申请有效期10分钟）
                        if current_time - application['created_at'] > timedelta(minutes=10):
                            del group_applications[target_id]
                    
                    # 清理空群组
                    if not group_applications:
                        del self.certificate_applications[group_id_str]
                
                # 记录清理结果
                self._log_operation("debug", 
                    f"清理过期邀请完成: "
                    f"约会邀请: {len(self.date_confirmations)}组, "
                    f"社交邀请: {len(self.social_invitations)}组, "
                    f"证件申请: {len(self.certificate_applications)}组"
                )
                
                # 每5分钟清理一次
                await asyncio.sleep(300)
            except Exception as e:
                self._log_operation("error", f"清理过期邀请失败: {str(e)}")
                # 出错时重置数据结构
                self.date_confirmations = {}
                self.social_invitations = {}
                self.certificate_applications = {}
                await asyncio.sleep(60)
    #endregion    

    #region 定期刷新股票价格
    async def _refresh_stock_prices(self, token: str):
        """优化股票价格刷新"""
        while True:
            try:
                # 令牌检查
                if token != self.task_token:
                    self._log_operation("info", f"股票刷新任务检测到令牌 {token} 失效，自动退出")
                    return
                
                # 检查交易时间
                if self.is_trading_time():
                    # 更新所有股票价格
                    for stock_name, stock_info in self.stocks.items():
                        # 0.1%概率触发黑天鹅事件
                        if random.random() < 0.001:
                            # 50%概率暴涨，50%概率暴跌
                            if random.random() < 0.5:
                                # 暴涨500%-1000%
                                multiplier = random.uniform(5.0, 10.0)
                                new_price = stock_info["price"] * multiplier
                                event_type = "暴涨"
                            else:
                                # 暴跌500%-1000%（价格变为1/5到1/10）
                                multiplier = random.uniform(0.1, 0.2)
                                new_price = stock_info["price"] * multiplier
                                event_type = "暴跌"
                            
                            # 更新价格
                            stock_info["price"] = max(5.00, round(new_price, 2))
                            
                            stock_info["last_black_swan_event"] = {
                                "type": event_type,
                                "multiplier": multiplier,
                                "time": datetime.now()
                            }

                            # 记录日志
                            self._log_operation("warning", 
                                f"黑天鹅事件: {stock_name} {event_type} {multiplier:.1f}倍!"
                            )
                            
                            # 跳过正常波动计算
                            continue
                        
                        # 50%概率更新波动率
                        if random.random() < 0.5:
                            # 在原有波动率基础上随机变化（±0.05）
                            current_volatility = stock_info["volatility"]
                            new_volatility = current_volatility + random.uniform(-0.05, 0.05)
                            
                            # 确保波动率在合理范围内
                            new_volatility = max(0.01, min(0.5, new_volatility))
                            stock_info["volatility"] = round(new_volatility, 4)
                            
                            # 记录日志
                            self._log_operation("debug", 
                                f"更新波动率: {stock_name} {current_volatility:.4f} -> {new_volatility:.4f}"
                            )
                        
                        volatility = stock_info["volatility"]
                        current_price = stock_info["price"]
                        
                        # 检查当前趋势
                        trend = stock_info.get("trend", "random")
                        trend_count = stock_info.get("trend_count", 0)
                        max_trend_duration = random.randint(3, 12)  # 趋势持续3-12次刷新
                    
                        # 决定本次波动
                        if trend_count < max_trend_duration:
                            # 延续当前趋势
                            stock_info["trend_count"] = trend_count + 1
                        else:
                            # 随机新趋势
                            trend_options = ["up", "down", "flat", "random"]
                            weights = [0.35, 0.35, 0.15, 0.15]  # 上涨/下跌概率更高
                            trend = random.choices(trend_options, weights=weights)[0]
                            stock_info["trend"] = trend
                            stock_info["trend_count"] = 1
                    
                        # 根据趋势计算波动
                        if trend == "up":
                            # 上涨趋势：0% 到 +波动率*1.5
                            change_percent = random.uniform(0, volatility * 1.5)
                        elif trend == "down":
                            # 下跌趋势：-波动率*1.5 到 0%
                            change_percent = random.uniform(-volatility * 1.5, 0)
                        elif trend == "flat":
                            # 持平趋势：-波动率*0.2 到 +波动率*0.2
                            change_percent = random.uniform(-volatility * 0.2, volatility * 0.2)
                        else:
                            # 随机波动：-波动率 到 +波动率
                            change_percent = random.uniform(-volatility, volatility)
                    
                        # 计算新价格
                        new_price = current_price * (1 + change_percent)
                    
                        # 防止价格过低
                        stock_info["price"] = max(5.00, round(new_price, 2))
                
                    # 保存更新后的数据
                    self._save_stock_data()
                
                    # 记录日志
                    self._log_operation("info", "股票价格已刷新（含波动率随机变化和趋势模拟）")
                else:
                    # 记录日志
                    self._log_operation("info", "当前非交易时间，跳过股票刷新")
                
                # 每3分钟刷新一次
                await asyncio.sleep(STOCK_REFRESH_INTERVAL)
            except Exception as e:
                self._log_operation("error", f"刷新股票价格失败: {str(e)}")
                await asyncio.sleep(60)  # 出错后等待1分钟
        #endregion

    #region 定期公司数据组件
    async def _trigger_company_events(self, token: str):
        """每天触发公司事件（早8点到晚8点）"""
        while token == self.task_token:
            now = datetime.now(SHANGHAI_TZ)
            # 检查是否在事件触发时间段（8:00-20:00）
            if 8 <= now.hour < 20:
                for company_id, company in self.company_data.items():
                    # 30%概率触发事件
                    if random.random() < COMPANY_CONFIG["event_probability"]:
                        # 随机选择事件类型（正面或负面）
                        event_type = "positive" if random.random() < 0.6 else "negative"
                        event = random.choice(COMPANY_EVENTS[event_type])
                        
                        # 计算影响幅度
                        impact_range = event["impact"]
                        impact_percent = random.uniform(impact_range[0], impact_range[1])
                        
                        # 更新公司市值
                        current_value = company["market_value"]
                        new_value = current_value * (1 + impact_percent)
                        company["market_value"] = max(1000000, new_value)  # 最低100万市值
                        
                        # 记录事件
                        event_record = {
                            "time": now.isoformat(),
                            "name": event["name"],
                            "description": event["description"].format(impact=impact_percent*100),
                            "impact_percent": impact_percent,
                            "old_value": current_value,
                            "new_value": company["market_value"]
                        }
                        company["events"].append(event_record)
                        
                        # 检查是否解散公司
                        if company["market_value"] < company["register_capital"] * COMPANY_CONFIG["dissolve_threshold"]:
                            # 解散公司
                            self._dissolve_company(company_id)
                            self._log_operation("info", f"公司解散: {company_id} 因市值低于阈值")
                        else:
                            self._log_operation("info", f"公司事件: {company_id} - {event['name']}, 市值变化: {impact_percent*100:.2f}%")
                
                # 保存数据
                self._save_company_data()
            
            # 每小时检查一次
            await asyncio.sleep(3600)
    
    async def _pay_company_salaries(self, token: str):
        """每天发放公司工资（晚8点）"""
        while token == self.task_token:
            now = datetime.now(SHANGHAI_TZ)
            # 检查是否是晚上8点
            if now.hour == 20 and now.minute < 10:  # 10分钟窗口期
                for company_id, company in self.company_data.items():
                    total_salary = 0
                    # 计算公司总工资
                    for group_id, employees in company["employees"].items():
                        for employee_id, employee_info in employees.items():
                            # 获取职位工资乘数
                            position = employee_info.get("position", "普通员工")
                            multiplier = COMPANY_CONFIG["position_salary_multipliers"].get(position, 1.0)
                            
                            # 计算工资 = 公司市值 * 工资比例 * 职位乘数
                            salary = company["market_value"] * COMPANY_CONFIG["salary_percentage"] * multiplier
                            total_salary += salary
                            
                            # 添加到员工银行账户
                            user_data = self._get_user_data(group_id, employee_id)
                            user_data["bank"] += salary
                            self._save_user_data(group_id, employee_id, user_data)
                    
                    # 记录工资发放
                    company["last_salary_date"] = now.date().isoformat()
                    company["last_salary_amount"] = total_salary
                    self._log_operation("info", f"公司工资发放: {company_id}, 总额: {total_salary:.2f}金币")
                
                # 保存数据
                self._save_company_data()
                self._save_data(self.data)  # 保存用户数据
            
            # 每小时检查一次
            await asyncio.sleep(3600)
    #endregion

#endregion

#region ==================== 契约系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        msg = event.message_str.strip()
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        if msg.startswith("购买"):
            target_id = self._parse_at_target(event)
            if not target_id:
                yield event.plain_result("❌ 请@要购买的对象哦~杂鱼酱❤~")
                return
            async for result in self._handle_hire(event, group_id, user_id, target_id):
                yield result
            return

        elif msg.startswith("出售"):
            target_id = self._parse_at_target(event)
            if not target_id:
                yield event.plain_result("❌ 请@要出售的对象哦~杂鱼酱❤~")
                return
            async for result in self._handle_sell(event, group_id, user_id, target_id):
                yield result
            return

    def _parse_at_target(self, event):
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                return str(comp.qq)
        return None

    async def _handle_hire(self, event, group_id, employer_id, target_id):
        employer = self._get_user_data(group_id, employer_id)
        target_user = self._get_user_data(group_id, target_id)
        
        # 获取时间数据
        time_data = self._get_user_time_data(group_id, target_id)
        
        # 新增：检查目标是否有自由身保险
        insurance_until = time_data.get("free_insurance_until")
        if insurance_until:
            insurance_time = SHANGHAI_TZ.localize(datetime.fromisoformat(insurance_until))
            if insurance_time > datetime.now(SHANGHAI_TZ):
                target_name = await self._get_at_user_name(event, target_id)
                remaining = insurance_time - datetime.now(SHANGHAI_TZ)
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                yield event.plain_result(f"❌ {target_name} 有自由身保险，剩余 {hours}小时{minutes}分钟 内不可购买哦~杂鱼酱❤~")
                return
        
        # 检查目标是否是用户自己
        if employer_id == target_id:
            yield event.plain_result("❌ 不能购买自己哦~杂鱼酱❤~")
            return

        # 检查目标是否是机器人本身
        if target_id == event.get_self_id():
            yield event.plain_result("❌ 杂鱼酱❤~妹妹是天，妹妹最大，妹妹不能买")
            return
            
        # 检查目标用户是否有主人
        if target_user["contracted_by"] is not None:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 已有主人，无法购买哦~杂鱼酱❤~")
            return

        # 检查目标用户是否是自己的主人
        if employer.get("contracted_by") == target_id:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ 你不能购买自己的主人 {target_name}哦~杂鱼酱❤~")
            return
    
        # 原有检查...
        if len(employer["contractors"]) >= 100:
            yield event.plain_result("❌ 已达最大购买数量（100人）了哦~杂鱼酱❤~")
            return
        
        cost = self._calculate_wealth(target_user)
        if employer["coins"] < cost:
            yield event.plain_result(f"❌ 需要支付目标身价：{cost}金币哦~杂鱼酱❤~")
            return

        employer["coins"] -= cost
        employer["contractors"].append(target_id)
        target_user["contracted_by"] = employer_id
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[employer_id] = employer
            group_data[target_id] = target_user
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"购买性奴: group={group_id}, employer={employer_id}, "
                f"target={target_id}, cost={cost}"
            )
        except Exception as e:
            self._log_operation("error", f"购买性奴保存数据失败: {str(e)}")
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 杂鱼酱❤~你成功购买 {target_name}了，消耗{cost}金币")

    async def _handle_sell(self, event, group_id, employer_id, target_id):
        employer = self._get_user_data(group_id, employer_id)
        target_user = self._get_user_data(group_id, target_id)

        if target_id not in employer["contractors"]:
            yield event.plain_result("❌ 目标不在你的性奴列表中哦~杂鱼酱❤~")
            return

        sell_price = self._calculate_wealth(target_user) * 0.2
        employer["coins"] += sell_price
        employer["contractors"].remove(target_id)
        target_user["contracted_by"] = None
        
        # 新增：检查是否为永久绑定
        permanent_contractors = employer.get("permanent_contractors", [])
        is_permanent = target_id in permanent_contractors
        
        # 如果出售永久绑定的性奴，解除绑定
        if is_permanent:
            permanent_contractors.remove(target_id)
            employer["permanent_contractors"] = permanent_contractors
            target_user["is_permanent"] = False
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[employer_id] = employer
            group_data[target_id] = target_user
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"出售性奴: group={group_id}, employer={employer_id}, "
                f"target={target_id}, price={sell_price}, permanent={is_permanent}"
            )
        except Exception as e:
            self._log_operation("error", f"出售性奴保存数据失败: {str(e)}")
        
        # 在结果中添加提示
        target_name = await self._get_at_user_name(event, target_id)
        result = f"✅ 杂鱼酱❤~你成功出售性奴了呢，获得{sell_price:.1f}金币"
        if is_permanent:
            result += "\n⚠️ 注意: 已解除永久绑定关系"
        yield event.chain_result([Plain(text=result)])

    async def _get_at_user_name(self, event, target_id: str) -> str:
        try:
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
            if isinstance(event, AiocqhttpMessageEvent):
                client = event.bot
                resp = await client.api.call_action(
                    'get_group_member_info',
                    group_id=event.message_obj.group_id,
                    user_id=int(target_id),
                    no_cache=True
                )
                return resp.get('card') or resp.get('nickname', f'用户{target_id[-4:]}')
                
            raw_msg = event.message_str
            if match := re.search(r'\$CQ:at,qq=(\d+)\$', raw_msg):
                return f'用户{match.group(1)[-4:]}'
            return f'用户{target_id[-4:]}'
        except Exception as e:
            logger.warning(f"获取用户名失败: {target_id} - {str(e)}")
            return "神秘用户"

    @filter.command("赎身")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def terminate_contract(self, event: AstrMessageEvent):
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
    
        # 新增：检查是否为永久绑定
        if user_data.get("is_permanent", False):
            yield event.chain_result([Plain(text="❌ 您已被主人永久绑定，无法赎身哦~杂鱼酱❤~")])
            return
    
        if not user_data["contracted_by"]:
            yield event.chain_result([Plain(text="❌ 您暂无契约在身哦~大笨蛋杂鱼酱❤~")])
            return

        # 计算基础身价
        base_cost = self._calculate_wealth(user_data)
        # 赎身费用 = 1.5倍身价
        cost = base_cost * 1.5
    
        if user_data["coins"] < cost:
            yield event.chain_result([Plain(text=f"❌ 需要支付赎身费用：{cost:.1f}金币 (1.5倍身价)哦~杂鱼酱❤~")])
            return

        employer_id = user_data["contracted_by"]
        employer = self._get_user_data(group_id, employer_id)
        if user_id in employer["contractors"]:
            employer["contractors"].remove(user_id)
    
        user_data["contracted_by"] = None
        user_data["coins"] -= cost
    
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            group_data[employer_id] = employer
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"赎身: group={group_id}, user={user_id}, "
                f"employer={employer_id}, cost={cost}"
            )
        except Exception as e:
            self._log_operation("error", f"赎身保存数据失败: {str(e)}")
    
        # 显示基础身价和实际支付金额
        yield event.chain_result([Plain(
            text=f"✅ 诶呀~杂鱼酱赎身成功了呢❤~\n"
                f"- 基础身价: {base_cost:.1f}金币\n"
                f"- 赎身费用: {cost:.1f}金币 (1.5倍)\n"
                f"- 剩余金币: {user_data['coins']:.1f}"
        )])
#endregion

#region ==================== 资产系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    # 新增打劫命令
    @filter.command("打劫",alias={'抢劫'})
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def robbery(self, event: AstrMessageEvent):
        """打劫其他用户"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 解析@的目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要打劫的对象哦~杂鱼酱❤~")
            return
            
        group_id = str(event.message_obj.group_id)
        robber_id = str(event.get_sender_id())
        robber_data = self._get_user_data(group_id, robber_id)
        target_data = self._get_user_data(group_id, target_id)
        
        # 获取时间数据
        time_data = self._get_user_time_data(group_id, robber_id)
        
        # 检查打劫者金币是否足够
        if robber_data["coins"] < 100:
            yield event.plain_result("❌ 你这个杂鱼❤~~连100金币都没有，还学人打劫吗❤~")
            return
            
        # 检查目标金币是否足够
        if target_data["coins"] < 100:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 还是个穷光蛋，放过他吧~杂鱼酱❤~来满足下妹妹我的需求好不好啊❤~")
            return
            
        # 检查冷却时间
        now = datetime.now(SHANGHAI_TZ)
        if time_data["last_robbery"]:
            last_robbery = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data["last_robbery"]))
            if (now - last_robbery) < timedelta(minutes=60):
                remaining = 60 - int((now - last_robbery).total_seconds() / 60)
                yield event.plain_result(f"❌ 打劫太频繁了，请等待{remaining}分钟后再试哦~杂鱼酱❤~")
                return
                
        # 检查是否是自己的性奴
        is_contractor = target_id in robber_data["contractors"]
        
        # 打劫金额随机1-100
        amount = random.randint(1, 100)
        
        # 25%失败率（除非是自己的性奴）
        success = True
        if not is_contractor and random.random() < 0.25:
            success = False
            
        robber_name = event.get_sender_name()
        target_name = await self._get_at_user_name(event, target_id)
        
        if success:
            # 打劫成功
            # 确保目标有足够的金币
            if target_data["coins"] < amount:
                amount = target_data["coins"]  # 有多少抢多少
                
            target_data["coins"] -= amount
            robber_data["coins"] += amount
            
            # 更新打劫时间
            time_data["last_robbery"] = now.replace(tzinfo=None).isoformat()
            
            # 保存数据
            try:
                # 保存主数据
                data = self._load_data()
                group_data = data.setdefault(group_id, {})
                group_data[robber_id] = robber_data
                group_data[target_id] = target_data
                self._save_data(data)
                
                # 保存时间数据
                self._save_user_time_data(group_id, robber_id, time_data)
                
                # 记录日志
                self._log_operation("info", 
                    f"打劫成功: group={group_id}, robber={robber_id}, "
                    f"target={target_id}, amount={amount}"
                )
            except Exception as e:
                self._log_operation("error", f"打劫保存数据失败: {str(e)}")
                
            yield event.plain_result(f"✅ 杂鱼酱❤打劫成功了呢！{robber_name} 从 {target_name} 那里抢到了 {amount} 金币")
        else:
            # 打劫失败
            # 随机扣除1-100金币
            penalty = random.randint(1, 100)
            # 确保打劫者有足够的金币支付罚金
            if robber_data["coins"] < penalty:
                penalty = robber_data["coins"]  # 有多少扣多少
                
            robber_data["coins"] -= penalty
            
            # 更新打劫时间
            time_data["last_robbery"] = now.replace(tzinfo=None).isoformat()
            
            # 保存数据
            try:
                # 保存主数据
                data = self._load_data()
                group_data = data.setdefault(group_id, {})
                group_data[robber_id] = robber_data
                self._save_data(data)
                
                # 保存时间数据
                self._save_user_time_data(group_id, robber_id, time_data)
                
                # 记录日志
                self._log_operation("info", 
                    f"打劫失败: group={group_id}, robber={robber_id}, "
                    f"target={target_id}, penalty={penalty}"
                )
            except Exception as e:
                self._log_operation("error", f"打劫保存数据失败: {str(e)}")
                
            yield event.plain_result(f"❌ 打劫失败！{robber_name} 被警察抓住，罚款 {penalty} 金币，真是笨呢~杂鱼酱❤~")


    @filter.command("转账")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def transfer(self, event: AstrMessageEvent):
        """转账给其他用户"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
                
        msg_parts = event.message_str.strip().split()
        if len(msg_parts) < 3:
            yield event.chain_result([Plain(text="❌ 格式错误，请使用：/转账 <金额> @对方 哦~杂鱼酱❤~")])
            return

        try:
            amount = float(msg_parts[1])
        except ValueError:
            yield event.chain_result([Plain(text="❌ 请输入有效的数字金额 哦~杂鱼酱❤~")])
            return

        if amount <= 0:
            yield event.chain_result([Plain(text="❌ 转账金额必须大于0 哦~杂鱼酱❤~")])
            return

        # 获取转账目标
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.chain_result([Plain(text="❌ 请@转账对象哦~杂鱼酱❤~")])
            return

        group_id = str(event.message_obj.group_id)
        sender_id = str(event.get_sender_id())

        if sender_id == target_id:
            yield event.chain_result([Plain(text="❌ 不能转账给自己哦~大笨蛋杂鱼酱❤~")])
            return

        # 获取双方数据
        sender_data = self._get_user_data(group_id, sender_id)
        receiver_data = self._get_user_data(group_id, target_id)

        # 添加转账手续费（10%）
        fee = amount * 0.10
        total_deduct = amount + fee

        # 检查发送方是否有足够资金（包括手续费）
        if sender_data["coins"] < total_deduct:
            yield event.chain_result([Plain(text=f"❌ 现金不足（含手续费），需要 {total_deduct:.1f}金币，当前现金: {sender_data['coins']:.1f}金币哦~杂鱼酱❤~")])
            return

        # 执行转账（扣除金额+手续费）
        sender_data["coins"] -= total_deduct
        receiver_data["coins"] += amount

        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[sender_id] = sender_data
            group_data[target_id] = receiver_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"转账: group={group_id}, from={sender_id}, "
                f"to={target_id}, amount={amount}, fee={fee}"
            )
        except Exception as e:
            self._log_operation("error", f"转账保存数据失败: {str(e)}")
            yield event.chain_result([Plain(text="❌ 转账失败，数据保存异常")])
            return

        # 获取目标用户的名字
        target_name = await self._get_at_user_name(event, target_id)
        sender_name = event.get_sender_name()

        # 通知双方
        yield event.chain_result([Plain(
            text=f"✅ 杂鱼酱❤转账成功了呢！\n"
                 f"- {sender_name} → {target_name}\n"
                 f"- 金额: {amount:.1f}金币\n"
                 f"- 手续费: {fee:.1f}金币\n"
                 f"- 你的现金余额: {sender_data['coins']:.1f}金币"
        )])

    @filter.command("存款")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def deposit(self, event: AstrMessageEvent):
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        msg_parts = event.message_str.strip().split()
        if len(msg_parts) < 2:
            yield event.chain_result([Plain(text="❌ 格式错误，请使用：/存款 <金额> 哦~杂鱼酱❤~")])
            return
        
        try:
            amount = float(msg_parts[1])
        except ValueError:
            yield event.chain_result([Plain(text="❌ 请输入有效的数字金额哦~杂鱼酱❤~")])
            return

        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        
        if amount <= 0:
            yield event.chain_result([Plain(text="❌ 存款金额必须大于0 哦~杂鱼酱❤~")])
            return
        
        # 计算可用总额（本插件金币 + 牛牛插件金币）
        total_available = user_data["coins"] + user_data.get("niuniu_coins", 0.0)
        
        if amount > total_available:
            yield event.chain_result([Plain(text="❌ 可用金币不足哦~杂鱼酱❤~")])
            return
        
        # 优先使用本插件的金币
        if user_data["coins"] >= amount:
            user_data["coins"] -= amount
        else:
            remaining = amount - user_data["coins"]
            user_data["coins"] = 0.0
            # 从牛牛插件的金币中扣除剩余部分
            niuniu_data_path = os.path.join('data', 'niuniu_lengths.yml')
            if os.path.exists(niuniu_data_path):
                try:
                    with open(niuniu_data_path, 'r', encoding='utf-8') as f:
                        niuniu_data = yaml.safe_load(f) or {}
                    # 确保群组和用户数据存在
                    if group_id not in niuniu_data:
                        niuniu_data[group_id] = {}
                    if user_id not in niuniu_data[group_id]:
                        niuniu_data[group_id][user_id] = {}
                    niuniu_data[group_id][user_id]['coins'] = niuniu_data[group_id][user_id].get('coins', 0.0) - remaining
                    with open(niuniu_data_path, 'w', encoding='utf-8') as f:
                        yaml.dump(niuniu_data, f, allow_unicode=True)
                except Exception as e:
                    self._log_operation("error", f"更新牛牛数据失败: {str(e)}")
                    yield event.chain_result([Plain(text="❌ 更新牛牛插件数据失败")])
                    return
        
        user_data["bank"] += amount
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"存款: group={group_id}, user={user_id}, "
                f"amount={amount}"
            )
        except Exception as e:
            self._log_operation("error", f"存款保存数据失败: {str(e)}")
        
        yield event.chain_result([Plain(text=f"✅ 杂鱼酱❤成功存入 {amount:.1f} 金币了呢")])

    @filter.command("取款")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def withdraw(self, event: AstrMessageEvent):
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        msg_parts = event.message_str.strip().split()
        if len(msg_parts) < 2:
            yield event.chain_result([Plain(text="❌ 格式错误，请使用：/取款 <金额> 哦~杂鱼酱❤~")])
            return
        
        try:
            amount = float(msg_parts[1])
        except ValueError:
            yield event.chain_result([Plain(text="❌ 请输入有效的数字金额哦~杂鱼酱❤~")])
            return

        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        
        if amount <= 0:
            yield event.chain_result([Plain(text="❌ 取款金额必须大于0 哦~杂鱼酱❤~")])
            return
        
        if amount > user_data["bank"]:
            yield event.chain_result([Plain(text="❌ 银行存款不足哦~杂鱼酱❤~")])
            return
        
        user_data["bank"] -= amount
        user_data["coins"] += amount
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"取款: group={group_id}, user={user_id}, "
                f"amount={amount}"
            )
        except Exception as e:
            self._log_operation("error", f"取款保存数据失败: {str(e)}")
        
        yield event.chain_result([Plain(text=f"✅ 杂鱼酱❤成功取出 {amount:.1f} 金币了呢")])

    @filter.command("资产核查")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def asset_check(self, event: AstrMessageEvent):
        """查询指定用户的资产情况"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 解析@的目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要查询的用户哦~杂鱼酱❤~")
            return
    
        group_id = str(event.message_obj.group_id)
    
        # 获取目标用户数据
        target_data = self._get_user_data(group_id, target_id)
    
        # 获取牛牛插件金币
        niuniu_coins = target_data.get("niuniu_coins", 0.0)
    
        # 计算总资产
        total_assets = target_data["coins"] + target_data["bank"] + niuniu_coins
    
        # 获取财富等级信息
        wealth_level, wealth_rate = self._get_wealth_info({
            "coins": target_data["coins"],
            "bank": target_data["bank"],
            "niuniu_coins": niuniu_coins
        })
    
        # 获取目标用户名称
        target_name = await self._get_at_user_name(event, target_id)
    
        # 生成资产核查卡片
        card_path = await self._generate_asset_card(
            event=event,
            user_id=target_id,
            user_name=target_name,
            coins=target_data["coins"],
            bank=target_data["bank"],
            niuniu_coins=niuniu_coins,
            total_assets=total_assets,
            wealth_level=wealth_level,
            wealth_rate=wealth_rate
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

#endregion

#region ==================== 帮助系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command("签到帮助")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def show_help(self, event: AstrMessageEvent):
        """显示财富与契约插件帮助菜单"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 所有帮助条目
        help_text = """
📊 财富与契约插件使用帮助📊

==============【核心功能】==============
/签到
- 每日签到获得金币奖励
- 连续签到有额外奖励
- 银行利息每日1%
- 特殊关系提供额外加成（恋人+5%，夫妻+15%等）
====================
/签到查询
- 查看当前签到状态
- 显示预计收益详情

==============【经济系统】==============
/存款 <金额>
- 将现金存入银行获得利息
- 示例: /存款 100
====================
/取款 <金额>
- 从银行取出金币到现金
- 示例: /取款 50
====================
/转账 <金额> @对方
- 转账给其他用户
- 收取10%手续费
- 示例: /转账 200 @用户
====================
/资产核查@用户
- 查询用户的资产详情（现金、银行、牛牛金币）
- 显示财富等级信息
====================
/打劫@用户
- 打劫其他用户的金币
- 25%失败率，失败会被罚款
- 打劫自己的性奴100%成功
- 60分钟冷却时间

==============【排行榜系统】==============
/金币排行榜
- 显示本群金币总资产前10名用户
====================
/性奴排行榜
- 显示本群拥有性奴数量前10名用户

==============【契约系统】==============
购买@用户
- 购买其他用户作为性奴
- 示例: 购买@用户
====================
出售@用户
- 出售你拥有的性奴
- 示例: 出售@用户
====================
/我的契约
- 查看当前契约关系（主人和性奴）
====================
/看看你的契约@用户
- 查看指定用户的契约关系（主人和性奴）
- 示例: /看看你的契约@用户
====================
/看看详细契约@用户
- 查看用户的详细契约信息（文本形式）
- 示例: /看看详细契约@用户
- 示例: /看看详细契约
====================
/赎身
- 支付1.5倍身价解除契约关系

==============【打工系统】==============
/打工 工作名 @用户
- 让性奴打工赚钱
- 示例: /打工 卖银 @用户
====================
/一键打工 工作名
- 让所有性奴同时进行指定工作
- 示例: /一键打工 送外卖
====================
/打工列表
- 显示可用的工作列表
====================
/打工查询
- 查询性奴打工冷却时间和签到加成详情

==============【社交系统】==============
/社交做 <事件名> [强制] @用户
- 发起社交邀请（如看电影、共进晚餐）
- 使用"强制"时无需对方同意但成功率降低
- 示例: /社交做 看电影 @用户
====================
/社交同意做 <验证码>
- 同意社交邀请
- 示例: /社交同意做 SOCIAL-1234
====================
/社交列表
- 显示所有可用的社交活动
====================
/社交邀请
- 查看自己收到的社交邀请
====================
/约会@对方
- 向其他用户发起约会邀请
- 每日最多可发起10次约会
- 好感度达到500点后需建立特殊关系才能继续提升
====================
/同意约会 <验证码>
- 使用验证码兼容多人约会
====================
/我的约会邀请
- 查看我的约会邀请
====================
/缔结关系@对方 关系类型
- 与对方缔结特殊关系（恋人、兄弟、包养）
- 需要双方好感度达到500点
- 需要特定道具：
  - 恋人：卡天亚戒指
  - 兄弟：一壶烈酒
  - 包养：黑金卡
  - 闺蜜：百合花种
====================
/升级关系@对方
- 升级现有关系（如恋人->夫妻）
- 需要特定道具：
  - 夫妻：永恒钻戒
  - 结义兄弟：金兰谱
  - 长期包养：白金卡
  - 百合：百合花蜜
====================
/解除关系@对方
- 解除与对方的特殊关系
- 解除后双方好感度重置为50点
====================
/查看关系@对方
- 查看你与对方的关系状态
====================
/社交网络
- 查看你的关系状态

==============【道具系统】==============
/签到商店
- 查看可购买的道具列表
====================
/签到背包
- 查看自己拥有的道具
====================
/签到商店购买 <道具名> [数量]
- 购买道具
====================
/道具 使用 <道具名> [@目标]
- 使用道具（如驯服贴、强制购买符等）
====================
/道具 赠送 <道具名> @用户
- 赠送礼物道具（增加好感度）

==============【股票系统】==============
/股票行情
- 查看当前股票市场行情
- 交易时间: 8:00-18:00
====================
/买入股票 <股票名> <数量>
- 购买指定数量的股票
- 示例: /买入股票 茅台科技 10
====================
/卖出股票 <股票名> <数量>
- 出售持有的股票
- 收取1%手续费
- 示例: /卖出股票 企鹅控股 5
====================
/抛售 [股票名]
- 一键卖出所有股票或指定股票
- 示例: /抛售
- 示例: /抛售 茅台科技
====================
/我的持仓
- 查看当前持有的股票及盈亏情况

==============【彩票提示】==============
- 在商店购买彩票道具
- 使用命令: /道具 使用 彩票
- 每人每天最多使用10次
- 2%中奖概率，奖金1500-50000金币
- 总资产超过500金币禁止购买
- 拥有3个或以上性奴禁止购买

==============【证件系统】==============
/申请证件 <证件名> @对方
- 申请证件（如结婚证、房产证等）
- 示例: /申请证件 结婚证 @对方
====================
/同意证件 <验证码>
- 同意证件申请
- 示例: /同意证件 1234
====================
/我的证件
- 列出我的所有证件
- 显示证件ID和状态
====================
/展示证件 <证件ID>
- 展示证件详情（精美图片）
- 示例: /展示证件 marriage_1234567890

==============【资产系统】==============
/购入资产 <资产名>
- 购买房产、车子等资产
- 示例: /购入资产 汤臣一品
====================
/卖出资产 <资产名>
- 出售资产
- 示例: /卖出资产 劳斯莱斯
====================
/我的资产
- 列出我的所有资产
- 显示资产价值和类型

==============【其他命令】==============
/WACadmin
- 管理员命令组
====================
/WACadmin-us
- 授权管理员命令组
====================
/牛牛菜单
- 牛牛插件帮助菜单
        """.strip()
        
        # 生成所有图片
        image_paths = await self.text_to_images(
            text=help_text,
            title="签到帮助"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)
#endregion

#region ==================== 排行榜系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command("金币排行榜")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def wealth_leaderboard(self, event: AstrMessageEvent):
        """显示金币排行榜（总资产前10名）"""
        group_id = str(event.message_obj.group_id)
        # 黑名单检查
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 加载数据
        data = self._load_data()
        

        group_data = data.get(group_id, {})
        
        # 加载牛牛插件数据
        niuniu_data = {}
        niuniu_data_path = os.path.join('data', 'niuniu_lengths.yml')
        if os.path.exists(niuniu_data_path):
            try:
                # 优先使用缓存
                if self._niuniu_cache is not None:
                    niuniu_data = self._niuniu_cache
                else:
                    with open(niuniu_data_path, 'r', encoding='utf-8') as f:
                        niuniu_data = yaml.safe_load(f) or {}
                    self._niuniu_cache = niuniu_data
                    self._niuniu_cache_time = time.time()
            except Exception as e:
                self._log_operation("error", f"加载牛牛排行榜数据失败: {str(e)}")
                pass
        
        # 计算每个用户的总资产
        user_wealth = []
        for user_id, user_data in group_data.items():
            niuniu_coins = niuniu_data.get(group_id, {}).get(user_id, {}).get('coins', 0.0)
            total_wealth = user_data.get('coins', 0.0) + user_data.get('bank', 0.0) + niuniu_coins
            user_wealth.append((user_id, total_wealth))
        
        # 按总资产排序（降序）
        user_wealth.sort(key=lambda x: x[1], reverse=True)
        
        # 只取前10名
        top_users = user_wealth[:10]
        
        # 获取用户名
        leaderboard = []
        for rank, (user_id, wealth) in enumerate(top_users, start=1):
            try:
                user_name = await self._get_at_user_name(event, user_id)
            except:
                user_name = f"用户{user_id[-4:]}"
            leaderboard.append((rank, user_name, wealth))
        
        # 生成排行榜图片
        card_path = await self._generate_wealth_leaderboard(
            event=event,
            group_id=group_id,
            leaderboard=leaderboard
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

    @filter.command("性奴排行榜")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def contractor_leaderboard(self, event: AstrMessageEvent):
        """显示性奴排行榜（拥有性奴数量前10名）"""
        group_id = str(event.message_obj.group_id)
        # 黑名单检查
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 加载数据
        data = self._load_data()
        
        group_data = data.get(group_id, {})
        
        # 计算每个用户的性奴数量
        user_contractors = []
        for user_id, user_data in group_data.items():
            contractor_count = len(user_data.get('contractors', []))
            user_contractors.append((user_id, contractor_count))
        
        # 按性奴数量排序（降序）
        user_contractors.sort(key=lambda x: x[1], reverse=True)
        
        # 只取前10名
        top_users = user_contractors[:10]
        
        # 获取用户名
        leaderboard = []
        for rank, (user_id, count) in enumerate(top_users, start=1):
            try:
                user_name = await self._get_at_user_name(event, user_id)
            except:
                user_name = f"用户{user_id[-4:]}"
            leaderboard.append((rank, user_name, count))
        
        # 生成排行榜图片
        card_path = await self._generate_contractor_leaderboard(
            event=event,
            group_id=group_id,
            leaderboard=leaderboard
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

#endregion

#region ==================== 打工系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    # 新增打工命令
    @filter.command("打工")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def work_command(self, event: AstrMessageEvent):
        """让性奴打工赚钱"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 解析消息：/打工 工作类型 @目标
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/打工 工作类型 @目标 哦~杂鱼酱❤~")
            return
        
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要打工的对象哦~杂鱼酱❤~")
            return
        
        job_name = parts[1]
        if job_name not in JOBS:
            yield event.plain_result(f"❌ 未知工作类型，可用工作：{', '.join(JOBS.keys())}")
            return
        
        group_id = str(event.message_obj.group_id)
        employer_id = str(event.get_sender_id())
        
        # 获取用户数据
        employer_data = self._get_user_data(group_id, employer_id)
        target_data = self._get_user_data(group_id, target_id)
        
        # 获取时间数据
        time_data = self._get_user_time_data(group_id, target_id)
        
        # 检查是否是自己的性奴
        if target_id not in employer_data["contractors"]:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 不是你的性奴，无法让其打工哦~杂鱼酱❤~")
            return
        
        # 检查冷却时间（每小时只能打工一次）
        now = datetime.now(SHANGHAI_TZ)
        if time_data.get("last_work"):
            last_work = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data["last_work"]))
            if (now - last_work) < timedelta(hours=1):
                remaining_minutes = 60 - int((now - last_work).total_seconds() / 60)
                target_name = await self._get_at_user_name(event, target_id)
                yield event.plain_result(f"❌ {target_name} 需要休息，请等待{remaining_minutes}分钟后再来打工，你个黑心杂鱼酱❤~")
                return
        
        # 获取工作信息
        job = JOBS[job_name]
        
        # 检查雇主是否有足够金币支付可能的最大惩罚（如果工作有失败惩罚）
        if job["risk_cost"][1] > 0:  # 有失败惩罚的工作
            max_risk = job["risk_cost"][1]
            if employer_data["coins"] < max_risk:
                yield event.plain_result(f"❌ 雇主金币不足，无法支付可能的最大惩罚（{max_risk}金币），穷鬼杂鱼酱❤~")
                return
        
        # 执行打工
        is_success = random.random() < job["success_rate"]
        
        if is_success:
            # 打工成功
            min_reward, max_reward = job["reward"]
            reward = random.uniform(min_reward, max_reward)
            employer_data["coins"] += reward
            
            # 更新消息
            target_name = await self._get_at_user_name(event, target_id)
            msg = job["success_msg"].format(
                worker_name=target_name,
                reward=reward
            )
        else:
            # 打工失败
            min_risk, max_risk = job["risk_cost"]
            risk_cost = random.uniform(min_risk, max_risk)
            
            # 确保有足够的金币支付风险
            if employer_data["coins"] < risk_cost:
                # 如果余额不足，不允许打工
                yield event.plain_result(f"❌ 雇主金币不足，无法支付可能的惩罚（{risk_cost:.1f}金币），穷鬼杂鱼酱❤~")
                return
            
            employer_data["coins"] -= risk_cost
            
            # 更新消息
            target_name = await self._get_at_user_name(event, target_id)
            msg = job["failure_msg"].format(
                worker_name=target_name,
                risk_cost=risk_cost
            )
        
        # 更新打工时间
        time_data["last_work"] = now.replace(tzinfo=None).isoformat()
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[employer_id] = employer_data
            group_data[target_id] = target_data
            self._save_data(data)
            
            # 保存时间数据
            self._save_user_time_data(group_id, target_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"打工: group={group_id}, employer={employer_id}, "
                f"worker={target_id}, job={job_name}, "
                f"success={is_success}, reward={reward if is_success else -risk_cost}"
            )
        except Exception as e:
            self._log_operation("error", f"打工保存数据失败: {str(e)}")
        
        yield event.plain_result(f"✅ {msg}")

    @filter.command("打工列表")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def work_list_command(self, event: AstrMessageEvent):
        """显示可用的工作列表"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 生成工作列表文本
        job_list = []
        for name, details in JOBS.items():
            min_reward, max_reward = details["reward"]
            success_rate = details["success_rate"] * 100
            
            if details["risk_cost"][0] > 0:
                min_risk, max_risk = details["risk_cost"]
                risk_info = f"失败惩罚: {min_risk}-{max_risk}金币"
            else:
                risk_info = "无失败惩罚"
            
            job_list.append(
                f"【{name}】\n"
                f"- 报酬: {min_reward}-{max_reward}金币\n"
                f"- 成功率: {success_rate:.1f}%\n"
                f"- {risk_info}"
            )

        response = "📋 可用工作列表：\n\n" + "\n\n".join(job_list)

        # 生成所有图片
        image_paths = await self.text_to_images(
            text=response,
            title="工作列表"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)        

    @filter.command("一键打工")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def batch_work_command(self, event: AstrMessageEvent):
        """让所有性奴同时进行指定的工作"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 解析消息：/一键打工 工作名
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/一键打工 工作名 哦~杂鱼酱❤~")
            return
        
        job_name = parts[1]
        if job_name not in JOBS:
            yield event.plain_result(f"❌ 未知工作类型，可用工作：{', '.join(JOBS.keys())}")
            return
        
        group_id = str(event.message_obj.group_id)
        employer_id = str(event.get_sender_id())
        
        # 获取用户数据
        employer_data = self._get_user_data(group_id, employer_id)
        
        # 检查是否有性奴
        if not employer_data["contractors"]:
            yield event.plain_result("❌ 您还没有性奴，无法使用一键打工哦~杂鱼酱❤~")
            return
        
        # 获取工作信息
        job = JOBS[job_name]
        
        # 检查雇主是否有足够金币支付可能的最大惩罚（如果工作有失败惩罚）
        max_risk = job["risk_cost"][1] if job["risk_cost"][1] > 0 else 0
        if max_risk > 0 and employer_data["coins"] < max_risk * len(employer_data["contractors"]):
            yield event.plain_result(f"❌ 雇主金币不足，无法支付所有性奴可能的最大惩罚（{max_risk * len(employer_data['contractors'])}金币），穷鬼杂鱼酱❤~")
            return
        
        # 执行批量打工
        results = []
        total_reward = 0
        total_risk = 0
        now = datetime.now(SHANGHAI_TZ)
        
        for target_id in employer_data["contractors"]:
            target_data = self._get_user_data(group_id, target_id)
            time_data = self._get_user_time_data(group_id, target_id)
            
            # 检查冷却时间
            if time_data.get("last_work"):
                last_work = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data["last_work"]))
                if (now - last_work) < timedelta(hours=1):
                    # 跳过冷却中的性奴
                    target_name = await self._get_at_user_name(event, target_id)
                    results.append(f"⏳ {target_name} 需要休息，跳过")
                    continue
            
            # 执行打工
            is_success = random.random() < job["success_rate"]
            
            if is_success:
                # 打工成功
                min_reward, max_reward = job["reward"]
                reward = random.uniform(min_reward, max_reward)
                total_reward += reward
                
                # 更新消息
                target_name = await self._get_at_user_name(event, target_id)
                results.append(job["success_msg"].format(
                    worker_name=target_name,
                    reward=reward
                ))
            else:
                # 打工失败
                min_risk, max_risk = job["risk_cost"]
                risk_cost = random.uniform(min_risk, max_risk)
                total_risk += risk_cost
                
                # 更新消息
                target_name = await self._get_at_user_name(event, target_id)
                results.append(job["failure_msg"].format(
                    worker_name=target_name,
                    risk_cost=risk_cost
                ))
            
            # 更新打工时间
            time_data["last_work"] = now.replace(tzinfo=None).isoformat()
            
            # 保存目标用户数据
            try:
                # 保存时间数据
                self._save_user_time_data(group_id, target_id, time_data)
            except Exception as e:
                self._log_operation("error", f"保存性奴时间数据失败: {str(e)}")
        
        # 更新雇主金币
        employer_data["coins"] += total_reward
        employer_data["coins"] -= total_risk
        
        # 保存雇主数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[employer_id] = employer_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"一键打工: group={group_id}, employer={employer_id}, "
                f"job={job_name}, reward={total_reward}, risk={total_risk}"
            )
        except Exception as e:
            self._log_operation("error", f"一键打工保存数据失败: {str(e)}")
        
        # 构建响应消息
        response = f"📊 一键打工结果（{job_name}）\n\n"
        response += "\n".join(results)
        response += f"\n\n💰 总收入: {total_reward:.1f}金币"
        response += f"\n💸 总损失: {total_risk:.1f}金币"
        response += f"\n💼 净收益: {(total_reward - total_risk):.1f}金币"
        response += f"\n💳 当前现金: {employer_data['coins']:.1f}金币"
        
        yield event.plain_result(response)

    @filter.command("打工查询")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def work_query(self, event: AstrMessageEvent):
        """查询性奴打工冷却时间和签到加成详情"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        
        # 获取时间数据
        time_data = self._get_user_time_data(group_id, user_id)
        
        # 计算签到加成信息
        base_income = BASE_INCOME
        wealth_level, wealth_rate = self._get_wealth_info(user_data)
        wealth_bonus = base_income * wealth_rate
        
        # 契约加成
        contractor_bonus = 0.0
        for cid in user_data["contractors"]:
            try:
                contractor_data = self._get_user_data(group_id, cid)
                _, c_rate = self._get_wealth_info(contractor_data)
                contractor_bonus += base_income * c_rate
            except:
                pass
        
        # 连签加成
        consecutive_bonus = 10 * user_data["consecutive"]
        
        # 关系加成
        relation_bonus = self.get_relation_bonus(group_id, user_id)
        
        # 总加成
        total_bonus = wealth_bonus + contractor_bonus + consecutive_bonus + relation_bonus
        
        # 构建响应消息
        response = "⏱️ 性奴打工冷却时间查询：\n\n"
        
        if not user_data["contractors"]:
            response += f"❌ 您还没有性奴哦~杂鱼酱❤~\n"

        now = datetime.now(SHANGHAI_TZ)
        for cid in user_data["contractors"]:
            # 获取性奴名称
            try:
                cname = await self._get_at_user_name(event, cid)
            except:
                cname = f"用户{cid[-4:]}"
            
            # 获取性奴时间数据
            c_time_data = self._get_user_time_data(group_id, cid)
            
            # 检查最后打工时间
            if c_time_data.get("last_work"):
                last_work = SHANGHAI_TZ.localize(datetime.fromisoformat(c_time_data["last_work"]))
                elapsed = now - last_work
                
                if elapsed < timedelta(hours=1):
                    remaining = timedelta(hours=1) - elapsed
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    response += f"🧑 {cname}：冷却中，还需 {minutes}分{seconds}秒\n"
                else:
                    response += f"🧑 {cname}：可立即打工\n"
            else:
                response += f"🧑 {cname}：可立即打工\n"
        
        # 添加详细的签到加成信息
        response += "\n📊 签到加成详情：\n"
        response += f"- 基础收益: {base_income:.1f}金币\n"
        response += f"- 财富等级加成: {wealth_bonus:.1f}金币 ({wealth_level}, +{wealth_rate*100:.0f}%)\n"
        response += f"- 契约加成: {contractor_bonus:.1f}金币 (性奴财富等级加成)\n"
        response += f"- 连签加成: {consecutive_bonus:.1f}金币 (连续签到{user_data['consecutive']}天)\n"
        response += f"- 关系加成: {relation_bonus:.1f}金币 (特殊关系加成)\n"
        response += f"💰 总加成: {total_bonus:.1f}金币\n"
        response += f"💼 预计下次签到收益: {base_income + total_bonus:.1f}金币"
        
        yield event.plain_result(response)
#endregion

#region ==================== 契约查询系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command("我的契约")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def my_contracts(self, event: AstrMessageEvent):
        """显示用户的契约关系（主人和性奴）"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 获取主人信息（如果有）
        master_info = None
        if user_data["contracted_by"]:
            master_id = user_data["contracted_by"]
            master_name = await self._get_at_user_name(event, master_id)
            master_info = (master_id, master_name)
    
        # 获取性奴列表（最多显示8个）
        contractors = []
        for cid in user_data["contractors"]:
            try:
                cname = await self._get_at_user_name(event, cid)
                contractors.append((cid, cname))
            except:
                contractors.append((cid, f"用户{cid[-4:]}"))
    
        # 生成契约关系卡片
        card_path = await self._generate_contract_card(
            event=event,
            user_id=user_id,
            user_name=event.get_sender_name(),
            master_info=master_info,
            contractors=contractors,
            group_id=group_id,
            is_permanent=user_data.get("is_permanent", False)  # 新增永久状态参数
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

    @filter.command("看看你的契约")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def view_contract(self, event: AstrMessageEvent):
        """查看指定用户的契约关系"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 解析@的目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要查看的用户")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取目标用户数据
        target_data = self._get_user_data(group_id, target_id)
        
        # 获取主人信息（如果有）
        master_info = None
        if target_data["contracted_by"]:
            master_id = target_data["contracted_by"]
            master_name = await self._get_at_user_name(event, master_id)
            master_info = (master_id, master_name)
    
        # 获取性奴列表
        contractors = []
        for cid in target_data["contractors"]:
            try:
                cname = await self._get_at_user_name(event, cid)
                contractors.append((cid, cname))
            except:
                contractors.append((cid, f"用户{cid[-4:]}"))
        
        # 获取目标用户名称
        target_name = await self._get_at_user_name(event, target_id)
        
        # 生成契约关系卡片
        card_path = await self._generate_contract_card(
            event=event,
            user_id=target_id,
            user_name=target_name,
            master_info=master_info,
            contractors=contractors,
            group_id=group_id,
            is_permanent=target_data.get("is_permanent", False)  # 新增永久状态参数
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

    @filter.command("看看详细契约")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def detailed_contract(self, event: AstrMessageEvent):
        """显示用户及其契约关系的详细信息"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        # 解析@的目标用户
        target_id = self._parse_at_target(event)
        group_id = str(event.message_obj.group_id)
    
        # 如果没有@用户，则使用发送者自己的ID
        if not target_id:
            target_id = str(event.get_sender_id())
    
        # 获取目标用户数据
        target_data = self._get_user_data(group_id, target_id)
    
        # 获取目标用户名称
        target_name = await self._get_at_user_name(event, target_id)
    
        # 获取主人信息（如果有）
        master_info = None
        if target_data["contracted_by"]:
            master_id = target_data["contracted_by"]
            try:
                master_name = await self._get_at_user_name(event, master_id)
                master_info = f"{master_name} ({master_id})"
            except:
                master_info = f"用户{master_id[-4:]}"
    
        # 获取性奴列表
        contractors = []
        for cid in target_data["contractors"]:
            try:
                cname = await self._get_at_user_name(event, cid)
                contractors.append(f"{cname} ({cid})")
            except:
                contractors.append(f"用户{cid[-4:]}")
    
        # 计算财富等级
        total_wealth = target_data["coins"] + target_data["bank"] + target_data.get("niuniu_coins", 0.0)
        wealth_level, wealth_rate = self._get_wealth_info({
            "coins": target_data["coins"],
            "bank": target_data["bank"],
            "niuniu_coins": target_data.get("niuniu_coins", 0.0)
        })
    
        # 构建响应消息
        response = f"📋 杂鱼酱❤{target_name} 的详细契约信息：\n\n"
        response += f"- QQ: {target_id}\n"
        response += f"- 财富等级: {wealth_level} (加成率: {wealth_rate*100:.0f}%)\n"
        response += f"- 总资产: {total_wealth:.1f}金币\n"
        response += f"- 现金: {target_data['coins']:.1f}金币\n"
        response += f"- 银行存款: {target_data['bank']:.1f}金币\n"
        response += f"- 牛牛金币: {target_data.get('niuniu_coins', 0.0):.1f}金币\n\n"
    
        if master_info:
            response += f"👑 主人: {master_info}\n\n"
        else:
            response += "🎗️ 自由之身，暂无主人\n\n"
    
        if contractors:
            response += f"🧑 性奴列表 ({len(contractors)}人):\n"
            for i, contractor in enumerate(contractors, start=1):
                response += f"  {i}. {contractor}\n"
        else:
            response += "📭 暂无性奴"
    
        yield event.chain_result([Plain(text=response)])
#endregion

#region ==================== 签到系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command("签到")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def sign_in(self, event: AstrMessageEvent):
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        time_data = self._get_user_time_data(group_id, user_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        now = datetime.now(SHANGHAI_TZ)
        today = now.date()
    
        if time_data["last_sign"]:
            last_sign = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data["last_sign"]))
            if last_sign.date() == today:
                yield event.chain_result([Plain(text="❌ 今日已签到，请明天再来光顾妹妹我哦~杂鱼酱❤~")])
                return

        interest = user_data["bank"] * 0.01
        user_data["bank"] += interest

        if time_data["last_sign"]:
            last_sign = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data["last_sign"]))
            delta = today - last_sign.date()
            user_data["consecutive"] = 1 if delta.days > 1 else user_data["consecutive"] + 1
        else:
            user_data["consecutive"] = 1

        # 获取用户自身身份的加成
        user_wealth_level, user_wealth_rate = self._get_wealth_info(user_data)
    
        # 计算契约收益加成
        contractor_rates = sum(
            self._get_wealth_info(self._get_user_data(group_id, c))[1]
            for c in user_data["contractors"]
        )
        
        # 计算性奴的性奴加成（50%）
        sub_contractor_rates = 0
        for cid in user_data["contractors"]:
            contractor_data = self._get_user_data(group_id, cid)
            for sub_cid in contractor_data["contractors"]:
                sub_contractor = self._get_user_data(group_id, sub_cid)
                _, rate = self._get_wealth_info(sub_contractor)
                sub_contractor_rates += rate * 0.5  # 50%加成
    
        # 计算连签奖励
        consecutive_bonus = 10 * (user_data["consecutive"] - 1)  
    
        # 计算特殊关系加成
        relation_bonus = self.get_relation_bonus(group_id, user_id)
        
        # 计算签到收益
        earned = BASE_INCOME * (1 + user_wealth_rate) * (1 + contractor_rates + sub_contractor_rates) + consecutive_bonus + relation_bonus

        user_data["coins"] += earned
        time_data["last_sign"] = now.replace(tzinfo=None).isoformat()
    
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
            
            # 保存时间数据
            self._save_user_time_data(group_id, user_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"签到: group={group_id}, user={user_id}, "
                f"earned={earned}, consecutive={user_data['consecutive']}, "
                f"relation_bonus={relation_bonus}"
            )
        except Exception as e:
            self._log_operation("error", f"签到保存数据失败: {str(e)}")
    
        # 生成签到卡片
        card_path = await self._generate_card(
            event=event,
            user_id=user_id,
            user_name=event.get_sender_name(),
            coins=user_data["coins"] + user_data.get("niuniu_coins", 0.0),  # 显示总额
            bank=user_data["bank"],
            consecutive=user_data["consecutive"],
            contractors=user_data["contractors"],
            is_contracted=bool(user_data["contracted_by"]),
            interest=interest,
            earned=earned,
            group_id=group_id,
            is_query=False,
            relation_bonus=relation_bonus  # 新增关系加成显示
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])


    @filter.command("签到查询")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def sign_query(self, event: AstrMessageEvent):
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return    

        # 获取用户财富信息
        user_wealth_level, user_wealth_rate = self._get_wealth_info(user_data)
    
        # 计算契约收益加成
        contractor_rates = 0.0
        for cid in user_data["contractors"]:
            try:
                contractor_data = self._get_user_data(group_id, cid)
                _, rate = self._get_wealth_info(contractor_data)
                contractor_rates += rate
            except:
                continue
    
        # 计算连签奖励
        consecutive_bonus = 10 * user_data["consecutive"]
    
        # 计算特殊关系加成
        relation_bonus = self.get_relation_bonus(group_id, user_id)
    
        # 计算预期收益
        earned = BASE_INCOME * (1 + user_wealth_rate) * (1 + contractor_rates) + consecutive_bonus + relation_bonus

        # 生成签到卡片
        card_path = await self._generate_card(
            event=event,
            user_id=user_id,
            user_name=event.get_sender_name(),
            coins=user_data["coins"] + user_data.get("niuniu_coins", 0.0),
            bank=user_data["bank"],
            consecutive=user_data["consecutive"],
            contractors=user_data["contractors"],
            is_contracted=bool(user_data["contracted_by"]),
            interest=user_data["bank"] * 0.01,
            earned=earned,
            group_id=group_id,
            is_query=True,
            user_wealth_rate=user_wealth_rate,
            relation_bonus=relation_bonus
        )
        yield event.chain_result([Image.fromFileSystem(card_path)])

#endregion

#region ==================== 道具系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command("签到商店", alias={'签到商城'})
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def shop(self, event: AstrMessageEvent):
        """显示签到商店"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        shop_text = "🛒 签到商店 🛒\n\n"
        for item, details in SHOP_ITEMS.items():
            shop_text += f"【{item}】\n"
            shop_text += f"- 价格: {details['price']}金币\n"
            shop_text += f"- 描述: {details['description']}\n"
            shop_text += f"- 购买命令: /签到商店购买 {item} [数量]\n\n"
        
        shop_text += "🎒 查看背包: /签到背包"
        
        # 生成所有图片
        image_paths = await self.text_to_images(
            text=shop_text,
            title="签到商店"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)

    @filter.command("签到商店购买",alias={'签到商城购买'})
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def buy_item(self, event: AstrMessageEvent):
        """购买商店道具"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.chain_result([Plain(text="❌ 格式错误，请使用: /签到商店购买 道具名 [数量] 哦~大笨蛋杂鱼酱❤~")])
            return
        
        item_name = parts[1]
        quantity = 1
        if len(parts) >= 3:
            try:
                quantity = int(parts[2])
                if quantity <= 0:
                    yield event.chain_result([Plain(text="❌ 购买数量必须大于0哦~杂鱼酱❤~")])
                    return
            except ValueError:
                yield event.chain_result([Plain(text="❌ 无效的数量哦~杂鱼酱❤~")])
                return
        
        if item_name not in SHOP_ITEMS:
            yield event.chain_result([Plain(text=f"❌ 未知道具: {item_name}")])
            return
        
        item_info = SHOP_ITEMS[item_name]
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        total_cost = item_info["price"] * quantity
        
        # 检查金币是否足够
        if user_data["coins"] < total_cost:
            yield event.chain_result([Plain(
                text=f"❌ 金币不足! 需要 {total_cost} 金币, 当前金币: {user_data['coins']:.1f}，穷鬼杂鱼酱❤~"
            )])
            return
        
        # 扣除金币
        user_data["coins"] -= total_cost
        
        # 更新道具数量
        user_props = self._get_user_props(group_id, user_id)
        current_count = user_props.get(item_name, 0)
        user_props[item_name] = current_count + quantity
        self._update_user_props(group_id, user_id, user_props)
        
        # 保存数据
        try:
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"购买道具: group={group_id}, user={user_id}, "
                f"item={item_name}, quantity={quantity}, cost={total_cost}"
            )
        except Exception as e:
            self._log_operation("error", f"购买道具保存数据失败: {str(e)}")
            return
        
        yield event.chain_result([Plain(
            text=f"🎒 杂鱼酱❤~购买成功了呢! 获得 {quantity} 个 {item_name}\n"
                 f"- 花费: {total_cost} 金币\n"
                 f"- 当前拥有: {user_props[item_name]} 个\n"
                 f"- 使用命令: /道具 <使用|赠送> {item_info['command']} [@目标]"
        )])

    @filter.command("签到背包")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def backpack(self, event: AstrMessageEvent):
        """查看用户背包"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_props = self._get_user_props(group_id, user_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        if not user_props:
            yield event.chain_result([Plain(text="🎒 您的背包空空如也")])
            return
        
        prop_text = "🎒 背包物品:\n\n"
        for item, quantity in user_props.items():
            if item in SHOP_ITEMS:
                prop_text += f"- {item}: {quantity} 个\n"
                prop_text += f"  使用命令: /道具 <使用|赠送> {SHOP_ITEMS[item]['command']} [@目标]\n"
        
        yield event.chain_result([Plain(text=prop_text)])

    @filter.command("道具")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def use_prop(self, event: AstrMessageEvent):
        """使用道具"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用: /道具 <使用|赠送> <道具名> [@目标] 哦~大笨蛋杂鱼酱❤~")
            return
        
        action = parts[1]
        if action not in ["使用", "赠送"]:
            yield event.plain_result("❌ 无效操作，可用操作: 使用, 赠送")
            return
        
        if len(parts) < 3:
            yield event.plain_result("❌ 请指定道具名哦~大笨蛋杂鱼酱❤~")
            return
        
        prop_name = parts[2]
        if prop_name not in SHOP_ITEMS:
            yield event.plain_result(f"❌ 未知道具: {prop_name}")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取道具信息
        prop_info = SHOP_ITEMS[prop_name]
        
        # 检查道具类型
        if action == "使用" and prop_info["type"] != "use":
            yield event.plain_result(f"❌ {prop_name} 不能直接使用哦~大笨蛋杂鱼酱❤~")
            return
            
        if action == "赠送" and prop_info["type"] != "gift":
            yield event.plain_result(f"❌ {prop_name} 不能赠送哦~大笨蛋杂鱼酱❤~")
            return
        
        # 解析目标用户
        target_id = None
        if len(parts) >= 4:
            # 尝试解析@的目标
            target_id = self._parse_at_target(event)
        
        # 对于某些道具，目标用户是必需的
        if prop_name in ["驯服贴", "强制购买符", "市场侵袭"]:
            if not target_id:
                yield event.plain_result(f"❌ 请@要使用 {prop_name} 的目标哦~杂鱼酱❤~")
                return
        
        # 根据道具类型调用相应的处理函数
        if action == "使用":
            if prop_name == "驯服贴":
                async for result in self._use_tame_sticker(event, group_id, user_id, target_id):
                    yield result
            elif prop_name == "强制购买符":
                async for result in self._use_force_buy(event, group_id, user_id, target_id):
                    yield result
            elif prop_name == "自由身保险":
                async for result in self._use_freedom_insurance(event, group_id, user_id):
                    yield result
            elif prop_name == "红星制裁":
                async for result in self._use_red_star_sanction(event, group_id, user_id):
                    yield result
            elif prop_name == "市场侵袭":
                async for result in self._use_market_invasion(event, group_id, user_id, target_id):
                    yield result
            elif prop_name == "彩票":
                async for result in self._use_lottery(event, group_id, user_id):
                    yield result
            elif prop_name == "贿赂券":
                async for result in self._use_bribe(event, group_id, user_id):
                    yield result
            elif prop_name == "美式咖啡":
                async for result in self._use_american_coffee(event, group_id, user_id):
                    yield result
            else:
                yield event.plain_result(f"❌ 未实现的道具: {prop_name}")
        elif action == "赠送":
            if not target_id:
                yield event.plain_result(f"❌ 请@要赠送 {prop_name} 的对象哦~杂鱼酱❤~")
                return
            async for result in self._give_gift(event, group_id, user_id, target_id, prop_name):
                yield result

    #region 道具实现
    async def _use_tame_sticker(self, event, group_id, user_id, target_id):
        """使用驯服贴永久绑定性奴"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "驯服贴" not in user_props or user_props["驯服贴"] < 1:
            yield event.plain_result("❌ 您没有驯服贴哦~杂鱼酱❤~")
            return
        
        if user_id == target_id:
            yield "❌ 不能对自己使用驯服贴哦~大笨蛋杂鱼酱❤~"
            return

        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        target_data = self._get_user_data(group_id, target_id)
        
        # 检查目标是否已经是自己的性奴
        if target_id not in user_data["contractors"]:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 不是你的性奴哦~杂鱼酱❤~")
            return
        
        # 检查永久绑定数量限制
        permanent_contractors = user_data.get("permanent_contractors", [])
        current_count = len(permanent_contractors)
        extra_cost = 0
        
        # 如果已有3个永久性奴，计算额外费用
        if current_count >= 3:
            # 额外费用公式: 2000 * 2 * (当前数量 + 1)
            # 例如: 第4个永久性奴: 2000*2*4= 4000
            #       第5个永久性奴: 2000*2*5 = 8000
            extra_cost = 2000 * 2 * (current_count + 1)
            
            # 检查用户金币是否足够
            if user_data["coins"] < extra_cost:
                yield event.plain_result(
                    f"❌ 超出永久性奴数量限制，需要额外支付 {extra_cost} 金币\n"
                    f"当前永久性奴数量: {current_count}/3"
                )
                return
        
        # 检查目标是否已被永久绑定
        if target_id in permanent_contractors:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 已被永久绑定了哦~杂鱼酱❤~")
            return
        
        # 添加永久绑定
        permanent_contractors.append(target_id)
        user_data["permanent_contractors"] = permanent_contractors
        
        # 标记目标已被永久绑定
        target_data["is_permanent"] = True
        
        # 扣除道具
        user_props["驯服贴"] -= 1
        if user_props["驯服贴"] <= 0:
            del user_props["驯服贴"]
        
        # 扣除额外费用（如果有）
        if extra_cost > 0:
            user_data["coins"] -= extra_cost
        
        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)
            
            # 保存用户数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            group_data[target_id] = target_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"使用驯服贴: group={group_id}, user={user_id}, "
                f"target={target_id}, extra_cost={extra_cost}"
            )
        except Exception as e:
            self._log_operation("error", f"驯服贴保存数据失败: {str(e)}")
        
        target_name = await self._get_at_user_name(event, target_id)
        result = f"✅ 杂鱼酱❤~成功永久绑定 {target_name}！\n"
        result += f"- 该性奴不会被制裁、赎身或强制购买\n"
        result += f"- 剩余驯服贴: {user_props.get('驯服贴', 0)}"
        
        if extra_cost > 0:
            result += f"\n⚠️ 超出数量限制，额外扣除 {extra_cost} 金币"
            
        yield event.plain_result(result)

    async def _use_force_buy(self, event, group_id, user_id, target_id):
        """使用强制购买符购买已有主人的性奴"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "强制购买符" not in user_props or user_props["强制购买符"] < 1:
            yield event.plain_result("❌ 您没有强制购买符哦~杂鱼酱❤~")
            return
        
        if user_id == target_id:
            yield "❌ 不能对自己使用强制购买符哦~大笨蛋杂鱼酱❤~"
            return

        # 获取用户数据
        employer_data = self._get_user_data(group_id, user_id)
        target_data = self._get_user_data(group_id, target_id)
        
        # 检查目标是否已被永久绑定
        if target_data.get("is_permanent", False):
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 已被永久绑定，无法强制购买哦~杂鱼酱❤~")
            return
        
        if employer_data.get("contracted_by") == target_id:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ 你不能购买自己的主人 {target_name}哦~杂鱼酱❤~")
            return
        
        # 检查目标是否有主人
        if not target_data["contracted_by"]:
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 没有主人，请直接购买哦~杂鱼酱❤~")
            return
        
        # 计算目标身价
        cost = self._calculate_wealth(target_data)
        
        # 检查金币是否足够
        if employer_data["coins"] < cost:
            yield event.plain_result(f"❌ 需要支付目标身价：{cost}金币哦~穷鬼杂鱼酱❤~")
            return
        
        # 获取原主人数据
        original_owner_id = target_data["contracted_by"]
        original_owner_data = self._get_user_data(group_id, original_owner_id)
        
        # 更新契约关系
        # 从原主人移除
        if target_id in original_owner_data["contractors"]:
            original_owner_data["contractors"].remove(target_id)
        
        # 添加到新主人
        employer_data["contractors"].append(target_id)
        target_data["contracted_by"] = user_id
        
        # 处理金币
        employer_data["coins"] -= cost  # 新主人支付身价
        original_owner_data["coins"] += cost  # 原主人获得补偿
        
        # 扣除道具
        user_props["强制购买符"] -= 1
        if user_props["强制购买符"] <= 0:
            del user_props["强制购买符"]
        
        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)
            
            # 保存用户数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = employer_data
            group_data[target_id] = target_data
            group_data[original_owner_id] = original_owner_data
            self._save_data(data)
            
            # 记录日志
            self._log_operation("info", 
                f"强制购买: group={group_id}, buyer={user_id}, "
                f"target={target_id}, original_owner={original_owner_id}, "
                f"cost={cost}"
            )
        except Exception as e:
            self._log_operation("error", f"强制购买保存数据失败: {str(e)}")
        
        target_name = await self._get_at_user_name(event, target_id)
        new_owner_name = event.get_sender_name()
        original_owner_name = await self._get_at_user_name(event, original_owner_id)
        
        yield event.plain_result(f"⚡ 强制购买成功! {new_owner_name} 从 {original_owner_name} 处抢走了 {target_name}\n"
                                 f"- 支付身价: {cost}金币\n"
                                 f"- 剩余强制购买符: {user_props.get('强制购买', 0)}")

    async def _use_freedom_insurance(self, event, group_id, user_id):
        """使用自由身保险"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "自由身保险" not in user_props or user_props["自由身保险"] < 1:
            yield event.plain_result("❌ 您没有自由身保险哦~杂鱼酱❤~")
            return
        
        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        time_data = self._get_user_time_data(group_id, user_id)
        
        # 新增：检查用户是否是性奴（有主人）
        if user_data["contracted_by"] is not None:
            yield event.plain_result("❌ 您已是性奴，不能使用自由身保险哦~性奴杂鱼酱❤~")
            return
        
        # 检查是否已有保险
        insurance_until = time_data.get("free_insurance_until")
        if insurance_until:
            insurance_time = SHANGHAI_TZ.localize(datetime.fromisoformat(insurance_until))
            if insurance_time > datetime.now(SHANGHAI_TZ):
                remaining = insurance_time - datetime.now(SHANGHAI_TZ)
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                yield event.plain_result(f"❌ 您已有自由身保险，剩余时间: {hours}小时{minutes}分钟")
                return
        
        # 设置保险到期时间
        duration = SHOP_ITEMS["自由身保险"]["duration_hours"]
        expire_time = datetime.now(SHANGHAI_TZ) + timedelta(hours=duration)
        time_data["free_insurance_until"] = expire_time.replace(tzinfo=None).isoformat()
        
        # 扣除道具
        user_props["自由身保险"] -= 1
        if user_props["自由身保险"] <= 0:
            del user_props["自由身保险"]
        
        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)
            
            # 保存时间数据
            self._save_user_time_data(group_id, user_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"使用自由身保险: group={group_id}, user={user_id}, "
                f"expire={expire_time}"
            )
        except Exception as e:
            self._log_operation("error", f"自由身保险保存数据失败: {str(e)}")
        
        expire_str = expire_time.strftime("%Y-%m-%d %H:%M")
        yield event.plain_result(f"🛡️ 自由身保险已激活! 有效期至: {expire_str}\n"
                                 f"- 在此期间您不会被购买为性奴\n"
                                 f"- 剩余自由身保险: {user_props.get('自由身保险', 0)}")
    
    async def _use_red_star_sanction(self, event, group_id, user_id):
        """使用红星制裁道具"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "红星制裁" not in user_props or user_props["红星制裁"] < 1:
            yield event.plain_result("❌ 您没有红星制裁道具哦~杂鱼酱❤~")
            return

        # 获取用户数据和时间数据
        user_data = self._get_user_data(group_id, user_id)
        time_data = self._get_user_time_data(group_id, user_id)
        
        # 检查使用者是否符合条件（不满足制裁条件）
        total_assets = user_data["coins"] + user_data["bank"] + user_data.get("niuniu_coins", 0.0)
        contractor_count = len(user_data["contractors"])

        # 检查使用者是否满足制裁条件
        if total_assets > 3000 or contractor_count > 6:
            yield event.plain_result("❌ 您自身已满足制裁条件，无法使用红星制裁哦~杂鱼酱❤~")
            return

        # 检查冷却时间（每天限用一次）
        now = datetime.now(SHANGHAI_TZ)
        last_use_key = "last_red_star_use"
        if time_data.get(last_use_key):
            last_use = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data[last_use_key]))
            if last_use.date() == now.date():
                yield event.plain_result("❌ 今天已使用过红星制裁，请明天再来哦~杂鱼酱❤~")
                return

        # 加载全群数据
        data = self._load_data()

        group_data = data.get(group_id, {})
        if not group_data:
            yield event.plain_result("❌ 群组数据为空")
            return

        # 对每个满足条件的用户进行制裁
        sanction_results = []
        for uid, u_data in group_data.items():
            # 跳过使用者自己
            if uid == user_id:
                continue
    
            # 计算用户总资产和性奴数量
            u_total_assets = u_data["coins"] + u_data["bank"] + u_data.get("niuniu_coins", 0.0)
            u_contractor_count = len(u_data["contractors"])

            # 检查是否满足制裁条件
            if u_total_assets > 3000 or u_contractor_count > 6:
                # 检查目标是否有贿赂券
                target_props = self._get_user_props(group_id, uid)
                if "贿赂券" in target_props and target_props["贿赂券"] > 0 and random.random() < 0.90:
                    # 使用贿赂券免疫制裁
                    target_props["贿赂券"] -= 1
                    if target_props["贿赂券"] <= 0:
                        del target_props["贿赂券"]
                    self._update_user_props(group_id, uid, target_props)
                    
                    try:
                        user_name = await self._get_at_user_name(event, uid)
                        sanction_results.append(f"🛡️ {user_name} 使用了贿赂券，免疫了红星制裁！")
                    except:
                        sanction_results.append(f"🛡️ 用户{uid[-4:]} 使用了贿赂券，免疫了红星制裁！")
                    continue
                
                # 75%概率触发制裁
                if random.random() < 0.75:
                    # 性奴制裁（非永久绑定的）
                    escape_results = []
                    escaped_slaves = []  # 存储逃走的性奴信息
                    if u_contractor_count > 0:
                        # 只处理非永久绑定的性奴
                        non_permanent = []
                        for cid in u_data["contractors"]:
                            slave_data = self._get_user_data(group_id, cid)
                            if not slave_data.get("is_permanent", False):
                                non_permanent.append(cid)
            
                        if non_permanent:
                            # 随机选择1-5个非永久性奴出逃
                            num_escape = random.randint(1, min(5, len(non_permanent)))
                            escaped_ids = random.sample(non_permanent, num_escape)
                
                            # 更新用户数据
                            for cid in escaped_ids:
                                if cid in u_data["contractors"]:
                                    u_data["contractors"].remove(cid)
                        
                            # 更新性奴数据 - 确保contracted_by被清除
                            for cid in escaped_ids:
                                slave_data = self._get_user_data(group_id, cid)
                                slave_data["contracted_by"] = None  # 关键修复：解除契约关系
                                # 保存性奴数据
                                group_data[cid] = slave_data
                
                            # 获取逃走的性奴名字
                            for cid in escaped_ids:
                                try:
                                    slave_name = await self._get_at_user_name(event, cid)
                                    escaped_slaves.append(slave_name)
                                except:
                                    escaped_slaves.append(f"用户{cid[-4:]}")
            
                    # 资产制裁
                    asset_results = []
                    if u_total_assets > 0:
                        # 随机损失10%-50%的总资产
                        loss_percent = random.uniform(0.1, 0.5)
                        loss_amount = u_total_assets * loss_percent
            
                        # 从现金中扣除，不够则从银行扣
                        if u_data["coins"] >= loss_amount:
                            u_data["coins"] -= loss_amount
                        else:
                            remaining = loss_amount - u_data["coins"]
                            u_data["coins"] = 0
                            u_data["bank"] = max(0, u_data["bank"] - remaining)
            
                    asset_results.append(f"资产损失: {loss_amount:.1f}金币({loss_percent*100:.0f}%)")
        
                    # 记录制裁结果 - 详细显示性奴丢失信息
                    try:
                        user_name = await self._get_at_user_name(event, uid)
                        sanction_entry = f"👉 群友 {user_name} 被制裁:"
                
                        # 如果有性奴逃跑，详细显示
                        if escaped_slaves:
                            sanction_entry += f"\n  - 丢失性奴 {len(escaped_slaves)} 名: {', '.join(escaped_slaves)}"
                
                        # 如果有资产损失
                        if asset_results:
                            sanction_entry += f"\n  - {asset_results[0]}"
                
                        sanction_results.append(sanction_entry)
                    except:
                        sanction_entry = f"👉 用户{uid[-4:]} 被制裁:"
                        if escaped_slaves:
                            sanction_entry += f"\n  - 丢失性奴 {len(escaped_slaves)} 名"
                        if asset_results:
                            sanction_entry += f"\n  - {asset_results[0]}"
                        sanction_results.append(sanction_entry)

        # 如果没有触发任何制裁
        if not sanction_results:
            sanction_results.append("本次制裁未影响任何用户")

        # 更新使用者数据
        time_data[last_use_key] = now.replace(tzinfo=None).isoformat()

        # 扣除道具
        user_props["红星制裁"] -= 1
        if user_props["红星制裁"] <= 0:
            del user_props["红星制裁"]

        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)

            # 保存用户数据
            self._save_data(data)
                
            # 保存时间数据
            self._save_user_time_data(group_id, user_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"使用红星制裁: group={group_id}, user={user_id}, "
                f"results={len(sanction_results)-1}"  # 减去未影响任何用户的条目
            )
        except Exception as e:
            self._log_operation("error", f"红星制裁保存数据失败: {str(e)}")

        # 构建响应消息
        response = "✨ 来自共和国的力量降临了。。。\n"
        response += f"📢 对全群进行了红星制裁！\n\n"
        response += "\n".join(sanction_results)

        yield event.plain_result(response)

    async def _use_market_invasion(self, event, group_id, user_id, target_id):
        """使用市场侵袭道具"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "市场侵袭" not in user_props or user_props["市场侵袭"] < 1:
            yield event.plain_result("❌ 您没有市场侵袭道具哦~杂鱼酱❤~")
            return

        if user_id == target_id:
            yield "❌ 不能对自己使用市场侵袭哦~大笨蛋杂鱼酱❤~"
            return

        # 获取用户数据和时间数据
        user_data = self._get_user_data(group_id, user_id)
        time_data = self._get_user_time_data(group_id, user_id)

        # 检查冷却时间（每小时限用一次）
        now = datetime.now(SHANGHAI_TZ)
        last_use_key = "last_market_invasion_use"
        if time_data.get(last_use_key):
            last_use = SHANGHAI_TZ.localize(datetime.fromisoformat(time_data[last_use_key]))
            if (now - last_use) < timedelta(hours=1):
                remaining_minutes = 60 - int((now - last_use).total_seconds() / 60)
                yield event.plain_result(f"❌ 市场侵袭太频繁，请等待{remaining_minutes}分钟后再试")
                return

        # 获取目标用户数据
        target_data = self._get_user_data(group_id, target_id)

        # 检查双方是否符合条件
        user_total_assets = user_data["coins"] + user_data["bank"] + user_data.get("niuniu_coins", 0.0)
        user_contractor_count = len(user_data["contractors"])

        target_total_assets = target_data["coins"] + target_data["bank"] + target_data.get("niuniu_coins", 0.0)
        target_contractor_count = len(target_data["contractors"])

        if not ((user_total_assets > 2000 or user_contractor_count > 5) and 
                (target_total_assets > 2000 or target_contractor_count > 5)):
            yield event.plain_result("❌ 双方必须都满足条件（总资产>2000或性奴>5）")
            return

        # 随机决定胜负（60%发起方胜，40%目标方胜）
        user_wins = random.random() < 0.60

        # 初始化结果变量
        user_gain = 0
        user_slaves_gained = []
        target_loss = 0
        target_slaves_lost = []

        # 计算目标损失（10%-30%资产）
        target_loss_percent = random.uniform(0.1, 0.3)
        target_loss_amount = target_total_assets * target_loss_percent

        # 加载群组数据
        data = self._load_data()
        group_data = data.setdefault(group_id, {})
        group_data[user_id] = user_data
        group_data[target_id] = target_data

        # 处理资产转移
        if user_wins:
            # 发起方获胜
            # 从目标扣除资产
            if target_data["coins"] >= target_loss_amount:
                target_data["coins"] -= target_loss_amount
            else:
                remaining = target_loss_amount - target_data["coins"]
                target_data["coins"] = 0
                target_data["bank"] = max(0, target_data["bank"] - remaining)

            # 给发起方增加资产
            user_data["coins"] += target_loss_amount
            user_gain = target_loss_amount
            target_loss = target_loss_amount

            # 处理性奴转移（最多3个）
            if target_data["contractors"]:
                # 只处理非永久绑定的性奴
                transferable = []
                for cid in target_data["contractors"]:
                    slave_data = self._get_user_data(group_id, cid)
                    if not slave_data.get("is_permanent", False):
                        transferable.append(cid)
    
                if transferable:
                    num_transfer = min(3, len(transferable))
                    transfer_ids = random.sample(transferable, num_transfer)
        
                    # 转移性奴
                    for cid in transfer_ids:
                        # 从目标移除
                        if cid in target_data["contractors"]:
                            target_data["contractors"].remove(cid)
            
                        # 添加到发起方
                        if cid not in user_data["contractors"]:
                            user_data["contractors"].append(cid)
            
                        # ==== 修复：正确更新性奴的主人信息 ====
                        # 获取性奴数据
                        slave_data = self._get_user_data(group_id, cid)
                        # 更新主人信息
                        slave_data["contracted_by"] = user_id
                        # 保存到待更新数据中
                        group_data[cid] = slave_data
            
                        try:
                            slave_name = await self._get_at_user_name(event, cid)
                            target_slaves_lost.append(slave_name)
                            user_slaves_gained.append(slave_name)
                        except:
                            target_slaves_lost.append(f"用户{cid[-4:]}")
                            user_slaves_gained.append(f"用户{cid[-4:]}")
        else:
            # 目标方获胜
            # 从发起方扣除资产（惩罚更多）
            user_loss_percent = random.uniform(0.15, 0.35)
            user_loss_amount = user_total_assets * user_loss_percent

            if user_data["coins"] >= user_loss_amount:
                user_data["coins"] -= user_loss_amount
            else:
                remaining = user_loss_amount - user_data["coins"]
                user_data["coins"] = 0
                user_data["bank"] = max(0, user_data["bank"] - remaining)

            # 给目标方增加资产
            target_data["coins"] += user_loss_amount
            user_gain = -user_loss_amount
            target_loss = -user_loss_amount  # 负值表示目标方获利

            # 处理性奴转移（发起方失去性奴）
            if user_data["contractors"]:
                # 只处理非永久绑定的性奴
                transferable = []
                for cid in user_data["contractors"]:
                    slave_data = self._get_user_data(group_id, cid)
                    if not slave_data.get("is_permanent", False):
                        transferable.append(cid)
    
                if transferable:
                    num_transfer = min(3, len(transferable))
                    transfer_ids = random.sample(transferable, num_transfer)
        
                    # 转移性奴
                    for cid in transfer_ids:
                        # 从发起方移除
                        if cid in user_data["contractors"]:
                            user_data["contractors"].remove(cid)
            
                        # 添加到目标方
                        if cid not in target_data["contractors"]:
                            target_data["contractors"].append(cid)
            
                        # ==== 修复：正确更新性奴的主人信息 ====
                        # 获取性奴数据
                        slave_data = self._get_user_data(group_id, cid)
                        # 更新主人信息
                        slave_data["contracted_by"] = target_id
                        # 保存到待更新数据中
                        group_data[cid] = slave_data
            
                        try:
                            slave_name = await self._get_at_user_name(event, cid)
                            user_slaves_gained.append(slave_name)  # 这里表示发起方失去的性奴
                            target_slaves_lost.append(slave_name)  # 目标方获得的性奴
                        except:
                            user_slaves_gained.append(f"用户{cid[-4:]}")
                            target_slaves_lost.append(f"用户{cid[-4:]}")

        # 更新使用者冷却时间
        time_data[last_use_key] = now.replace(tzinfo=None).isoformat()

        # 扣除道具
        user_props["市场侵袭"] -= 1
        if user_props["市场侵袭"] <= 0:
            del user_props["市场侵袭"]

        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)

            # 保存用户数据
            self._save_data(data)
                
            # 保存时间数据
            self._save_user_time_data(group_id, user_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"市场侵袭: group={group_id}, attacker={user_id}, "
                f"target={target_id}, result={'win' if user_wins else 'lose'}"
            )
        except Exception as e:
            self._log_operation("error", f"市场侵袭保存数据失败: {str(e)}")

        # 获取用户名
        user_name = event.get_sender_name()
        target_name = await self._get_at_user_name(event, target_id)

        # 构建响应消息
        response = "⚔️ 市场侵袭结果:\n\n"

        if user_wins:
            response += f"🏆 在资本的斗争中 {user_name} 战胜了 {target_name}！\n"
            response += f"- 掠夺资产: {user_gain:.1f}金币\n"
            if user_slaves_gained:
                response += f"- 获得性奴 {len(user_slaves_gained)}名: {', '.join(user_slaves_gained)}\n"
            else:
                response += "- 没有获得性奴\n"
        else:
            response += f"💥 在资本的斗争中 {target_name} 抵御了 {user_name} 的侵袭！\n"
            response += f"- 损失资产: {-user_gain:.1f}金币\n"
            if user_slaves_gained:
                response += f"- 失去性奴 {len(user_slaves_gained)}名: {', '.join(user_slaves_gained)}\n"
            else:
                response += "- 没有失去性奴\n"

        response += f"\n💼 {user_name} 当前资产: {user_data['coins'] + user_data['bank']:.1f}金币"
        response += f"\n💼 {target_name} 当前资产: {target_data['coins'] + target_data['bank']:.1f}金币"

        yield event.plain_result(response)

    async def _use_lottery(self, event, group_id, user_id):
        """使用彩票道具"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        
        # 检查彩票数量
        if "彩票" not in user_props or user_props["彩票"] < 1:
            yield event.plain_result("❌ 您没有彩票哦~杂鱼酱❤~")
            return
        
        # 获取时间数据
        time_data = self._get_user_time_data(group_id, user_id)
        now = datetime.now(SHANGHAI_TZ)
        today = now.date()
    
        # 检查是否是新的自然日
        if time_data.get("last_lottery_date") != today.isoformat():
            time_data["lottery_count"] = 0
            time_data["last_lottery_date"] = today.isoformat()
    
        # 检查每日使用次数限制（使用配置值）
        if time_data.get("lottery_count", 0) >= self.MAX_LOTTERY_PER_DAY:
            yield event.plain_result(f"❌ 今天已经使用了{self.MAX_LOTTERY_PER_DAY}次彩票，请明天再来哦~杂鱼酱❤~")
            return
        
        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        
        # 检查性奴数量限制（使用配置值）
        if len(user_data["contractors"]) >= self.MAX_CONTRACTORS_FOR_LOTTERY:
            yield event.chain_result([Plain(text="❌ 拥有3个或以上性奴的用户禁止使用彩票哦~杂鱼酱❤~")])
            return
    
        # 计算总资产（现金+银行+牛牛金币）
        total_assets = user_data["coins"] + user_data["bank"] + user_data.get("niuniu_coins", 0.0)
    
        # 检查总资产限制（使用配置值）
        if total_assets > self.MAX_ASSETS_FOR_LOTTERY:
            yield event.chain_result([Plain(text=f"❌ 总资产超过{self.MAX_ASSETS_FOR_LOTTERY}金币，禁止使用彩票哦~杂鱼酱❤~")])
            return

        # 执行彩票开奖（使用配置值）
        is_win = random.random() < self.LOTTERY_WIN_RATE
        
        if is_win:
            # 中奖，随机生成奖金金额（使用配置范围）
            prize = random.randint(self.LOTTERY_MIN_PRIZE, self.LOTTERY_MAX_PRIZE)
            user_data["coins"] += prize
            result_msg = f"🎉 恭喜中奖！获得 {prize} 金币！"
        else:
            result_msg = "😢 很遗憾，没有中奖"
        
        # 更新彩票计数
        time_data["lottery_count"] = time_data.get("lottery_count", 0) + 1
        
        # 扣除道具
        user_props["彩票"] -= 1
        if user_props["彩票"] <= 0:
            del user_props["彩票"]
        
        # 保存数据
        try:
            # 保存道具数据
            self._update_user_props(group_id, user_id, user_props)
            
            # 保存主数据
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
            
            # 保存时间数据
            self._save_user_time_data(group_id, user_id, time_data)
            
            # 记录日志
            self._log_operation("info", 
                f"使用彩票: group={group_id}, user={user_id}, "
                f"prize={prize if is_win else 0}"
            )
        except Exception as e:
            self._log_operation("error", f"彩票保存数据失败: {str(e)}")
    
        yield event.plain_result(f"✅ 使用彩票成功\n{result_msg}\n今日剩余彩票次数: {self.MAX_LOTTERY_PER_DAY - time_data['lottery_count']}")

    async def _use_bribe(self, event, group_id, user_id):
        """使用贿赂券（不需要目标）"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if "贿赂券" not in user_props or user_props["贿赂券"] < 1:
            yield event.plain_result("❌ 您没有贿赂券")
            return
        
        # 只是提示，实际使用在红星制裁中处理
        yield event.plain_result("🛡️ 贿赂券已准备就绪！当您成为红星制裁目标时，有75%概率自动使用并免疫制裁")

    async def _give_gift(self, event, group_id, user_id, target_id, gift_name):
        """赠送礼物增加好感度（新增关系加成）"""
        # 获取用户道具
        user_props = self._get_user_props(group_id, user_id)
        if gift_name not in user_props or user_props[gift_name] < 1:
            yield event.plain_result(f"❌ 您没有{gift_name}，请先在商店购买哦~杂鱼酱❤~")
            return
        
        if user_id == target_id:
            yield "❌ 不能对自己赠送礼物哦~大笨蛋杂鱼酱❤~"
            return

        # 获取关系类型
        relation_type = self.get_special_relation(group_id, user_id, target_id)
        
        # 确定好感度增加值（根据关系类型）
        min_gain, max_gain = 5, 10
        if relation_type:
            gift_bonus = RELATION_GIFT_BONUS.get(relation_type, {}).get(gift_name)
            if gift_bonus:
                min_gain, max_gain = gift_bonus
        
        favorability_gain = random.randint(min_gain, max_gain)
        
        # 更新好感度
        new_favorability = self._update_favorability(group_id, target_id, user_id, favorability_gain)
        
        # 扣除道具
        user_props[gift_name] -= 1
        if user_props[gift_name] <= 0:
            del user_props[gift_name]
        self._update_user_props(group_id, user_id, user_props)
        
        # 记录日志
        self._log_operation("info", 
            f"赠送礼物: group={group_id}, from={user_id}, "
            f"to={target_id}, gift={gift_name}, "
            f"favorability_gain={favorability_gain}"
        )
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"🎁 你向 {target_name} 赠送了{gift_name}，TA对你的好感度增加了{favorability_gain}点！\n当前好感度: {new_favorability}")

    async def _use_american_coffee(self, event, group_id, user_id):
        """使用美式咖啡道具减少约会计数"""
        user_props = self._get_user_props(group_id, user_id)
        if "美式咖啡" not in user_props or user_props["美式咖啡"] < 1:
            yield event.plain_result("❌ 您没有美式咖啡")
            return
        # 获取用户社交数据
        user_data = self._get_user_social_data(group_id, user_id)
        today = datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")
        
        # 检查是否需要刷新约会计数
        if user_data["last_date_date"] != today:
            user_data["daily_date_count"] = 0
            user_data["last_date_date"] = today
        

        if user_data["daily_date_count"] <= 0:
            yield event.plain_result("❌ 现在你精力满满，无法使用美式咖啡哦~杂鱼酱❤~")
            return
        else:
            user_data["daily_date_count"] -= 1
        
        social_data = self._load_social_data()
        social_data.setdefault(group_id, {})[user_id] = user_data
        self._save_social_data(social_data)
        
        user_props["美式咖啡"] -= 1
        if user_props["美式咖啡"] <= 0:
            del user_props["美式咖啡"]

        self._update_user_props(group_id, user_id, user_props)

        yield event.plain_result("☕ 使用美式咖啡成功！今日约会次数增加1次")
        return
    #endregion
#endregion

#region ==================== 社交系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    #region 约会事件
    @filter.command("约会")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def invite_date(self, event: AstrMessageEvent):
        """发起约会邀请（修改：约会计数在对方同意后增加）"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要约会的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 检查是否是自己
        if user_id == target_id:
            yield event.plain_result("❌ 不能和自己约会哦~杂鱼酱❤~")
            return
        
        # 检查是否是机器人
        if target_id == event.get_self_id():
            yield event.plain_result("抱歉，我现在很忙，没有时间约会哦~杂鱼酱❤~")
            return
        
        # 获取用户数据
        user_data = self._get_user_social_data(group_id, user_id)
        today = datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")
        
        # 检查每日约会次数（但不立即增加计数）
        if user_data["last_date_date"] != today:
            user_data["daily_date_count"] = 0
            user_data["last_date_date"] = today
        
        if user_data["daily_date_count"] >= 10:
            yield event.plain_result("你今天已经约会10次了，请明天再来哦~杂鱼酱❤~")
            return
        
        # 生成唯一验证码
        confirmation_code = self._generate_unique_code(group_id, target_id)
        
        # 存储约会邀请
        group_id_str = str(group_id)
        if group_id_str not in self.date_confirmations:
            self.date_confirmations[group_id_str] = {}
        
        self.date_confirmations[group_id_str][target_id] = {
            "initiator_id": user_id,
            "confirmation_code": confirmation_code,
            "created_at": datetime.now(SHANGHAI_TZ),
            "status": "pending"
        }
        
        # 保存数据（不增加约会次数）
        social_data = self._load_social_data()
        social_data.setdefault(group_id_str, {})[user_id] = user_data
        self._save_social_data(social_data)
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(
            f"✅ 已向 {target_name} 发送约会邀请，等待对方回应...\n"
            f"🔑 验证码: {confirmation_code} \n"
            f"💖 请 {target_name} 使用/同意约会 {confirmation_code} 以同意约会请求"
        )

    def _generate_unique_code(self, group_id: str, target_id: str) -> str:
        """生成唯一的验证码（确保在群组内目标用户唯一）"""
        group_id_str = str(group_id)
        
        # 生成随机验证码
        code = str(random.randint(1000, 9999))
        
        # 检查是否已存在（概率很低但可能发生）
        if (group_id_str in self.date_confirmations and 
            target_id in self.date_confirmations[group_id_str] and
            code in self.date_confirmations[group_id_str][target_id]):
            # 如果已存在，递归生成新码
            return self._generate_unique_code(group_id, target_id)
        
        return code

    @filter.command("同意约会")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def accept_date(self, event: AstrMessageEvent):
        """同意约会邀请（增加发起方约会计数）"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/同意约会 <验证码>")
            return
        
        confirmation_code = parts[1]
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        group_id_str = str(group_id)
        
        # 获取约会邀请
        if (group_id_str not in self.date_confirmations or 
            user_id not in self.date_confirmations[group_id_str]):
            yield event.plain_result("❌ 没有待处理的约会邀请哦~杂鱼酱❤~")
            return
        
        invitation = self.date_confirmations[group_id_str][user_id]
        
        # 检查邀请是否过期
        if datetime.now(SHANGHAI_TZ) - invitation['created_at'] > timedelta(minutes=5):
            del self.date_confirmations[group_id_str][user_id]
            yield event.plain_result("❌ 约会邀请已过期了~你来晚了路明非~你还是那个没人要的臭小孩~")
            return
        
        # 检查验证码是否匹配
        if confirmation_code != invitation["confirmation_code"]:
            yield event.plain_result(f"❌ 验证码错误！请向发起者确认正确的验证码")
            return
        
        # 标记为已确认
        invitation["status"] = "confirmed"
        
        # 执行约会
        initiator_id = invitation["initiator_id"]
        initiator_name = await self._get_at_user_name(event, initiator_id)
        user_name = event.get_sender_name()
        
        # 运行约会流程
        result = await self._run_date(group_id, initiator_id, user_id, initiator_name, user_name)
        
        # 删除邀请
        del self.date_confirmations[group_id_str][user_id]
        
        # 增加发起方的约会计数（只有在对方同意后才增加）
        initiator_data = self._get_user_social_data(group_id, initiator_id)
        initiator_data["daily_date_count"] += 1
        
        # 保存数据
        social_data = self._load_social_data()
        social_data.setdefault(group_id_str, {})[initiator_id] = initiator_data
        self._save_social_data(social_data)
        
        # 构建响应消息
        response = f"💖 {initiator_name} 和 {user_name} 的约会结果：\n\n"
        for event_info in result["events"]:
            response += f"【{event_info['name']}】\n{event_info['description']}\n\n"
        
        response += f"✨ {initiator_name} 对 {user_name} 的好感度变化: +{result['user_a_to_b_change']}\n"
        response += f"✨ {user_name} 对 {initiator_name} 的好感度变化: +{result['user_b_to_a_change']}\n\n"
        
        if result["user_a_to_b_level_up"]:
            response += f"🎉 {initiator_name} 对 {user_name} 的关系提升为: {result['user_a_to_b_level_after']}\n"
        if result["user_b_to_a_level_up"]:
            response += f"🎉 {user_name} 对 {initiator_name} 的关系提升为: {result['user_b_to_a_level_after']}\n"
        
        yield event.plain_result(response)

    @filter.command("我的约会邀请")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def list_my_invitations(self, event: AstrMessageEvent):
        """查看我的约会邀请列表"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        group_id_str = str(group_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 获取我的邀请
        if (group_id_str not in self.date_confirmations or 
            user_id not in self.date_confirmations[group_id_str]):
            yield event.plain_result("❌ 你目前没有待处理的约会邀请哦~杂鱼酱❤~")
            return
        
        invitations = self.date_confirmations[group_id_str][user_id]
        
        # 构建响应消息
        response = "💌 你的约会邀请列表：\n\n"
        for code, invite in invitations.items():
            initiator_id = invite["initiator_id"]
            initiator_name = await self._get_at_user_name(event, initiator_id)
            created_time = invite["created_at"].strftime("%H:%M")
            remaining_minutes = max(0, 5 - int((datetime.now(SHANGHAI_TZ) - invite["created_at"]).total_seconds() / 60))
            
            response += (
                f"🔑 验证码: {code}\n"
                f"发起者: {initiator_name}\n"
                f"时间: {created_time} (剩余{remaining_minutes}分钟)\n"
                f"----------------\n"
            )
        
        response += "\n使用 /同意约会 <验证码> 来接受邀请"
        yield event.plain_result(response)

    async def _run_date(self, group_id: str, user_a_id: str, user_b_id: str, user_a_name: str, user_b_name: str) -> dict:
        """执行约会流程（添加500点好感度限制）"""
        # 初始化事件结果列表
        events_result = []
    
        # 检查双方是否已有特殊关系
        has_relation = bool(self.get_special_relation(group_id, user_a_id, user_b_id))

        # 记录开始时的好感度
        a_to_b_before = self.get_favorability(group_id, user_a_id, user_b_id)
        b_to_a_before = self.get_favorability(group_id, user_b_id, user_a_id)

        # 随机选择3个事件
        event_count = min(3, len(DATE_EVENTS))
        selected_events = random.sample(DATE_EVENTS, event_count)

        # 累计好感度变化
        a_to_b_change = 0
        b_to_a_change = 0

        # 处理每个事件
        for event in selected_events:
            change_min, change_max = event["favorability_change"]
            change_a = random.randint(change_min, change_max)
            change_b = random.randint(change_min, change_max)
    
            # 添加500点好感度限制检查
            if a_to_b_before + a_to_b_change >= 500 and not has_relation:
                change_a = 0
            if b_to_a_before + b_to_a_change >= 500 and not has_relation:
                change_b = 0
    
            a_to_b_change += change_a
            b_to_a_change += change_b
    
            events_result.append({
                "name": event["name"],
                "description": event["description"],
                "a_to_b_change": change_a,
                "b_to_a_change": change_b
            })
    
        # 更新好感度（内部方法已包含500点限制）
        a_to_b_after = self._update_favorability(group_id, user_a_id, user_b_id, a_to_b_change)
        b_to_a_after = self._update_favorability(group_id, user_b_id, user_a_id, b_to_a_change)
    
        # 检查关系变化
        a_to_b_level_before = self._get_relation_level(a_to_b_before)
        a_to_b_level_after = self._get_relation_level(a_to_b_after)
        b_to_a_level_before = self._get_relation_level(b_to_a_before)
        b_to_a_level_after = self._get_relation_level(b_to_a_after)
    
        return {
            "events": events_result,
            "user_a_to_b_change": a_to_b_change,
            "user_b_to_a_change": b_to_a_change,
            "user_a_to_b_level_before": a_to_b_level_before,
            "user_a_to_b_level_after": a_to_b_level_after,
            "user_b_to_a_level_before": b_to_a_level_before,
            "user_b_to_a_level_after": b_to_a_level_after,
            "user_a_to_b_level_up": a_to_b_level_before != a_to_b_level_after,
            "user_b_to_a_level_up": b_to_a_level_before != b_to_a_level_after
        }

    #endregion

    #region 社交关系
    @filter.command("缔结关系")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def form_relationship(self, event: AstrMessageEvent):
        """缔结特殊关系"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/缔结关系 @对方 关系类型 哦~杂鱼酱❤~")
            yield event.plain_result("可用关系类型：恋人、兄弟、包养、闺蜜")
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要缔结关系的对象哦~杂鱼酱❤~")
            return
        
        relation_type = parts[2]
        if relation_type not in ["恋人", "兄弟", "包养", "闺蜜"]:
            yield event.plain_result("❌ 无效的关系类型，可用：恋人、兄弟、包养、闺蜜")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 不能与自己缔结关系
        if user_id == target_id:
            yield event.plain_result("❌ 不能与自己缔结特殊关系哦~大笨蛋杂鱼酱❤~")
            return
          
        # 获取好感度
        user_to_target = self.get_favorability(group_id, user_id, target_id)
        target_to_user = self.get_favorability(group_id, target_id, user_id)
        
        # 检查好感度是否足够
        if relation_type == "包养":
            if target_to_user < 500:
                yield event.plain_result(f"❌ 对方对你的好感度不足，需要达到500点才能被包养。当前好感度: {target_to_user}")
                return
        else:
            if user_to_target < 500:
                yield event.plain_result(f"❌ 你对对方的好感度不足，需要达到500点。当前好感度: {user_to_target}")
                return
            if target_to_user < 500:
                yield event.plain_result(f"❌ 对方对你的好感度不足，需要达到500点。当前好感度: {target_to_user}")
                return
        
        # 检查所需道具
        required_item = ""
        if relation_type == "恋人":
            required_item = "卡天亚戒指"
        elif relation_type == "兄弟":
            required_item = "一壶烈酒"
        elif relation_type == "包养":
            required_item = "黑金卡"
        elif relation_type == "闺蜜":
            required_item = "百合花种"
        
        # 检查用户是否拥有所需道具
        user_props = self._get_user_props(group_id, user_id)
        if required_item not in user_props or user_props[required_item] < 1:
            yield event.plain_result(f"❌ 缔结{relation_type}关系需要{required_item}，你还没有这个道具！杂鱼酱❤")
            return
        
        # 检查关系数量限制（使用英文标识）
        relation_type_eng = self.RELATION_NAME_TO_TYPE.get(relation_type, relation_type)
        if not self.can_add_relation(group_id, user_id, relation_type_eng):
            yield event.plain_result(f"❌ 您已达到{relation_type}关系的数量上限哦~杂鱼酱❤~")
            return
        
        # 检查目标用户是否可以添加该关系
        if not self.can_add_relation(group_id, target_id, relation_type_eng):
            target_name = await self._get_at_user_name(event, target_id)
            yield event.plain_result(f"❌ {target_name} 已达到{relation_type}关系的数量上限，无法缔结关系哦~杂鱼酱❤~")
            return
        
        # 检查双方是否已有特殊关系
        existing_relation = self.get_special_relation(group_id, user_id, target_id)
        if existing_relation:
            yield event.plain_result(f"❌ 你们之间已有{existing_relation}关系，无法重复缔结{relation_type}关系哦~杂鱼酱❤~")
            return

        # 缔结关系
        self.add_relation(group_id, user_id, target_id, relation_type_eng)
        
        # 扣除道具
        user_props[required_item] -= 1
        if user_props[required_item] <= 0:
            del user_props[required_item]
        self._update_user_props(group_id, user_id, user_props)
        
        # 记录日志
        self._log_operation("info", 
            f"缔结关系: group={group_id}, user={user_id}, "
            f"target={target_id}, relation={relation_type}"
        )
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 恭喜！你与 {target_name} 成功缔结'{relation_type}'关系！\n- 消耗道具: {required_item}")

    @filter.command("升级关系")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def upgrade_relationship(self, event: AstrMessageEvent):
        """升级特殊关系"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/升级关系 @对方 哦~杂鱼酱❤~")
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要升级关系的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取当前关系（中文）
        current_relation_chinese = self.get_special_relation(group_id, user_id, target_id)
        if not current_relation_chinese:
            yield event.plain_result("❌ 你们之间没有可升级的基础关系哦~杂鱼酱❤~")
            return
        
        # 将中文关系转换为英文标识
        if current_relation_chinese in self.RELATION_NAME_TO_TYPE:
            current_relation = self.RELATION_NAME_TO_TYPE[current_relation_chinese]
        else:
            yield event.plain_result(f"❌ 未知的关系类型: {current_relation_chinese}")
            return
        
        # 检查是否可以升级
        if current_relation not in RELATION_UPGRADES:
            yield event.plain_result(f"❌ {current_relation_chinese} 关系无法升级哦~杂鱼酱❤~")
            return
        
        upgraded_relation = RELATION_UPGRADES[current_relation]
        required_item = UPGRADE_ITEMS[upgraded_relation]
        
        # 检查用户是否拥有所需道具
        user_props = self._get_user_props(group_id, user_id)
        if required_item not in user_props or user_props[required_item] < 1:
            yield event.plain_result(f"❌ 升级关系需要{required_item}，你还没有这个道具！杂鱼酱❤")
            return
        
        # 执行升级
        # 移除旧关系（使用中文关系类型）
        self.remove_any_relation(group_id, user_id, target_id)
        
        # 添加新关系（使用英文标识）
        relation_type = upgraded_relation
        self.add_relation(group_id, user_id, target_id, relation_type)
        
        # 扣除道具
        user_props[required_item] -= 1
        if user_props[required_item] <= 0:
            del user_props[required_item]
        self._update_user_props(group_id, user_id, user_props)
        
        # 记录日志
        self._log_operation("info", 
            f"升级关系: group={group_id}, user={user_id}, "
            f"target={target_id}, from={current_relation}, to={upgraded_relation}"
        )
        
        target_name = await self._get_at_user_name(event, target_id)
        new_relation_name = RELATION_TYPE_NAMES.get(upgraded_relation, upgraded_relation)
        yield event.plain_result(f"✨ 恭喜！你与 {target_name} 的关系从 {current_relation_chinese} 升级为 {new_relation_name}！")

    @filter.command("解除关系")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def break_relationship(self, event: AstrMessageEvent):
        """解除特殊关系"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要解除关系的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 不能与自己解除关系
        if user_id == target_id:
            yield event.plain_result("❌ 不能与自己解除关系哦~大笨蛋杂鱼酱❤~")
            return
          
        # 获取当前关系
        relation_type = self.get_special_relation(group_id, user_id, target_id)
        if not relation_type:
            yield event.plain_result("❌ 你们之间没有特殊关系，无法解除哦~杂鱼酱❤~")
            return
        
        # 解除关系
        self.remove_any_relation(group_id, user_id, target_id)
        
        # 重置好感度为50
        self._update_favorability(group_id, user_id, target_id, 50 - self.get_favorability(group_id, user_id, target_id))
        self._update_favorability(group_id, target_id, user_id, 50 - self.get_favorability(group_id, target_id, user_id))
        
        # 记录日志
        self._log_operation("info", 
            f"解除关系: group={group_id}, user={user_id}, "
            f"target={target_id}, relation={relation_type}"
        )
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已成功解除与 {target_name} 的'{relation_type}'关系。双方好感度已重置为50。")

    @filter.command("查看关系")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def view_relationship(self, event: AstrMessageEvent):
        """查看两人之间的关系"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要查看关系的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取相互好感度
        user_to_target = self.get_favorability(group_id, user_id, target_id)
        target_to_user = self.get_favorability(group_id, target_id, user_id)
        
        # 获取关系等级
        user_to_target_level = self._get_relation_level(user_to_target)
        target_to_user_level = self._get_relation_level(target_to_user)
        
        # 获取特殊关系
        special_relation = self.get_special_relation(group_id, user_id, target_id)
        
        # 构建响应
        target_name = await self._get_at_user_name(event, target_id)
        response = f"💞 你与 {target_name} 的关系：\n"
        response += f"- 你对TA的好感度: {user_to_target} ({user_to_target_level})\n"
        response += f"- TA对你的好感度: {target_to_user} ({target_to_user_level})\n"
        
        if special_relation:
            response += f"- 特殊关系: {special_relation}\n"
        
        yield event.plain_result(response)

    @filter.command("社交网络")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def social_network(self, event: AstrMessageEvent):
        """查看自己的社交网络"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return        

        user_data = self._get_user_social_data(group_id, user_id)
        favorability_data = user_data["favorability"]
        
        # 按好感度排序
        sorted_relations = sorted(
            favorability_data.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]  # 取前5个
        
        # 获取特殊关系
        special_relations = {}
        for rel_type, targets in user_data["relations"].items():
            for target_id in targets:
                special_relations[target_id] = RELATION_TYPE_NAMES.get(rel_type, rel_type)
        
        # 构建响应
        response = "🌟 你的社交网络（按好感度排序）:\n\n"
        for i, (target_id, favorability) in enumerate(sorted_relations, 1):
            if favorability <= 0:
                continue
                
            level = self._get_relation_level(favorability)
            special_relation = special_relations.get(str(target_id))
            
            try:
                target_name = await self._get_at_user_name(event, target_id)
            except:
                target_name = f"用户{target_id[-4:]}"
            
            relation_info = f"{i}. {target_name} - 好感度: {favorability} ({level})"
            if special_relation:
                relation_info += f" - {special_relation}"
            
            response += relation_info + "\n"
        
        yield event.plain_result(response)

    #endregion

    #region 社交事件
    @filter.command("社交做")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def social_invite(self, event: AstrMessageEvent):
        """发起社交邀请"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/社交做 <事件名> [强制] @用户")
            return
        
        event_name = parts[1]
        if event_name not in SOCIAL_EVENTS:
            yield event.plain_result(f"❌ 未知社交事件，可用事件: {', '.join(SOCIAL_EVENTS.keys())}")
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要邀请的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())

        # 检查是否强制
        force = "强制" in parts
        if force:
            # 检查是否有"媚药"道具
            user_props = self._get_user_props(group_id, user_id)
            if "媚药" not in user_props or user_props["媚药"] < 1:
                yield event.plain_result("❌ 强制社交需要消耗【媚药】道具，可在商店购买")
                return
        
            # 扣除道具
            user_props["媚药"] -= 1
            if user_props["媚药"] <= 0:
                del user_props["媚药"]
            self._update_user_props(group_id, user_id, user_props)
        
            # 记录日志
            self._log_operation("info", 
                f"强制社交消耗媚药: group={group_id}, user={user_id}, "
                f"target={target_id}, event={event_name}"
            )
        
        # 检查是否是自己
        if user_id == target_id:
            yield event.plain_result("❌ 不能邀请自己哦~杂鱼酱❤~")
            return
        
        # 检查是否是机器人
        if target_id == event.get_self_id():
            yield event.plain_result("抱歉，我现在很忙，无法参加社交活动哦~杂鱼酱❤~")
            return
        
        # 强制邀请直接执行
        if force:
            async for result in self._execute_social_event(
                event, group_id, user_id, target_id, event_name, force=True
            ):
                yield result
            return
        
        # 非强制邀请：存储邀请
        confirmation_code = self._generate_social_code(group_id, target_id)
        
        # 存储邀请
        group_id_str = str(group_id)
        if group_id_str not in self.social_invitations:
            self.social_invitations[group_id_str] = {}
            
        self.social_invitations[group_id_str][target_id] = {
            "initiator_id": user_id,
            "event_name": event_name,
            "confirmation_code": confirmation_code,
            "created_at": datetime.now(SHANGHAI_TZ)
        }
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(
            f"📩 已向 {target_name} 发送社交邀请: {event_name}\n"
            f"🔑 验证码: {confirmation_code}\n"
            f"💖 请 {target_name} 使用命令同意邀请: /社交同意做 {confirmation_code}"
        )

    def _generate_social_code(self, group_id: str, target_id: str) -> str:
        """生成唯一的验证码（确保在群组内目标用户唯一）"""
        confirmation_code = str(group_id)
        
        # 生成随机验证码
        code = str(random.randint(1000, 9999))
        
        # 检查是否已存在（概率很低但可能发生）
        if (confirmation_code in self.social_invitations and 
            target_id in self.social_invitations[confirmation_code] and
            code in self.social_invitations[confirmation_code][target_id]):
            # 如果已存在，递归生成新码
            return self._generate_social_code(group_id, target_id)
        
        return code

    @filter.command("社交同意做")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def accept_social(self, event: AstrMessageEvent):
        """同意社交邀请"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/社交同意做 <验证码>")
            return
        
        confirmation_code = parts[1]
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        group_id_str = str(group_id)
        
        # 获取邀请
        if (group_id_str not in self.social_invitations or 
            user_id not in self.social_invitations[group_id_str]):
            yield event.plain_result("❌ 没有找到有效的社交邀请")
            return
        
        invitation = self.social_invitations[group_id_str][user_id]
        
        # 检查验证码
        if confirmation_code != invitation["confirmation_code"]:
            yield event.plain_result("❌ 验证码错误！")
            return
        
        # 检查邀请是否过期（10分钟）
        if datetime.now(SHANGHAI_TZ) - invitation["created_at"] > timedelta(minutes=10):
            del self.social_invitations[group_id_str][user_id]
            yield event.plain_result("❌ 邀请已过期")
            return
        
        # 执行社交事件
        initiator_id = invitation["initiator_id"]
        event_name = invitation["event_name"]
        
        async for result in self._execute_social_event(
            event, group_id, initiator_id, user_id, event_name
        ):
            yield result
        
        # 删除邀请
        del self.social_invitations[group_id_str][user_id]

    async def _execute_social_event(self, event, group_id, user_id, target_id, event_name, force=False):
        """执行社交事件"""
        event_config = SOCIAL_EVENTS[event_name]
        user_name = await self._get_at_user_name(event, user_id)
        target_name = await self._get_at_user_name(event, target_id)
        
        # 检查好感度要求（强制时忽略）
        if not force:
            favorability = self.get_favorability(group_id, target_id, user_id)
            if favorability < event_config["min_favorability"]:
                yield event.plain_result(
                    f"❌ {target_name} 对你的好感度不足（需要{event_config['min_favorability']}，当前{favorability}），无法进行此社交活动"
                )
                return
        
        # 计算成功率（强制时降低20%）
        success_rate = event_config["success_rate"]
        if force:
            success_rate = max(0.1, success_rate - 0.2)
        
        # 随机决定结果
        is_success = random.random() < success_rate
        change_range = event_config["favorability_change"]
        change = random.randint(change_range[0], change_range[1])
        
        # 选择随机消息
        if is_success:
            msg_template = random.choice(event_config["success_msgs"])
            change_sign = 1
        else:
            msg_template = random.choice(event_config["failure_msgs"])
            change_sign = -1
        
        # 更新好感度
        self._update_favorability(group_id, user_id, target_id, change * change_sign)
        self._update_favorability(group_id, target_id, user_id, change * change_sign)
        
        # 构建响应
        response = msg_template.format(
            inviter_name=user_name,
            target_name=target_name,
            change=change
        )
        
        if force:
            response = f"⚡强制社交: {response}\n- 消耗【媚药】x1"
        
        yield event.plain_result(response)

    @filter.command("社交列表")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def social_list(self, event: AstrMessageEvent):
        """显示社交事件列表"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        list_text = "📋 可用的社交活动:\n\n"
        for name, details in SOCIAL_EVENTS.items():
            list_text += f"【{name}】\n"
            list_text += f"- 成功率: {details['success_rate']*100:.0f}%\n"
            list_text += f"- 好感度变化: {details['favorability_change'][0]}-{details['favorability_change'][1]}点\n"
            list_text += f"- 最低好感要求: {details.get('min_favorability', 0)}点\n\n"
        
        # 生成图片
        image_paths = await self.text_to_images(
            text=list_text,
            title="社交活动列表"
        )
        
        for path in image_paths:
            yield event.image_result(path)

    @filter.command("社交邀请")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def view_social_invites(self, event: AstrMessageEvent):
        """查看收到的社交邀请"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        group_id_str = str(group_id)
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        if (group_id_str not in self.social_invitations or 
            user_id not in self.social_invitations[group_id_str]):
            yield event.plain_result("❌ 你目前没有待处理的社交邀请")
            return
        
        invites = self.social_invitations[group_id_str][user_id]
        now = datetime.now(SHANGHAI_TZ)
        
        response = "📨 你的社交邀请:\n\n"
        for code, invite in invites.items():
            initiator_id = invite["initiator_id"]
            try:
                initiator_name = await self._get_at_user_name(event, initiator_id)
            except:
                initiator_name = f"用户{initiator_id[-4:]}"
            
            elapsed = now - invite["created_at"]
            remaining = max(0, 10 - int(elapsed.total_seconds() / 60))
            
            response += (
                f"🔑 验证码: {code}\n"
                f"发起人: {initiator_name}\n"
                f"活动: {invite['event_name']}\n"
                f"剩余时间: {remaining}分钟\n"
                f"----------------\n"
            )
        
        response += "\n使用 /社交同意做 <验证码> 来接受邀请"
        yield event.plain_result(response)
    #endregion

    #region 证件系统
    @filter.command("申请证件")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def apply_certificate(self, event: AstrMessageEvent):
        """申请证件"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/申请证件 <证件名> @对方 哦~杂鱼酱❤~")
            return
        
        cert_name = parts[1]
        if cert_name not in CERTIFICATE_TYPES:
            yield event.plain_result(f"❌ 未知证件类型，可用证件: {', '.join(CERTIFICATE_TYPES.keys())}")
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@申请证件的对象哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 检查是否是自己
        if user_id == target_id:
            yield event.plain_result("❌ 不能对自己申请证件哦~大笨蛋杂鱼酱❤~")
            return
            
        # 检查是否是机器人
        if target_id == event.get_self_id():
            yield event.plain_result("抱歉，妹妹不能申请证件哦~杂鱼酱❤~")
            return
        
        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        target_data = self._get_user_data(group_id, target_id)
        
        # 检查关系（结婚证需要夫妻关系）
        if cert_name == "结婚证":
            relation = self.get_special_relation(group_id, user_id, target_id)
            if relation != "夫妻":
                yield event.plain_result("❌ 申请结婚证需要双方是夫妻关系哦~杂鱼酱❤~")
                return
        
        # 检查资产要求
        requirements = CERTIFICATE_TYPES[cert_name]["requirements"]
        asset_data = self._load_asset_data()
        user_assets = asset_data.get(group_id, {}).get(user_id, {})
        
        missing_assets = []
        for asset_type in requirements:
            if asset_type not in user_assets or not user_assets[asset_type]:
                missing_assets.append(asset_type)
        
        if missing_assets:
            yield event.plain_result(f"❌ 申请证件需要以下资产: {', '.join(missing_assets)}")
            return
        
        # 生成唯一验证码
        confirmation_code = str(random.randint(1000, 9999))
        
        # 存储证件申请
        group_id_str = str(group_id)
        if group_id_str not in self.certificate_applications:
            self.certificate_applications[group_id_str] = {}
            
        self.certificate_applications[group_id_str][target_id] = {
            "applicant_id": user_id,
            "certificate_name": cert_name,
            "confirmation_code": confirmation_code,
            "created_at": datetime.now(SHANGHAI_TZ)
        }
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(
            f"📝 已向 {target_name} 发送 {cert_name} 申请!\n"
            f"🔑 验证码: {confirmation_code}\n"
            f"💖 请 {target_name} 使用命令同意申请: /同意证件 {confirmation_code}"
        )

    @filter.command("同意证件")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def accept_certificate(self, event: AstrMessageEvent):
        """同意证件申请"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/同意证件 <验证码>")
            return
        
        confirmation_code = parts[1]
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        group_id_str = str(group_id)
        
        # 获取证件申请
        if (group_id_str not in self.certificate_applications or 
            user_id not in self.certificate_applications[group_id_str]):
            yield event.plain_result("❌ 没有找到有效的证件申请")
            return
        
        application = self.certificate_applications[group_id_str][user_id]
        
        # 检查验证码
        if confirmation_code != application["confirmation_code"]:
            yield event.plain_result("❌ 验证码错误！")
            return
        
        # 检查申请是否过期（10分钟）
        if datetime.now(SHANGHAI_TZ) - application["created_at"] > timedelta(minutes=10):
            del self.certificate_applications[group_id_str][user_id]
            yield event.plain_result("❌ 证件申请已过期")
            return
        
        # 创建证件
        applicant_id = application["applicant_id"]
        cert_name = application["certificate_name"]
        
        # 获取证件数据
        certificate_data = self._load_certificate_data()
        group_certs = certificate_data.setdefault(group_id, {})
        user_certs = group_certs.setdefault(user_id, {})
        applicant_certs = group_certs.setdefault(applicant_id, {})
        
        # 生成证件ID
        cert_id = f"{cert_name}_{int(time.time())}"
        
        # 创建证件信息
        cert_info = {
            "id": cert_id,
            "type": cert_name,
            "applicant": applicant_id,
            "target": user_id,
            "created_at": datetime.now(SHANGHAI_TZ).isoformat(),
            "status": "有效"
        }
        
        # 保存到双方证件列表
        user_certs[cert_id] = cert_info
        applicant_certs[cert_id] = cert_info
        
        # 保存数据
        self._save_certificate_data(certificate_data)
        
        # 删除申请
        del self.certificate_applications[group_id_str][user_id]
        
        applicant_name = await self._get_at_user_name(event, applicant_id)
        user_name = await self._get_at_user_name(event, user_id)
        yield event.plain_result(f"✅ {user_name} 已同意 {applicant_name} 的 {cert_name} 申请！证件ID: {cert_id}")

    @filter.command("我的证件")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def list_my_certificates(self, event: AstrMessageEvent):
        """列出我的证件"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 获取证件数据
        certificate_data = self._load_certificate_data()
        user_certs = certificate_data.get(group_id, {}).get(user_id, {})
        
        if not user_certs:
            yield event.plain_result("📭 您目前没有任何证件哦~杂鱼酱❤~")
            return
        
        response = "📋 您的证件列表:\n\n"
        for cert_id, cert_info in user_certs.items():
            response += f"【{cert_info['type']}】\n"
            response += f"- ID: {cert_id}\n"
            response += f"- 状态: {cert_info['status']}\n"
            response += f"- 创建时间: {cert_info['created_at']}\n"
            
            if cert_info['type'] in ["结婚证", "离婚证"]:
                other_id = cert_info['applicant'] if cert_info['target'] == user_id else cert_info['target']
                other_name = await self._get_at_user_name(event, other_id)
                response += f"- 对方: {other_name}\n"
            
            response += "\n"
        
        response += "使用 /展示证件 <证件ID> 查看证件详情"
        yield event.plain_result(response)

    @filter.command("展示证件")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def show_certificate(self, event: AstrMessageEvent):
        """展示证件详情（图片）"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/展示证件 <证件ID>")
            return
        
        cert_id = parts[1]
        
        # 获取证件数据
        certificate_data = self._load_certificate_data()
        user_certs = certificate_data.get(group_id, {}).get(user_id, {})
        
        if cert_id not in user_certs:
            yield event.plain_result("❌ 未找到该证件，请检查证件ID")
            return
        
        cert_info = user_certs[cert_id]
        
        # 检查证件状态（如果关系解除，自动转为离婚证）
        if cert_info["type"] == "结婚证":
            # 检查双方是否还是夫妻关系
            other_id = cert_info['applicant'] if cert_info['target'] == user_id else cert_info['target']
            relation = self.get_special_relation(group_id, user_id, other_id)
            
            if relation != "夫妻":
                # 更新为离婚证
                cert_info["type"] = "离婚证"
                cert_info["status"] = "失效"
                user_certs[cert_id] = cert_info
                self._save_certificate_data(certificate_data)
        
        # 根据证件类型生成不同的图片
        if cert_info["type"] in ["结婚证", "离婚证"]:
            # 获取双方名称
            applicant_id = cert_info['applicant']
            target_id = cert_info['target']
            
            applicant_name = await self._get_at_user_name(event, applicant_id)
            target_name = await self._get_at_user_name(event, target_id)
            
            # 生成结婚证/离婚证卡片
            image_path = await self._generate_marriage_certificate(
                event=event,
                user_id1=applicant_id,
                user_name1=applicant_name,
                user_id2=target_id,
                user_name2=target_name,
                cert_id=cert_id,
                cert_type=cert_info["type"]  # 添加证件类型参数
            )
        else:
            # 其他证件使用通用生成方法
            image_path = await self._generate_certificate_image(event, cert_info)
        
        yield event.image_result(image_path)

    #endregion

    #region 资产组件
    @filter.command("购入资产")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def buy_asset(self, event: AstrMessageEvent):
        """购入资产"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/购入资产 <资产名> 哦~杂鱼酱❤~")
            yield event.plain_result(f"可用资产类型: {', '.join(ASSET_TYPES.keys())}")
            return
        
        asset_name = parts[1]
        asset_type = None
        asset_details = None
        
        # 查找匹配的资产
        for asset_type_name, assets in ASSET_TYPES.items():
            if asset_name in assets:
                asset_type = asset_type_name
                asset_details = assets[asset_name]
                break
        
        if not asset_details:
            yield event.plain_result(f"❌ 未知资产，可用资产: {', '.join([a for t in ASSET_TYPES.values() for a in t])}")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        user_data = self._get_user_data(group_id, user_id)
        
        # 检查金币是否足够
        price = asset_details["price"]
        if user_data["coins"] < price:
            yield event.plain_result(f"❌ 需要 {price}金币，当前金币: {user_data['coins']:.1f}哦~穷鬼杂鱼酱❤~")
            return
        
        # 扣除金币
        user_data["coins"] -= price
        
        # 添加资产
        asset_data = self._load_asset_data()
        group_assets = asset_data.setdefault(group_id, {})
        user_assets = group_assets.setdefault(user_id, {})
        
        if asset_type not in user_assets:
            user_assets[asset_type] = []
        
        user_assets[asset_type].append(asset_name)
        
        # 保存数据
        self._save_asset_data(asset_data)
        self._save_user_data(group_id, user_id, user_data)
        
        yield event.plain_result(f"✅ 杂鱼酱❤~成功购买 {asset_name} ({asset_type})，消耗{price}金币")

    @filter.command("卖出资产")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def sell_asset(self, event: AstrMessageEvent):
        """卖出资产"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/卖出资产 <资产名> 哦~杂鱼酱❤~")
            return
        
        asset_name = parts[1]
        
        # 获取资产数据
        asset_data = self._load_asset_data()
        group_assets = asset_data.get(group_id, {})
        user_assets = group_assets.get(user_id, {})
        
        # 查找资产
        asset_found = False
        for asset_type, assets in user_assets.items():
            if asset_name in assets:
                # 移除资产
                assets.remove(asset_name)
                asset_found = True
                
                # 计算售价（原价的80%）
                price = ASSET_TYPES[asset_type][asset_name]["price"]
                sell_price = price * 0.8
                
                # 增加用户金币
                user_data = self._get_user_data(group_id, user_id)
                user_data["coins"] += sell_price
                
                # 保存数据
                self._save_asset_data(asset_data)
                self._save_user_data(group_id, user_id, user_data)
                
                yield event.plain_result(f"✅ 杂鱼酱❤~成功卖出 {asset_name}，获得{sell_price:.1f}金币")
                return
        
        if not asset_found:
            yield event.plain_result(f"❌ 未找到资产 {asset_name}，请检查资产名称")

    @filter.command("我的资产")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def list_my_assets(self, event: AstrMessageEvent):
        """列出我的资产"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 获取资产数据
        asset_data = self._load_asset_data()
        user_assets = asset_data.get(group_id, {}).get(user_id, {})
        
        if not user_assets:
            yield event.plain_result("📭 您目前没有任何资产哦~杂鱼酱❤~")
            return
        
        response = "🏠 您的资产列表:\n\n"
        total_value = 0
        
        for asset_type, assets in user_assets.items():
            if assets:  # 确保有资产
                response += f"【{asset_type}】\n"
                for asset_name in assets:
                    price = ASSET_TYPES[asset_type][asset_name]["price"]
                    total_value += price
                    response += f"- {asset_name}: {price}金币\n"
                response += "\n"
        
        response += f"💰 总资产价值: {total_value}金币"
        yield event.plain_result(response)
    #endregion

#endregion

#region ==================== 股票交易系统 ====================
    @filter.command("股票行情")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def stock_market(self, event: AstrMessageEvent):
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        """显示优化后的股票行情"""
        response = "📈 当前股票行情:\n\n"
        response += f"当前股票交易时间: 8:00-18:00\n"
        response += f"当前股票刷新时间间隔：{STOCK_REFRESH_INTERVAL}秒\n"
    
        for stock_name, stock_info in self.stocks.items():
            price = stock_info["price"]
            volatility = stock_info["volatility"] * 100
            trend = stock_info.get("trend", "random")
            trend_count = stock_info.get("trend_count", 0)
        
            # 趋势描述
            trend_desc = {
                "up": "📈 上涨趋势",
                "down": "📉 下跌趋势",
                "flat": "📊 盘整趋势",
                "random": "🎲 随机波动"
            }.get(trend, "🎲 未知趋势")
        
            # 趋势强度
            if trend_count > 0:
                trend_desc += f" (已持续{trend_count}次)"
        
            response += f"==============================\n"
            response += f"【{stock_name}】\n"
            response += f"- 当前价格: {price:.2f}金币\n"
            response += f"- 波动率: {volatility:.1f}%\n"
            response += f"- 趋势: {trend_desc}\n\n"

            if "last_black_swan_event" in stock_info:
                event_info = stock_info["last_black_swan_event"]
                event_time = event_info["time"]
                event_type = event_info["type"]
                multiplier = event_info["multiplier"]
            
                # 计算时间差
                now = datetime.now()
                elapsed = now - event_time
                hours = elapsed.seconds // 3600
                minutes = (elapsed.seconds % 3600) // 60
            
                # 添加事件信息
                response += f"⚠️ 黑天鹅事件: {event_type} {multiplier:.1f}倍 ({hours}小时{minutes}分钟前)\n"
        
            response += "\n"
    
        response += f"==============================\n"
        response += "💡 黑天鹅事件说明:\n"
        response += "- 0.1%概率发生极端波动\n"
        response += "- 暴涨: 5-10倍价格增长\n"
        response += "- 暴跌: 价格变为1/5-1/10\n"
        response += "- 事件发生后价格保持新水平\n\n"
        response += f"==============================\n"
        response += "💡 趋势说明:\n"
        response += "📈 上涨趋势: 价格可能连续上涨\n"
        response += "📉 下跌趋势: 价格可能连续下跌\n"
        response += "📊 盘整趋势: 价格波动较小\n"
        response += "🎲 随机波动: 价格无明确方向\n\n"
        response += f"==============================\n"
        response += "使用 /买入股票 <股票名> <数量> 购买股票\n"
        response += "使用 /卖出股票 <股票名> <数量> 卖出股票\n"
        response += f"使用 /抛出 <股票名> 一键抛出股票\n"
    
        # 生成图片
        image_paths = await self.text_to_images(
            text=response,
            title="股票行情"
        )
    
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)

    @filter.command("买入股票")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def buy_stock(self, event: AstrMessageEvent):
        """买入股票"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        if not self.is_trading_time():
            yield event.plain_result("❌ 当前非交易时间（8:00-18:00），无法交易股票")
            return

        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/买入股票 <股票名> <数量> 哦~杂鱼酱❤~")
            return
        
        stock_name = parts[1]
        try:
            quantity = int(parts[2])
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字数量哦~杂鱼酱❤~")
            return
        
        if quantity <= 0:
            yield event.plain_result("❌ 数量必须大于0哦~杂鱼酱❤~")
            return
        
        if stock_name not in self.stocks:
            yield event.plain_result(f"❌ 未知股票，可用股票: {', '.join(self.stocks.keys())}")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        
        # 获取用户股票数据（按群聊隔离）
        user_stock_data = self._get_user_stock_data(group_id, user_id)
        
        stock_price = self.stocks[stock_name]["price"]
        total_cost = stock_price * quantity
        
        # 检查金币是否足够
        if user_data["coins"] < total_cost:
            yield event.plain_result(f"❌ 需要 {total_cost:.2f}金币，当前现金: {user_data['coins']:.2f}金币哦~穷鬼杂鱼酱❤~")
            return
        
        # 扣除金币
        user_data["coins"] -= total_cost
        
        # 更新用户股票数据
        if stock_name not in user_stock_data:
            user_stock_data[stock_name] = {
                "quantity": 0,
                "avg_price": 0.0
            }
        
        stock_info = user_stock_data[stock_name]
        current_quantity = stock_info["quantity"]
        current_avg_price = stock_info["avg_price"]
        
        # 计算新的平均价格
        new_quantity = current_quantity + quantity
        new_avg_price = (current_avg_price * current_quantity + total_cost) / new_quantity
        
        stock_info["quantity"] = new_quantity
        stock_info["avg_price"] = round(new_avg_price, 2)
        
        # 保存数据
        self._save_user_data(group_id, user_id, user_data)
        self._save_user_stock_data()
        
        yield event.plain_result(
            f"✅ 杂鱼酱❤成功买入 {quantity}股 {stock_name}!\n"
            f"- 成交价: {stock_price:.2f}金币/股\n"
            f"- 总花费: {total_cost:.2f}金币\n"
            f"- 持仓均价: {new_avg_price:.2f}金币/股"
        )

    @filter.command("卖出股票")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def sell_stock(self, event: AstrMessageEvent):
        """卖出股票"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        if not self.is_trading_time():
            yield event.plain_result("❌ 当前非交易时间（8:00-18:00），无法交易股票")
            return

        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/卖出股票 <股票名> <数量> 哦~杂鱼酱❤~")
            return
        
        stock_name = parts[1]
        try:
            quantity = int(parts[2])
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字数量哦~杂鱼酱❤~")
            return
        
        if quantity <= 0:
            yield event.plain_result("❌ 数量必须大于0哦~杂鱼酱❤~")
            return
        
        if stock_name not in self.stocks:
            yield event.plain_result(f"❌ 未知股票，可用股票: {', '.join(self.stocks.keys())}")
            return
        
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        
        # 获取用户数据
        user_data = self._get_user_data(group_id, user_id)
        
        # 获取用户股票数据（按群聊隔离）
        user_stock_data = self._get_user_stock_data(group_id, user_id)
        
        if stock_name not in user_stock_data:
            yield event.plain_result(f"❌ 你没有持有 {stock_name} 股票哦~杂鱼酱❤~")
            return
        
        stock_info = user_stock_data[stock_name]
        if stock_info["quantity"] < quantity:
            yield event.plain_result(f"❌ 你只有 {stock_info['quantity']}股 {stock_name}，无法卖出 {quantity}股哦~杂鱼酱❤~")
            return
        
        # 计算收益
        current_price = self.stocks[stock_name]["price"]
        avg_price = stock_info["avg_price"]
        total_income = current_price * quantity
        profit = total_income - (avg_price * quantity)
        
        # 收取1%手续费
        fee = total_income * 0.01
        net_income = total_income - fee

        # 更新用户金币
        user_data["coins"] += net_income
        
        # 更新股票持仓
        stock_info["quantity"] -= quantity
        if stock_info["quantity"] == 0:
            del user_stock_data[stock_name]
        
        # 保存数据
        self._save_user_data(group_id, user_id, user_data)
        self._save_user_stock_data()
        
        profit_text = f"盈利: +{profit:.2f}金币" if profit >= 0 else f"亏损: {profit:.2f}金币"
        yield event.plain_result(
            f"✅ 杂鱼酱❤成功卖出 {quantity}股 {stock_name}!\n"
            f"- 成交价: {current_price:.2f}金币/股\n"
            f"- 总收益: {total_income:.2f}金币\n"
            f"- 手续费(1%): {fee:.2f}金币\n"
            f"- 净收益: {net_income:.2f}金币\n"
            f"- {profit_text}"
        )

    @filter.command("我的持仓")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def my_stocks(self, event: AstrMessageEvent):
        """查看我的股票持仓（按群聊隔离）"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        # 黑名单检查
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return

        # 获取用户股票数据（按群聊隔离）
        user_stock_data = self._get_user_stock_data(group_id, user_id)
        
        if not user_stock_data:
            yield event.plain_result("📭 你目前没有持有任何股票哦~杂鱼酱❤~")
            return
        
        response = "📊 你的股票持仓:\n\n"
        total_value = 0
        total_profit = 0
        
        for stock_name, stock_info in user_stock_data.items():
            quantity = stock_info["quantity"]
            avg_price = stock_info["avg_price"]
            current_price = self.stocks[stock_name]["price"]
            current_value = current_price * quantity
            profit = (current_price - avg_price) * quantity
            
            total_value += current_value
            total_profit += profit
            
            profit_text = f"盈利: +{profit:.2f}金币" if profit >= 0 else f"亏损: {profit:.2f}金币"
            
            response += (
                f"【{stock_name}】\n"
                f"- 持仓: {quantity}股\n"
                f"- 均价: {avg_price:.2f}金币/股\n"
                f"- 现价: {current_price:.2f}金币/股\n"
                f"- 当前价值: {current_value:.2f}金币\n"
                f"- {profit_text}\n\n"
            )
        
        response += f"💰 持仓总价值: {total_value:.2f}金币\n"
        response += f"📈 总浮动盈亏: {total_profit:.2f}金币"
        
        yield event.plain_result(response)

    @filter.command("抛售")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def sell_all_stocks(self, event: AstrMessageEvent):
        """一键抛售股票"""
        # 黑名单检查
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        if self.is_user_blacklisted(group_id, user_id):
            self._log_operation("info", 
                f"忽略黑名单用户请求: group={group_id}, user={user_id}, "
                f"message={event.message_str[:50]}"
            )
            return
        
        # 检查交易时间
        if not self.is_trading_time():
            yield event.plain_result("❌ 当前非交易时间（8:00-18:00），无法交易股票")
            return
        
        # 解析参数
        parts = event.message_str.strip().split()
        stock_name = None
        if len(parts) > 1:
            stock_name = parts[1]
        
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 获取用户股票数据
        user_stock_data = self._get_user_stock_data(group_id, user_id)
        
        if not user_stock_data:
            yield event.plain_result("📭 您当前没有持有任何股票")
            return
        
        # 计算总收益
        total_income = 0
        sold_stocks = []
        
        # 卖出所有股票或指定股票
        for name, stock_info in list(user_stock_data.items()):
            if stock_name and name != stock_name:
                continue
            
            quantity = stock_info["quantity"]
            current_price = self.stocks[name]["price"]
            stock_value = current_price * quantity
            
            # 计算手续费（1%）
            fee = stock_value * 0.01
            net_income = stock_value - fee
            
            # 更新用户金币
            user_data = self._get_user_data(group_id, user_id)
            user_data["coins"] += net_income
            self._save_user_data(group_id, user_id, user_data)
            
            # 记录卖出信息
            sold_stocks.append({
                "name": name,
                "quantity": quantity,
                "price": current_price,
                "value": stock_value,
                "fee": fee,
                "net_income": net_income
            })
            
            total_income += net_income
            
            # 从持仓中移除
            del user_stock_data[name]
        
        # 保存数据
        self._save_user_stock_data()
        
        # 生成响应
        if not sold_stocks:
            yield event.plain_result(f"❌ 未找到股票 '{stock_name}' 或您未持有该股票")
            return
        
        response = "📉 股票抛售结果:\n\n"
        for stock in sold_stocks:
            response += (
                f"==============================\n"
                f"【{stock['name']}】\n"
                f"- 数量: {stock['quantity']}股\n"
                f"- 成交价: {stock['price']:.2f}金币/股\n"
                f"- 总价值: {stock['value']:.2f}金币\n"
                f"- 手续费(1%): {stock['fee']:.2f}金币\n"
                f"- 净收益: {stock['net_income']:.2f}金币\n\n"
            )
        
        response += f"==============================\n"
        response += f"💰 总净收益: {total_income:.2f}金币"
        
        # 生成图片
        image_paths = await self.text_to_images(
            text=response,
            title="股票抛售结果"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)

#endregion

#region ==================== 管理系统 ====================
#免责声明：代码中的称呼与词汇为娱乐性质，不涉及政治等敏感内容
    @filter.command_group("WACadmin")
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def admin_commands(self, event: AstrMessageEvent):
        """管理员命令组"""
        pass

    #region 管理员股票管理
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("添加股票")
    async def add_stock(self, event: AstrMessageEvent):
        """添加新股票"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 添加股票 <股票名> <初始价格> [波动率]")
            return
        
        stock_name = parts[2]
        try:
            initial_price = float(parts[3])
            if initial_price <= 0:
                yield event.plain_result("❌ 初始价格必须大于0")
                return
        except (ValueError, IndexError):
            yield event.plain_result("❌ 请输入有效的初始价格")
            return
        
        # 默认波动率10%
        volatility = 0.10
        if len(parts) > 4:
            try:
                volatility = float(parts[4])
                if volatility <= 0 or volatility > 1:
                    yield event.plain_result("❌ 波动率必须在0.01到1之间")
                    return
            except ValueError:
                yield event.plain_result("❌ 请输入有效的波动率")
                return
        
        if stock_name in self.stocks:
            yield event.plain_result(f"❌ 股票 {stock_name} 已存在")
            return
        
        # 添加新股票
        self.stocks[stock_name] = {
            "price": initial_price,
            "volatility": volatility
        }
        self._save_stock_data()
        
        yield event.plain_result(f"✅ 成功添加股票 {stock_name}!\n- 初始价格: {initial_price:.2f}金币\n- 波动率: {volatility*100:.1f}%")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("删除股票")
    async def remove_stock(self, event: AstrMessageEvent):
        """删除股票"""
        # 获取消息字符串并去除首尾空格
        msg = event.message_str.strip()
    
        # 分割命令，但只分割一次（分成两部分：命令名和参数）
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 删除股票 <股票名>")
            return
    
        # 股票名是剩余部分
        stock_name = parts[2]
    
        # 检查股票是否存在
        if stock_name not in self.stocks:
            # 尝试查找相似股票
            similar_stocks = [name for name in self.stocks.keys() if stock_name in name]
        
            if similar_stocks:
                yield event.plain_result(
                    f"❌ 股票 '{stock_name}' 不存在，可能是以下股票之一？\n"
                    f"{', '.join(similar_stocks)}"
                )
            else:
                yield event.plain_result(
                    f"❌ 股票 '{stock_name}' 不存在，可用股票: {', '.join(self.stocks.keys())}"
                )
            return
    
        # 删除股票
        del self.stocks[stock_name]
        self._save_stock_data()
    
        # 从所有用户持仓中移除该股票
        total_refund = 0
        affected_users = 0
    
        for group_id, group_users in self.stock_user_data.items():
            for user_id, user_stocks in group_users.items():
                if stock_name in user_stocks:
                    stock_info = user_stocks[stock_name]
                    quantity = stock_info["quantity"]
                    current_price = self.stocks.get(stock_name, {}).get("price", 0)
                    total_value = current_price * quantity
                
                    # 返还金币（如果用户数据存在）
                    if group_id in self._get_user_data(group_id, user_id):
                        user_data = self._get_user_data(group_id, user_id)
                        user_data["coins"] += total_value
                        self._save_user_data(group_id, user_id, user_data)
                        total_refund += total_value
                        affected_users += 1
                
                del user_stocks[stock_name]
    
        self._save_user_stock_data()
    
        yield event.plain_result(
            f"✅ 成功删除股票 {stock_name}!\n"
            f"⚠️ 所有用户持仓已强制卖出\n"
            f"- 受影响用户: {affected_users}人\n"
            f"- 总返还金币: {total_refund:.2f}"
        )


    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("设置股价")
    async def set_stock_price(self, event: AstrMessageEvent):
        """设置股票价格"""
        parts = event.message_str.strip().split()
        if len(parts) < 4:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 设置股价 <股票名> <新价格>")
            return
        
        stock_name = parts[2]
        try:
            new_price = float(parts[3])
            if new_price <= 0:
                yield event.plain_result("❌ 价格必须大于0")
                return
        except ValueError:
            yield event.plain_result("❌ 请输入有效的价格")
            return
        
        if stock_name not in self.stocks:
            yield event.plain_result(f"❌ 股票 {stock_name} 不存在")
            return
        
        # 更新价格
        self.stocks[stock_name]["price"] = new_price
        self._save_stock_data()
        
        yield event.plain_result(f"✅ 成功设置 {stock_name} 价格为 {new_price:.2f}金币")
    #endregion

    #region 管理员事件管理
        #region 约会事件
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("查阅约会邀请")
    async def view_date_invitations(self, event: AstrMessageEvent):
        """列出所有有效的约会邀请（使用图片输出）"""
        # 获取当前时间
        now = datetime.now(SHANGHAI_TZ)
        
        # 构建邀请列表文本
        invitation_text = "📬 有效约会邀请列表（未过期）\n\n"
        invitation_count = 0
        
        for group_id, invites in self.date_confirmations.items():
            # 获取群组名称
            try:
                group_info = await self.context.get_group_info(int(group_id))
                group_name = group_info.group_name
            except:
                group_name = f"群组 {group_id}"
            
            invitation_text += f"【{group_name}】\n"
            
            for target_id, invite in invites.items():
                # 检查邀请是否过期
                if now - invite['created_at'] > timedelta(minutes=5):
                    continue  # 跳过过期邀请
                
                # 获取用户名称
                try:
                    initiator_name = await self._get_at_user_name(event, invite['initiator_id'])
                    target_name = await self._get_at_user_name(event, target_id)
                except:
                    initiator_name = f"用户{invite['initiator_id'][-4:]}"
                    target_name = f"用户{target_id[-4:]}"
                
                # 计算剩余时间
                remaining = timedelta(minutes=5) - (now - invite['created_at'])
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                
                invitation_text += (
                    f"==============================\n"
                    f"- 发起人: {initiator_name} → 目标: {target_name}\n"
                    f"  验证码: {invite['confirmation_code']}\n"
                    f"  剩余时间: {minutes}分{seconds}秒\n"
                    f"  创建时间: {invite['created_at'].strftime('%H:%M:%S')}\n\n"
                )
                invitation_count += 1
        
        if invitation_count == 0:
            invitation_text += "❌ 当前没有有效的约会邀请"
        
        # 使用文本转图片接口输出
        image_paths = await self.text_to_images(
            text=invitation_text,
            title="约会邀请列表"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("强接约会")
    async def force_accept_date(self, event: AstrMessageEvent):
        """强制替用户接受约会"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 强接约会 @用户 <验证码>")
            return
        
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要强制接受约会的用户")
            return
        
        confirmation_code = parts[2]
        group_id = str(event.message_obj.group_id)
        group_id_str = str(group_id)
        
        # 获取约会邀请
        if (group_id_str not in self.date_confirmations or 
            target_id not in self.date_confirmations[group_id_str]):
            yield event.plain_result("❌ 该用户没有待处理的约会邀请")
            return
        
        invitation = self.date_confirmations[group_id_str][target_id]
        
        # 检查验证码是否匹配
        if confirmation_code != invitation["confirmation_code"]:
            yield event.plain_result(f"❌ 验证码错误！正确的验证码是: {invitation['confirmation_code']}")
            return
        
        # 执行约会
        initiator_id = invitation["initiator_id"]
        initiator_name = await self._get_at_user_name(event, initiator_id)
        target_name = await self._get_at_user_name(event, target_id)
        
        # 运行约会流程
        result = await self._run_date(group_id, initiator_id, target_id, initiator_name, target_name)
        
        # 删除邀请
        del self.date_confirmations[group_id_str][target_id]
        
        # 构建响应消息
        response = f"⚡ 管理员强制完成约会：{initiator_name} 和 {target_name}\n\n"
        for event_info in result["events"]:
            response += f"【{event_info['name']}】\n{event_info['description']}\n\n"
        
        response += f"✨ {initiator_name} 对 {target_name} 的好感度变化: +{result['user_a_to_b_change']}\n"
        response += f"✨ {target_name} 对 {initiator_name} 的好感度变化: +{result['user_b_to_a_change']}\n\n"
        
        if result["user_a_to_b_level_up"]:
            response += f"🎉 {initiator_name} 对 {target_name} 的关系提升为: {result['user_a_to_b_level_after']}\n"
        if result["user_b_to_a_level_up"]:
            response += f"🎉 {target_name} 对 {initiator_name} 的关系提升为: {result['user_b_to_a_level_after']}\n"
        
        yield event.plain_result(response)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("约会")
    async def admin_create_date(self, event: AstrMessageEvent):
        """强行给两个用户约会"""
        # 解析两个目标用户
        target_ids = []
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                target_ids.append(str(comp.qq))
        
        if len(target_ids) < 2:
            yield event.plain_result("❌ 请@两个用户")
            return
        
        user_a_id, user_b_id = target_ids[:2]
        
        # 不能是同一个用户
        if user_a_id == user_b_id:
            yield event.plain_result("❌ 不能强制同一个用户约会哦~杂鱼酱❤~")
            return
        
        group_id = str(event.message_obj.group_id)
        
        # 获取用户名称
        user_a_name = await self._get_at_user_name(event, user_a_id)
        user_b_name = await self._get_at_user_name(event, user_b_id)
        
        # 运行约会流程
        result = await self._run_date(group_id, user_a_id, user_b_id, user_a_name, user_b_name)
        
        # 构建响应消息
        response = f"⚡ 管理员强制约会：{user_a_name} 和 {user_b_name}\n\n"
        for event_info in result["events"]:
            response += f"【{event_info['name']}】\n{event_info['description']}\n\n"
        
        response += f"✨ {user_a_name} 对 {user_b_name} 的好感度变化: +{result['user_a_to_b_change']}\n"
        response += f"✨ {user_b_name} 对 {user_a_name} 的好感度变化: +{result['user_b_to_a_change']}\n\n"
        
        if result["user_a_to_b_level_up"]:
            response += f"🎉 {user_a_name} 对 {user_b_name} 的关系提升为: {result['user_a_to_b_level_after']}\n"
        if result["user_b_to_a_level_up"]:
            response += f"🎉 {user_b_name} 对 {user_a_name} 的关系提升为: {result['user_b_to_a_level_after']}\n"
        
        yield event.plain_result(response)

        #endregion

        #region 社交事件
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("查阅社交邀请")
    async def admin_view_social_invites(self, event: AstrMessageEvent):
        """查看所有社交邀请"""
        now = datetime.now(SHANGHAI_TZ)
        response = "📊 全群社交邀请列表:\n\n"
        
        for group_id, invites in self.social_invitations.items():
            # 获取群组名称
            try:
                group_info = await self.context.get_group_info(int(group_id))
                group_name = group_info.group_name
            except:
                group_name = f"群组 {group_id}"
            
            response += f"【{group_name}】\n"
            
            for target_id, invite in invites.items():
                # 检查是否过期
                if now - invite['created_at'] > timedelta(minutes=10):
                    continue
                
                try:
                    initiator_name = await self._get_at_user_name(event, invite['initiator_id'])
                    target_name = await self._get_at_user_name(event, target_id)
                except:
                    initiator_name = f"用户{invite['initiator_id'][-4:]}"
                    target_name = f"用户{target_id[-4:]}"
                
                elapsed = now - invite['created_at']
                remaining = max(0, 10 - int(elapsed.total_seconds() / 60))
                
                response += (
                    f"- {initiator_name} → {target_name}: {invite['event_name']}\n"
                    f"  验证码: {invite['confirmation_code']}\n"
                    f"  剩余时间: {remaining}分钟\n"
                )
        
        # 使用文本转图片
        image_paths = await self.text_to_images(
            text=response,
            title="全群社交邀请"
        )
        
        for path in image_paths:
            yield event.image_result(path)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("强制社交同意")
    async def admin_accept_social(self, event: AstrMessageEvent):
        """强制同意社交邀请"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误: /WACadmin 强制社交同意 @用户 <验证码>")
            return
        
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@目标用户")
            return
        
        confirmation_code = parts[2]
        group_id = str(event.message_obj.group_id)
        group_id_str = str(group_id)
        
        # 获取邀请
        if (group_id_str not in self.social_invitations or 
            target_id not in self.social_invitations[group_id_str]):
            yield event.plain_result("❌ 该用户没有待处理的社交邀请")
            return
        
        invitation = self.social_invitations[group_id_str][target_id]
        
        # 检查验证码
        if confirmation_code != invitation["confirmation_code"]:
            yield event.plain_result(f"❌ 验证码错误！正确的验证码是: {invitation['confirmation_code']}")
            return
        
        # 执行社交事件
        initiator_id = invitation["initiator_id"]
        event_name = invitation["event_name"]
        
        async for result in self._execute_social_event(
            event, group_id, initiator_id, target_id, event_name
        ):
            yield result
        
        # 删除邀请
        del self.social_invitations[group_id_str][target_id]

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("强制社交")
    async def admin_force_social(self, event: AstrMessageEvent):
        """强制两个用户进行社交"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误: /WACadmin 强制社交 <事件名> @用户A @用户B")
            return
        
        event_name = parts[2]
        if event_name not in SOCIAL_EVENTS:
            yield event.plain_result(f"❌ 未知社交事件，可用事件: {', '.join(SOCIAL_EVENTS.keys())}")
            return
        
        # 解析两个目标用户
        target_ids = []
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                target_ids.append(str(comp.qq))
        
        if len(target_ids) < 2:
            yield event.plain_result("❌ 请@两个用户")
            return
        
        user_a_id, user_b_id = target_ids[:2]
        group_id = str(event.message_obj.group_id)
        
        # 执行社交事件
        async for result in self._execute_social_event(
            event, group_id, user_a_id, user_b_id, event_name, force=True
        ):
            yield result
        #endregion
    #endregion
    
    #region 管理员数据管理
    #region 功能数据
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("添加金币")
    async def add_coins(self, event: AstrMessageEvent):
        """添加金币到指定用户"""
        async for result in self._handle_coin_operation(event, "add"):
            yield result

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("删除金币")
    async def remove_coins(self, event: AstrMessageEvent):
        """从指定用户删除金币"""
        async for result in self._handle_coin_operation(event, "remove"):
            yield result

    async def _handle_coin_operation(self, event, operation):
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误: /WACadmin <添加金币|删除金币> <金额> @用户 [银行|钱包]")
            return
    
        try:
            amount = float(parts[2])
        except ValueError:
            yield event.plain_result("❌ 金额必须是数字")
            return
    
        if amount <= 0:
            yield event.plain_result("❌ 金额必须大于0")
            return
    
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@目标用户")
            return
    
        # 确定存储位置（默认钱包）
        location = "coins"
        if len(parts) > 3 and parts[3] in ["银行", "bank"]:
            location = "bank"
    
        group_id = str(event.message_obj.group_id)
        user_data = self._get_user_data(group_id, target_id)
    
        # 执行操作
        if operation == "add":
            user_data[location] += amount
            action = "添加"
        else:
            if user_data[location] < amount:
                user_data[location] = 0
            else:
                user_data[location] -= amount
            action = "删除"
    
        # 保存数据
        self._save_user_data(group_id, target_id, user_data)
    
        target_name = await self._get_at_user_name(event, target_id)
        location_name = "钱包" if location == "coins" else "银行"
        yield event.plain_result(f"✅ 已{action} {amount}金币 到 {target_name} 的{location_name}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("解放")
    async def free_user(self, event: AstrMessageEvent):
        """解放用户（移除契约状态）"""
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@要解放的用户")
            return
    
        group_id = str(event.message_obj.group_id)
        user_data = self._get_user_data(group_id, target_id)
    
        # 检查用户状态
        if user_data["contracted_by"] is None and not user_data.get("is_permanent", False):
            yield event.plain_result("❌ 该用户已经是自由状态")
            return
    
        # 更新用户状态
        original_owner = user_data["contracted_by"]
        user_data["contracted_by"] = None
        user_data["is_permanent"] = False
    
        # 从原主人处移除
        if original_owner:
            owner_data = self._get_user_data(group_id, original_owner)
            if target_id in owner_data["contractors"]:
                owner_data["contractors"].remove(target_id)
            if target_id in owner_data.get("permanent_contractors", []):
                owner_data["permanent_contractors"].remove(target_id)
        
            # 保存原主人数据
            self._save_user_data(group_id, original_owner, owner_data)
    
        # 保存用户数据
        self._save_user_data(group_id, target_id, user_data)
    
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已成功解放 {target_name}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("添加道具")
    async def add_prop(self, event: AstrMessageEvent):
        """添加道具到用户背包"""
        async for result in self._handle_prop_operation(event, "add"):
            yield result

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("扣除道具")
    async def remove_prop(self, event: AstrMessageEvent):
        """从用户背包扣除道具"""
        async for result in self._handle_prop_operation(event, "remove"):
            yield result  

    async def _handle_prop_operation(self, event, operation):
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result(f"❌ 格式错误: /WACadmin <{operation}道具> <道具名> [数量] @用户")
            return
    
        prop_name = parts[2]
        quantity = 1
    
        # 解析数量
        if len(parts) >= 4 and parts[3].isdigit():
            quantity = int(parts[3])
            if quantity <= 0:
                yield event.plain_result("❌ 数量必须大于0")
                return
    
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@目标用户")
            return
    
        group_id = str(event.message_obj.group_id)
        user_props = self._get_user_props(group_id, target_id)
    
        # 执行操作
        current = user_props.get(prop_name, 0)
        if operation == "add":
            user_props[prop_name] = current + quantity
            action = "添加"
        else:
            if current < quantity:
               user_props[prop_name] = 0
            else:
                user_props[prop_name] = current - quantity
            action = "扣除"
    
        # 保存数据
        self._update_user_props(group_id, target_id, user_props)
    
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已{action} {quantity}个{prop_name} 到 {target_name} 的背包")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("添加好感度")
    async def add_favorability(self, event: AstrMessageEvent):
        """增加用户A对用户B的好感度"""
        async for result in self._handle_favorability_operation(event, "add"):
            yield result

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("减少好感度")
    async def remove_favorability(self, event: AstrMessageEvent):
        """减少用户A对用户B的好感度"""
        async for result in self._handle_favorability_operation(event, "remove"):
            yield result

    async def _handle_favorability_operation(self, event, operation):
        parts = event.message_str.strip().split()
        if len(parts) < 4:
            yield event.plain_result(f"❌ 格式错误: /WACadmin <{operation}好感度> <数值> @用户A @用户B")
            return
    
        try:
            amount = int(parts[2])
        except ValueError:
            yield event.plain_result("❌ 数值必须是整数")
            return
    
        if amount <= 0:
            yield event.plain_result("❌ 数值必须大于0")
            return
    
        # 解析目标用户
        target_ids = []
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                target_ids.append(str(comp.qq))
    
        if len(target_ids) < 2:
            yield event.plain_result("❌ 请@两个用户（用户A和用户B）")
            return
    
        user_a_id, user_b_id = target_ids[:2]
    
        group_id = str(event.message_obj.group_id)
    
        # 执行操作
        if operation == "add":
            new_value = self._update_favorability(group_id, user_a_id, user_b_id, amount)
            action = "增加"
        else:
            new_value = self._update_favorability(group_id, user_a_id, user_b_id, -amount)
            action = "减少"
    
        user_a_name = await self._get_at_user_name(event, user_a_id)
        user_b_name = await self._get_at_user_name(event, user_b_id)
        yield event.plain_result(f"✅ 已{action} {user_a_name} 对 {user_b_name} 的好感度 {amount}点\n当前好感度: {new_value}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("创建关系")
    async def create_relation(self, event: AstrMessageEvent):
        """创建用户间的关系"""
        async for result in self._handle_relation_operation(event, "create"):
            yield result

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("删除关系")
    async def wacadmmin_remove_relation(self, event: AstrMessageEvent):
        """删除用户间的关系"""
        async for result in self._handle_relation_operation(event, "remove"):
            yield result

    #region 删除关系实现
    async def _handle_relation_operation(self, event, operation):
        parts = event.message_str.strip().split()
    
        # 删除关系不需要指定关系名
        if operation == "remove" and len(parts) < 2:
            yield event.plain_result("❌ 格式错误: /WACadmin 删除关系 @用户A @用户B")
            return
    
        # 创建关系需要指定关系名
        if operation == "create" and len(parts) < 3:
            yield event.plain_result("❌ 格式错误: /WACadmin 创建关系 <关系名> @用户A @用户B")
            return
    
        # 解析关系名（仅创建时需要）
        relation_name = parts[2] if operation == "create" else None
    
        # 解析目标用户
        target_ids = []
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                target_ids.append(str(comp.qq))
    
        if len(target_ids) < 2:
            yield event.plain_result("❌ 请@两个用户")
            return
    
        user_a_id, user_b_id = target_ids[:2]
        group_id = str(event.message_obj.group_id)
    
        # 检查双方是否已有关系
        existing_relation = self.get_special_relation(group_id, user_a_id, user_b_id)
    
        # 执行操作
        if operation == "create":
            # 添加关系前检查是否已有关系
            if existing_relation:
                user_a_name = await self._get_at_user_name(event, user_a_id)
                user_b_name = await self._get_at_user_name(event, user_b_id)
                yield event.plain_result(f"❌ {user_a_name} 和 {user_b_name} 已有 {existing_relation} 关系，无法重复添加")
                return
        
            self.add_relation(group_id, user_a_id, user_b_id, relation_name)
            action = "创建"
        else:  # operation == "remove"
            # 删除关系前检查是否有关
            if not existing_relation:
                user_a_name = await self._get_at_user_name(event, user_a_id)
                user_b_name = await self._get_at_user_name(event, user_b_id)
                yield event.plain_result(f"❌ {user_a_name} 和 {user_b_name} 没有特殊关系，无需删除")
                return
        
            # 删除所有关系（不指定具体类型）
            self.remove_any_relation(group_id, user_a_id, user_b_id)
            action = "删除"
    
        user_a_name = await self._get_at_user_name(event, user_a_id)
        user_b_name = await self._get_at_user_name(event, user_b_id)
    
        if operation == "create":
            yield event.plain_result(f"✅ 已{action} {user_a_name} 和 {user_b_name} 的 {relation_name} 关系")
        else:
            yield event.plain_result(f"✅ 已{action} {user_a_name} 和 {user_b_name} 双方互相的所有特殊关系")

    def remove_any_relation(self, group_id: str, user_id: str, target_id: str):
        """删除两个用户之间的所有特殊关系"""
        user_data = self._get_user_social_data(group_id, user_id)
        target_data = self._get_user_social_data(group_id, target_id)
    
        # 遍历所有关系类型
        for rel_type in user_data["relations"]:
            # 从发起方移除
            if str(target_id) in user_data["relations"][rel_type]:
                user_data["relations"][rel_type].remove(str(target_id))
        
            # 从目标方移除
            if str(user_id) in target_data["relations"][rel_type]:
                target_data["relations"][rel_type].remove(str(user_id))
    
        # 保存数据
        social_data = self._load_social_data()
        social_data.setdefault(str(group_id), {})[str(user_id)] = user_data
        social_data[str(group_id)][str(target_id)] = target_data
        self._save_social_data(social_data)
    
        # 检查是否有结婚证
        certificate_data = self._load_certificate_data()
        group_certs = certificate_data.get(group_id, {})
        user_certs = group_certs.get(user_id, {})
        target_certs = group_certs.get(target_id, {})
        
        # 查找双方的结婚证
        marriage_cert_id = None
        for cert_id, cert_info in user_certs.items():
            if cert_info["type"] == "结婚证" and (
                (cert_info["applicant"] == user_id and cert_info["target"] == target_id) or
                (cert_info["applicant"] == target_id and cert_info["target"] == user_id)
            ):
                marriage_cert_id = cert_id
                break
        
        # 如果找到结婚证，转为离婚证
        if marriage_cert_id:
            # 更新用户证件
            user_certs[marriage_cert_id]["type"] = "离婚证"
            user_certs[marriage_cert_id]["status"] = "失效"
            
            # 更新对方证件
            if target_id in group_certs and marriage_cert_id in group_certs[target_id]:
                group_certs[target_id][marriage_cert_id]["type"] = "离婚证"
                group_certs[target_id][marriage_cert_id]["status"] = "失效"
            
            # 保存数据
            self._save_certificate_data(certificate_data)

        # 记录日志
        self._log_operation("info", 
            f"移除所有关系: group={group_id}, user={user_id}, "
            f"target={target_id}"
        )
    #endregion

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("清空计时")
    async def clear_timer(self, event: AstrMessageEvent):
        """清空用户的时间记录"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误: /WACadmin 清空计时 <计时类型> @用户")
            yield event.plain_result("可用计时类型: 签到, 打工, 抢劫, 红星制裁, 市场侵袭, 彩票")
            return
    
        timer_type = parts[2]
        valid_types = ["签到", "打工", "抢劫", "红星制裁", "市场侵袭", "彩票"]
    
        if timer_type not in valid_types:
            yield event.plain_result(f"❌ 无效计时类型，可用: {', '.join(valid_types)}")
            return
    
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            yield event.plain_result("❌ 请@目标用户")
            return
    
        group_id = str(event.message_obj.group_id)
        time_data = self._get_user_time_data(group_id, target_id)
    
        # 映射计时类型到字段名
        field_map = {
            "签到": "last_sign",
            "打工": "last_work",
            "抢劫": "last_robbery",
            "红星制裁": "last_red_star_use",
            "市场侵袭": "last_market_invasion_use",
            "彩票": "lottery_count"
        }
    
        field = field_map[timer_type]
    
        # 清空计时
        if field == "lottery_count":
            time_data[field] = 0
        else:
            time_data[field] = None
    
        # 保存数据
        self._save_user_time_data(group_id, target_id, time_data)
    
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已清空 {target_name} 的 {timer_type} 计时")
    #endregion

    #region 数据删除管理
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("删除用户")
    async def delete_user(self, event: AstrMessageEvent):
        """删除用户数据"""
        # 首先清理所有过期请求
        current_time = time.time()
        expired_keys = [
            key for key, pending in self.pending_confirmations.items()
            if current_time - pending["timestamp"] > 300
        ]
        for key in expired_keys:
            del self.pending_confirmations[key]
    
        parts = event.message_str.strip().split()
        target_id = None
    
        # 解析目标用户
        if len(parts) >= 3 and parts[2].isdigit():
            target_id = parts[2]
        else:
            # 尝试从@消息解析
            target_id = self._parse_at_target(event)
    
        if not target_id:
            yield event.plain_result("❌ 请@用户或提供QQ号")
            return
    
        group_id = str(event.message_obj.group_id)
        admin_id = str(event.get_sender_id())
    
        # 生成唯一确认码
        confirmation_code = str(random.randint(1000, 9999))
    
        # 存储待确认操作
        self.pending_confirmations[admin_id] = {
            "type": "delete_user",
            "group_id": group_id,
            "target_id": target_id,
            "code": confirmation_code,
            "timestamp": time.time()
        }
    
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(
            f"⚠️ 即将删除 {target_name}({target_id}) 的所有数据\n"
            f"此操作不可逆！请回复以下确认码完成操作：\n"
            f"{confirmation_code}"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("群聊数据清空")
    async def clear_group_data(self, event: AstrMessageEvent):
        """清空群聊所有数据"""
        # 首先清理所有过期请求
        current_time = time.time()
        expired_keys = [
            key for key, pending in self.pending_confirmations.items()
            if current_time - pending["timestamp"] > 300
        ]
        for key in expired_keys:
            del self.pending_confirmations[key]
    
        parts = event.message_str.strip().split()
        group_id = str(event.message_obj.group_id)
        admin_id = str(event.get_sender_id())
    
        # 解析群号（默认当前群聊）
        target_group = group_id
        if len(parts) >= 3 and parts[2].isdigit():
            target_group = parts[2]
    
        # 生成唯一确认码
        confirmation_code = str(random.randint(1000, 9999))
    
        # 存储待确认操作
        self.pending_confirmations[admin_id] = {
            "type": "clear_group",
            "group_id": target_group,
            "code": confirmation_code,
            "timestamp": time.time()
        }
    
        yield event.plain_result(
            f"⚠️ 即将清空群组 {target_group} 的所有数据\n"
            f"此操作不可逆！请回复以下确认码完成操作：\n"
            f"{confirmation_code}"
        )

    #region 数据删除实现
    async def _execute_delete_user(self, group_id, target_id, admin_id):
        """执行删除用户操作"""
        # 加载数据
        data = self._load_data()
        prop_data = self._load_prop_data()
        social_data = self._load_social_data()
        time_data = self._load_time_data()
    
        # 从主数据删除
        if group_id in data and target_id in data[group_id]:
            user_data = data[group_id][target_id]
        
            # 更新契约关系
            if user_data["contracted_by"]:
                owner_id = user_data["contracted_by"]
                if owner_id in data[group_id]:
                    owner_data = data[group_id][owner_id]
                    if target_id in owner_data["contractors"]:
                        owner_data["contractors"].remove(target_id)
                    if target_id in owner_data.get("permanent_contractors", []):
                        owner_data["permanent_contractors"].remove(target_id)
        
            # 删除用户数据
            del data[group_id][target_id]
            if not data[group_id]:
                del data[group_id]
    
        # 从道具数据删除
        if group_id in prop_data and target_id in prop_data[group_id]:
            del prop_data[group_id][target_id]
            if not prop_data[group_id]:
                del prop_data[group_id]
    
        # 从社交数据删除
        group_id_str = str(group_id)
        if group_id_str in social_data:
            # 删除用户的好感度数据
            if target_id in social_data[group_id_str]:
                # 删除其他用户对TA的好感度
                for uid, user_social in social_data[group_id_str].items():
                    if target_id in user_social["favorability"]:
                        del user_social["favorability"][target_id]
            
                # 删除用户的好感度数据
                del social_data[group_id_str][target_id]
        
            # 删除用户的关系数据
            for uid, user_social in social_data[group_id_str].items():
                for rel_type, relations in user_social["relations"].items():
                    if target_id in relations:
                        relations.remove(target_id)
        
            # 清理空数据
            if not social_data[group_id_str]:
                del social_data[group_id_str]
    
        # 从时间数据删除
        if group_id in time_data and target_id in time_data[group_id]:
            del time_data[group_id][target_id]
            if not time_data[group_id]:
                del time_data[group_id]
    
        # 从用户股票数据删除
        group_id_str = str(group_id)
        target_id_str = str(target_id)
        if group_id_str in self.stock_user_data and target_id_str in self.stock_user_data[group_id_str]:
            # 直接删除用户股票数据
            del self.stock_user_data[group_id_str][target_id_str]
        
            # 如果群组股票数据为空，删除整个群组条目
            if not self.stock_user_data[group_id_str]:
                del self.stock_user_data[group_id_str]
        
            # 保存用户股票数据
            self._save_user_stock_data()

        # 保存所有数据
        self._save_data(data)
        self._save_prop_data(prop_data)
        self._save_social_data(social_data)
        self._save_time_data(time_data)
    
        # 记录日志
        self._log_operation("warning", 
            f"删除用户: group={group_id}, user={target_id}, "
            f"by_admin={admin_id}"
        )
    
        target_name = self._get_user_name(target_id)
        yield f"✅ 已成功删除用户 {target_name}({target_id}) 的所有数据"

    async def _execute_clear_group(self, group_id, admin_id):
        """执行清空群聊操作"""
        # 加载数据
        data = self._load_data()
        prop_data = self._load_prop_data()
        social_data = self._load_social_data()
        time_data = self._load_time_data()
    
        # 删除主数据
        if group_id in data:
            del data[group_id]
    
        # 删除道具数据
        if group_id in prop_data:
            del prop_data[group_id]
    
        # 删除社交数据
        if str(group_id) in social_data:
            del social_data[str(group_id)]
    
        # 删除时间数据
        if group_id in time_data:
            del time_data[group_id]

        # 删除用户股票数据
        if group_id in self.stock_user_data:
            # 直接删除整个群组的股票数据
            del self.stock_user_data[group_id]
            self._save_user_stock_data()
    
        # 保存所有数据
        self._save_data(data)
        self._save_prop_data(prop_data)
        self._save_social_data(social_data)
        self._save_time_data(time_data)
    
        # 记录日志
        self._log_operation("warning", 
            f"清空群组数据: group={group_id}, "
            f"by_admin={admin_id}"
        )
    
        yield f"✅ 已成功清空群组 {group_id} 的所有数据"

    def _get_user_name(self, user_id):
        """获取用户名（简化版）"""
        # 实际实现中可能需要查询用户信息
        return f"用户{user_id[-4:]}"
    #endregion

    #endregion

    def _save_user_data(self, group_id: str, user_id: str, user_data: dict):
        """保存用户数据"""
        try:
            data = self._load_data()
            group_data = data.setdefault(group_id, {})
            group_data[user_id] = user_data
            self._save_data(data)
        except Exception as e:
            self._log_operation("error", f"保存用户数据失败: {str(e)}")

    #endregion

    #region 管理员辅助管理
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("确认")
    async def confirm_action(self, event: AstrMessageEvent):
        """确认危险操作"""
        admin_id = str(event.get_sender_id())
    
        # 正确提取确认码
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 请提供确认码")
            return
    
        confirmation_code = parts[-1]  # 取最后一个部分作为确认码
    
        # 首先清理所有过期请求
        current_time = time.time()
        expired_keys = [
            key for key, pending in self.pending_confirmations.items()
            if current_time - pending["timestamp"] > 300
        ]
        for key in expired_keys:
            del self.pending_confirmations[key]
    
        # 检查是否有待确认操作
        if admin_id not in self.pending_confirmations:
            yield event.plain_result("❌ 没有待确认的操作")
            return
    
        pending = self.pending_confirmations[admin_id]
    
        # 检查确认码是否匹配
        if confirmation_code != pending["code"]:
            yield event.plain_result(f"❌ 确认码错误 (输入: {confirmation_code}, 需要: {pending['code']})")
            return
    
        # 检查操作是否超时（5分钟）
        if time.time() - pending["timestamp"] > 300:
            del self.pending_confirmations[admin_id]
            yield event.plain_result("❌ 操作已超时，请重新发起")
            return
    
        # 执行操作
        if pending["type"] == "delete_user":
            yield event.plain_result(f"✅ 执行删除用户数据的操作中。。。")
            async for result in self._execute_delete_user(
                pending["group_id"], 
                pending["target_id"],
                admin_id
            ):
                yield result
        elif pending["type"] == "clear_group":
            yield event.plain_result(f"✅ 执行删除群聊数据的操作中。。。")
            async for result in self._execute_clear_group(
                pending["group_id"],
                admin_id
            ):
                yield result
    
        # 删除待确认记录
        del self.pending_confirmations[admin_id]

    @admin_commands.command("help")
    async def admin_help(self, event: AstrMessageEvent):
        """显示管理员帮助（图片版）"""
        help_text = """
🛠️ WACadmin 管理员命令帮助 🛠️

============【用户授权】============
/WACadmin 授权 <等级> <@用户|QQ号>  [群号]
  - 授权用户使用管理命令（等级1-4）
  - 等级1: 查阅管理员, 等级2: 股票管理员, 等级3: 操作管理员, 等级4: 数据管理员

====================
/WACadmin 取消授权 <@用户|QQ号> [群号]
  - 取消用户的管理权限

====================
/WACadmin 查看授权
  - 查看本群授权用户列表

===========【黑名单管理】===========
/WACadmin 拉黑用户 <@用户|QQ号>
  - 拉黑用户（拒绝响应其请求）

====================
/WACadmin 解除拉黑用户 <@用户|QQ号>
  - 解除用户拉黑

====================
/WACadmin 拉黑群聊 [群号]
  - 拉黑整个群聊（拒绝响应所有请求）

====================
/WACadmin 解除拉黑群聊 [群号]
  - 解除群聊拉黑

====================
/WACadmin 查看黑名单
  - 查看所有黑名单条目
  
============【金币管理】============
/WACadmin 添加金币 <金额> @用户 [银行|钱包]
  - 添加金币到用户的钱包或银行（默认钱包）

====================
/WACadmin 删除金币 <金额> @用户 [银行|钱包]
  - 从用户的钱包或银行删除金币

===========【用户状态管理】===========
/WACadmin 解放 @用户
  - 解除用户的契约状态（包括永久绑定）

============【道具管理】============
/WACadmin 添加道具 <道具名> [数量] @用户
  - 添加道具到用户背包

====================  
/WACadmin 扣除道具 <道具名> [数量] @用户
  - 从用户背包扣除道具

===========【好感度管理】===========
/WACadmin 添加好感度 <数值> @用户A @用户B
  - 增加用户A对用户B的好感度

==================== 
/WACadmin 减少好感度 <数值> @用户A @用户B
  - 减少用户A对用户B的好感度

============【关系管理】============
/WACadmin 创建关系 <关系名> @用户A @用户B
  - 创建用户间的关系（恋人、兄弟等）

====================
/WACadmin 删除关系 @用户A @用户B
  - 删除用户间的关系

============【约会管理】============
/WACadmin 强接约会 @用户 <验证码>  
  - 强制替用户接受约会

====================  
/WACadmin 约会 @用户A @用户B
  - 强行给两个用户约会

====================
/WACadmin 查阅约会邀请
  - 列出所有有效的约会邀请

============【社交管理】============
/WACadmin 查阅社交邀请
  - 查看全群社交邀请

====================
/WACadmin 强制社交同意 @用户 <验证码>
  - 强制同意社交邀请

====================
/WACadmin 强制社交 <事件名> @用户A @用户B
  - 强制进行社交活动

============【股票管理】============
/WACadmin 添加股票 <股票名> <初始价格> [波动率]
  - 添加新股票
  - 示例: /WACadmin 添加股票 字节跳动 300 0.15

====================
/WACadmin 删除股票 <股票名>
  - 删除股票（强制卖出所有用户持仓）
  - 示例: /WACadmin 删除股票 小鹏电车

====================
/WACadmin 设置股价 <股票名> <新价格>
  - 手动设置股票价格
  - 示例: /WACadmin 设置股价 茅台科技 2000
  
============【时间管理】============
/WACadmin 清空计时 <计时类型> @用户
  - 清空用户的时间记录（签到、打工等）

============【数据管理】============
/WACadmin 删除用户 <@用户|QQ号>
  - 删除用户的所有数据（需二次确认）

====================  
/WACadmin 群聊数据清空 [群号]
  - 清空群聊所有数据（需双重确认）

====================  
/WACadmin 确认 <验证码>
  - 确认命令

============【帮助】============
/WACadmin help
  - 显示此帮助信息
        """.strip()
        
        # 生成所有图片
        image_paths = await self.text_to_images(
            text=help_text,
            title="WACadmin 管理员帮助"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)
    #endregion

    #region 管理员授权
    #region 授权命令
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("授权")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def authorize_user(self, event: AstrMessageEvent):
        """授权用户使用管理命令"""
        parts = event.message_str.strip().split()
        if len(parts) < 4:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 授权 <等级> <@用户|QQ号> [群号]")
            yield event.plain_result(f"可用等级: {', '.join([f'{k}-{v}' for k, v in AUTH_LEVELS.items()])}")
            return
        
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            # 尝试解析QQ号
            if parts[3].isdigit():
                target_id = parts[3]
            else:
                yield event.plain_result("❌ 请@用户或提供QQ号")
                return
        
        # 解析授权等级
        try:
            auth_level = int(parts[2])
            if auth_level not in AUTH_LEVELS:
                yield event.plain_result(f"❌ 无效等级，可用等级: {', '.join(map(str, AUTH_LEVELS.keys()))}")
                return
        except ValueError:
            yield event.plain_result("❌ 请输入有效的等级数字")
            return
        
        # 解析群号（默认当前群）
        group_id = event.message_obj.group_id
        if len(parts) > 4 and parts[4].isdigit():
            group_id = int(parts[4])
        
        # 设置授权
        self._set_user_auth_level(group_id, target_id, auth_level)
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(
            f"✅ 已授权 {target_name} 为 {AUTH_LEVELS[auth_level]}\n"
            f"- 等级: {auth_level}\n"
            f"- 权限: {AUTH_LEVELS[auth_level]}"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("取消授权")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def unauthorize_user(self, event: AstrMessageEvent):
        """取消用户管理权限"""
        parts = event.message_str.strip().split()
        if len(parts) < 3:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 取消授权 <@用户|QQ号> [群号]")
            return
    
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            # 尝试解析QQ号
            if parts[2].isdigit():
                target_id = parts[2]
            else:
                yield event.plain_result("❌ 请@用户或提供QQ号")
                return
    
        # 解析群号（默认当前群）
        group_id = event.message_obj.group_id
        if len(parts) > 3 and parts[3].isdigit():
            group_id = int(parts[3])
    
        # 移除授权
        self._remove_user_auth(group_id, target_id)
    
        # 确保数据保存
        try:
            self._save_auth_data()
        except Exception as e:
            self._log_operation("error", f"保存授权数据失败: {str(e)}")
            yield event.plain_result("❌ 取消授权失败，数据保存异常")
            return
    
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已取消 {target_name} 的所有管理权限")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("查看授权")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def list_authorized_users(self, event: AstrMessageEvent):
        """查看所有群的授权用户列表"""
        if not self.auth_data:
            yield event.plain_result("❌ 暂无任何授权用户")
            return
    
        response = "📝 全群授权用户列表：\n\n"
    
        # 获取所有群组信息
        group_info_cache = {}
    
        for group_id_str, users in self.auth_data.items():
            # 获取群组名称
            group_id = int(group_id_str)
            if group_id not in group_info_cache:
                try:
                    group_info = await self.context.get_group_info(group_id)
                    group_name = group_info.group_name
                    group_info_cache[group_id] = group_name
                except:
                    group_name = f"群组 {group_id}"
                    group_info_cache[group_id] = group_name
            else:
                group_name = group_info_cache[group_id]
        
            response += f"【{group_name} ({group_id})】\n"
        
            if not users:
                response += "  暂无授权用户\n"
                continue
        
            for user_id, level in users.items():
                try:
                    user_name = await self._get_at_user_name(event, user_id)
                except:
                    user_name = f"用户{user_id}"
            
                level_name = AUTH_LEVELS.get(level, f"未知等级({level})")
                response += f"  - {user_name} ({user_id}) - {level_name}\n"
        
            response += "\n"
    
        # 生成图片
        image_paths = await self.text_to_images(
            text=response,
            title="全群授权用户列表"
        )
    
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)
        #endregion    

    #region 授权用户命令组
    @filter.command_group("WACadmin-us")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def user_admin_commands(self, event: AstrMessageEvent):
        """授权用户命令组入口"""
        pass

    @user_admin_commands.command("help")
    async def user_admin_help(self, event: AstrMessageEvent):
        """授权用户帮助"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        auth_level = self._get_user_auth_level(group_id, user_id)
        
        if auth_level == 0:
            yield event.plain_result("❌ 您未被授权使用此命令")
            return
        
        response = f"🛠️ 授权用户帮助 (您的等级: {AUTH_LEVELS.get(auth_level, auth_level)})\n\n"
        response += "可用命令:\n"
        
        # 根据用户等级显示可用命令
        if auth_level >= 1:
            response += "- /WACadmin-us 查阅约会邀请\n"
            response += "- /WACadmin-us 查阅社交邀请\n"
        if auth_level >= 2:
            response += "- /WACadmin-us 添加股票 <股票名> <初始价格> [波动率]\n"
            response += "- /WACadmin-us 设置股价 <股票名> <新价格>\n"
        if auth_level >= 3:
            response += "- /WACadmin-us 拉黑用户 <@用户|QQ号>\n"
            response += "- /WACadmin-us 解除拉黑用户 <@用户|QQ号>\n"
            response += "- /WACadmin-us 查看黑名单\n"
            response += "- /WACadmin-us 强接约会 @用户 <验证码>\n"
            response += "- /WACadmin-us 约会 @用户A @用户B\n"
            response += "- /WACadmin-us 强制社交同意 @用户 <验证码>\n"
            response += "- /WACadmin-us 强制社交 <事件名> @用户A @用户B\n"
        if auth_level >= 4:
            response += "- /WACadmin-us 删除股票 <股票名>\n"
            response += "- /WACadmin-us 添加金币 <金额> @用户 [银行|钱包]\n"
            response += "- /WACadmin-us 删除金币 <金额> @用户 [银行|钱包]\n"
            response += "- /WACadmin-us 解放 @用户\n"
            response += "- /WACadmin-us 添加道具 <道具名> [数量] @用户\n"
            response += "- /WACadmin-us 扣除道具 <道具名> [数量] @用户\n"
            response += "- /WACadmin-us 添加好感度 <数值> @用户A @用户B\n"
            response += "- /WACadmin-us 减少好感度 <数值> @用户A @用户B\n"
            response += "- /WACadmin-us 创建关系 <关系名> @用户A @用户B\n"
            response += "- /WACadmin-us 删除关系 @用户A @用户B\n"
            response += "- /WACadmin-us 清空计时 <计时类型> @用户\n"
            response += "- /WACadmin-us 删除用户 <@用户|QQ号>\n"
            response += "- /WACadmin-us 确认 <验证码>\n"
        
        response += "\n使用 /WACadmin-us <命令> 执行操作"
        response += "\n可使用 /WACadmin help 查阅命令详情"
        yield event.plain_result(response)

    #region 授权用户命令组-等级1
    @user_admin_commands.command("查阅约会邀请")
    async def user_view_date_invitations(self, event: AstrMessageEvent):
        """查阅约会邀请（需要等级1）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 1:
            yield event.plain_result("❌ 需要查阅管理员(等级1)权限")
            return
        
        # 调用逻辑
        async for result in self.view_date_invitations(event):
            yield result 

    @user_admin_commands.command("查阅社交邀请")
    async def user_admin_view_social_invites(self, event: AstrMessageEvent):
        """查阅社交邀请（需要等级1）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 1:
            yield event.plain_result("❌ 需要查阅管理员(等级1)权限")
            return
        
        # 调用逻辑
        async for result in self.admin_view_social_invites(event):
            yield result
    #endregion

    #region 授权用户命令组-等级2
    @user_admin_commands.command("添加股票")
    async def user_add_stock(self, event: AstrMessageEvent):
        """添加新股票（需要等级2）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 2:
            yield event.plain_result("❌ 需要股票管理员(等级2)权限")
            return
        
        # 调用逻辑
        async for result in self.add_stock(event):
            yield result

    @user_admin_commands.command("设置股价")
    async def user_set_stock_price(self, event: AstrMessageEvent):
        """设置股票价格（需要等级3）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 2:
            yield event.plain_result("❌ 需要股票管理员(等级2)权限")
            return
        
        # 调用逻辑
        async for result in self.set_stock_price(event):
            yield result
    #endregion

    #region 授权用户命令组-等级3
    @user_admin_commands.command("强接约会")
    async def user_force_accept_date(self, event: AstrMessageEvent):
        """强制接受约会邀请（需要等级3）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.force_accept_date(event):
            yield result

    @user_admin_commands.command("约会")
    async def user_admin_create_date(self, event: AstrMessageEvent):
        """强制约会（需要等级3）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.admin_create_date(event):
            yield result

    @user_admin_commands.command("强制社交同意")
    async def user_admin_accept_social(self, event: AstrMessageEvent):
        """强制同意社交邀请（需要等级3）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.admin_accept_social(event):
            yield result

    @user_admin_commands.command("强制社交")
    async def user_admin_force_social(self, event: AstrMessageEvent):
        """强制进行社交活动（需要等级3）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.admin_force_social(event):
            yield result

    @user_admin_commands.command("拉黑用户")
    async def user_blacklist_user(self, event: AstrMessageEvent):
        """拉黑用户（拒绝响应其请求）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.blacklist_user(event):
            yield result

    @user_admin_commands.command("解除拉黑用户")
    async def user_unblacklist_user(self, event: AstrMessageEvent):
        """解除用户拉黑"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.unblacklist_user(event):
            yield result

    @user_admin_commands.command("查看黑名单")
    async def user_view_blacklist(self, event: AstrMessageEvent):
        """查看黑名单"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 3:
            yield event.plain_result("❌ 需要操作管理员(等级3)权限")
            return
        
        # 调用逻辑
        async for result in self.view_blacklist(event):
            yield result
    #endregion

    #region 授权用户命令组-等级4
    @user_admin_commands.command("删除股票")
    async def user_remove_stock(self, event: AstrMessageEvent):
        """删除股票（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.remove_stock(event):
            yield result

    @user_admin_commands.command("添加金币")
    async def user_add_coins(self, event: AstrMessageEvent):
        """添加金币（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.add_coins(event):
            yield result

    @user_admin_commands.command("删除金币")
    async def user_remove_coins(self, event: AstrMessageEvent):
        """删除金币（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.remove_coins(event):
            yield result

    @user_admin_commands.command("解放")
    async def user_free_user(self, event: AstrMessageEvent):
        """解放用户（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.free_user(event):
            yield result

    @user_admin_commands.command("添加道具")
    async def user_add_prop(self, event: AstrMessageEvent):
        """添加道具（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.add_prop(event):
            yield result

    @user_admin_commands.command("扣除道具")
    async def user_remove_prop(self, event: AstrMessageEvent):
        """扣除道具（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.remove_prop(event):
            yield result

    @user_admin_commands.command("添加好感度")
    async def user_add_favorability(self, event: AstrMessageEvent):
        """添加好感度（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.add_favorability(event):
            yield result

    @user_admin_commands.command("减少好感度")
    async def user_remove_favorability(self, event: AstrMessageEvent):
        """减少好感度（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.remove_favorability(event):
            yield result

    @user_admin_commands.command("创建关系")
    async def user_create_relation(self, event: AstrMessageEvent):
        """创建关系（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.create_relation(event):
            yield result

    @user_admin_commands.command("删除关系")
    async def user_remove_relation(self, event: AstrMessageEvent):
        """删除关系（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.remove_relation(event):
            yield result

    @user_admin_commands.command("清空计时")
    async def user_clear_timer(self, event: AstrMessageEvent):
        """清空计时（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.clear_timer(event):
            yield result

    @user_admin_commands.command("删除用户")
    async def user_delete_user(self, event: AstrMessageEvent):
        """删除用户（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.delete_user(event):
            yield result

    @user_admin_commands.command("确认")
    async def user_confirm_action(self, event: AstrMessageEvent):
        """确认操作（需要等级4）"""
        group_id = event.message_obj.group_id
        user_id = event.get_sender_id()
        
        # 检查授权等级
        auth_level = self._get_user_auth_level(group_id, user_id)
        if auth_level < 4:
            yield event.plain_result("❌ 需要数据管理员(等级4)权限")
            return
        
        # 调用逻辑
        async for result in self.confirm_action(event):
            yield result
    #endregion    
    #endregion

    #endregion

    #region 管理员黑名单管理
    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("拉黑用户")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def blacklist_user(self, event: AstrMessageEvent):
        """拉黑用户（拒绝响应其请求）"""
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 拉黑用户 <@用户|QQ号>")
            return
        
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            # 尝试解析QQ号
            if parts[1].isdigit():
                target_id = parts[1]
            else:
                yield event.plain_result("❌ 请@用户或提供QQ号")
                return
        
        # 解析群号
        group_id = event.message_obj.group_id
        group_id_str = str(group_id)
        target_id_str = str(target_id)
        
        # 初始化群组黑名单
        if group_id_str not in self.blacklist_data["users"]:
            self.blacklist_data["users"][group_id_str] = []
        
        # 添加用户到黑名单
        if target_id_str not in self.blacklist_data["users"][group_id_str]:
            self.blacklist_data["users"][group_id_str].append(target_id_str)
            self._save_blacklist_data()
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已拉黑用户 {target_name}\n- 群号: {group_id}\n- 该用户的所有请求将被忽略")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("拉黑群聊")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def blacklist_group(self, event: AstrMessageEvent):
        """拉黑群聊（拒绝响应所有请求）"""
        parts = event.message_str.strip().split()
        
        # 默认使用当前群
        group_id = event.message_obj.group_id
    
        # 检查是否有群号参数
        if len(parts) > 2 and parts[2].isdigit():
            group_id = int(parts[2])
        elif len(parts) > 1 and parts[1].isdigit():
            group_id = int(parts[1])
    
        group_id_str = str(group_id)
        
        # 添加群聊到黑名单
        if group_id_str not in self.blacklist_data["groups"]:
            self.blacklist_data["groups"].append(group_id_str)
            self._save_blacklist_data()
        
        try:
            group_info = await self.context.get_group_info(group_id)
            group_name = group_info.group_name
        except:
            group_name = f"群组 {group_id}"
        
        yield event.plain_result(f"✅ 已拉黑群聊 {group_name}\n- 群号: {group_id}\n- 该群的所有请求将被忽略")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("解除拉黑用户")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def unblacklist_user(self, event: AstrMessageEvent):
        """解除用户拉黑"""
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("❌ 格式错误，请使用：/WACadmin 解除拉黑用户 <@用户|QQ号> [群号]")
            return
        
        # 解析目标用户
        target_id = self._parse_at_target(event)
        if not target_id:
            # 尝试解析QQ号
            if parts[1].isdigit():
                target_id = parts[1]
            else:
                yield event.plain_result("❌ 请@用户或提供QQ号")
                return
        
        # 解析群号（默认当前群）
        group_id = event.message_obj.group_id
        group_id_str = str(group_id)
        target_id_str = str(target_id)
        
        # 从黑名单中移除用户
        if group_id_str in self.blacklist_data["users"]:
            if target_id_str in self.blacklist_data["users"][group_id_str]:
                self.blacklist_data["users"][group_id_str].remove(target_id_str)
                self._save_blacklist_data()
                
                # 如果群组黑名单为空，删除整个群组条目
                if not self.blacklist_data["users"][group_id_str]:
                    del self.blacklist_data["users"][group_id_str]
        
        target_name = await self._get_at_user_name(event, target_id)
        yield event.plain_result(f"✅ 已解除拉黑用户 {target_name}\n- 群号: {group_id}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("解除拉黑群聊")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def unblacklist_group(self, event: AstrMessageEvent):
        """解除群聊拉黑"""
        parts = event.message_str.strip().split()
        
        # 默认使用当前群
        group_id = event.message_obj.group_id
    
        # 检查是否有群号参数
        if len(parts) > 2 and parts[2].isdigit():
            group_id = int(parts[2])
        elif len(parts) > 1 and parts[1].isdigit():
            group_id = int(parts[1])
    
        group_id_str = str(group_id)
        
        # 从黑名单中移除群聊
        if group_id_str in self.blacklist_data["groups"]:
            self.blacklist_data["groups"].remove(group_id_str)
            self._save_blacklist_data()
        
        try:
            group_info = await self.context.get_group_info(group_id)
            group_name = group_info.group_name
        except:
            group_name = f"群组 {group_id}"
        
        yield event.plain_result(f"✅ 已解除拉黑群聊 {group_name}\n- 群号: {group_id}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @admin_commands.command("查看黑名单")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def view_blacklist(self, event: AstrMessageEvent):
        """查看黑名单"""
        response = "🚫 黑名单列表\n\n"
        
        # 拉黑的群聊
        if self.blacklist_data["groups"]:
            response += "【拉黑的群聊】\n"
            for group_id in self.blacklist_data["groups"]:
                try:
                    group_info = await self.context.get_group_info(int(group_id))
                    group_name = group_info.group_name
                except:
                    group_name = f"群组 {group_id}"
                response += f"- {group_name} ({group_id})\n"
            response += "\n"
        else:
            response += "【拉黑的群聊】\n- 暂无\n\n"
        
        # 拉黑的用户
        if self.blacklist_data["users"]:
            response += "【拉黑的用户】\n"
            for group_id, users in self.blacklist_data["users"].items():
                try:
                    group_info = await self.context.get_group_info(int(group_id))
                    group_name = group_info.group_name
                except:
                    group_name = f"群组 {group_id}"
                
                response += f"群聊: {group_name} ({group_id})\n"
                
                for user_id in users:
                    try:
                        user_name = await self._get_at_user_name(event, user_id)
                    except:
                        user_name = f"用户 {user_id}"
                    response += f"  - {user_name} ({user_id})\n"
                
                response += "\n"
        else:
            response += "【拉黑的用户】\n- 暂无\n"
        _get_background
        # 生成图片
        image_paths = await self.text_to_images(
            text=response,
            title="黑名单列表"
        )
        
        # 发送所有图片
        for path in image_paths:
            yield event.image_result(path)
    #endregion

#endregion
