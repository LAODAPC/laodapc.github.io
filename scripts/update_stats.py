import json
import requests
import os
from datetime import datetime
import random

def get_douyin_stats():
    """
    获取抖音数据
    由于抖音API限制，这里使用模拟数据 + 随机增长
    您可以替换为真实的API调用
    """
    try:
        # 读取当前数据
        try:
            with open('data/stats.json', 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，使用初始数据
            current_data = {
                "followers": 12000,
                "likes": 50000,
                "videos": 100,
                "lastUpdate": "2023-10-01"
            }
        
        # 模拟数据增长（每天随机增加一些粉丝和点赞）
        growth_followers = random.randint(10, 50)
        growth_likes = random.randint(100, 500)
        
        new_data = {
            "followers": current_data["followers"] + growth_followers,
            "likes": current_data["likes"] + growth_likes,
            "videos": current_data["videos"] + random.randint(0, 1),  # 偶尔发布新视频
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "auto_updated"
        }
        
        return new_data
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def update_stats_file():
    """更新数据文件"""
    new_stats = get_douyin_stats()
    
    if new_stats:
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        # 写入新数据
        with open('data/stats.json', 'w', encoding='utf-8') as f:
            json.dump(new_stats, f, ensure_ascii=False, indent=2)
        
        print("数据更新成功:")
        print(f"粉丝数: {new_stats['followers']}")
        print(f"获赞数: {new_stats['likes']}")
        print(f"作品数: {new_stats['videos']}")
        print(f"更新时间: {new_stats['lastUpdate']}")
    else:
        print("数据更新失败，使用备用方案")
        # 创建基础数据文件
        backup_data = {
            "followers": 12345,
            "likes": 56789,
            "videos": 128,
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "backup"
        }
        
        os.makedirs('data', exist_ok=True)
        with open('data/stats.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_stats_file()
