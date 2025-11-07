import json
import requests
import os
from datetime import datetime

def get_real_douyin_stats():
    """
    使用 SocialCounts.org API 获取真实抖音数据
    """
    try:
        # 使用您的抖音号
        douyin_unique_id = "mzhvip666"
        
        # SocialCounts.org API
        api_url = f"https://socialcounts.org/api/douyin/{douyin_unique_id}"
        
        print(f"尝试获取抖音数据，抖音号: {douyin_unique_id}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://socialcounts.org/'
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("API响应数据:", data)
            
            # 解析返回的数据结构
            if 'count' in data:
                return {
                    "followers": data.get("count", 0),
                    "likes": data.get("likes", 0),
                    "videos": data.get("videos", 0),
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "live_data",
                    "source": "socialcounts.org"
                }
            else:
                print("API返回的数据格式不符合预期")
                return None
                
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"获取真实抖音数据失败: {e}")
        return None

def get_backup_stats():
    """
    备用方案：使用固定数据，不模拟增长
    """
    try:
        # 读取当前数据
        with open('data/stats.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
            # 保持原有数据不变
            return {
                "followers": current_data.get("followers", 10000),
                "likes": current_data.get("likes", 50000),
                "videos": current_data.get("videos", 50),
                "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "backup_data",
                "source": "backup_fixed"
            }
    except FileNotFoundError:
        # 初始数据
        return {
            "followers": 10000,
            "likes": 50000,
            "videos": 50,
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "initial_data",
            "source": "initial"
        }

def update_stats_file():
    """更新数据文件"""
    print("开始更新抖音数据...")
    
    # 先尝试获取真实数据
    real_stats = get_real_douyin_stats()
    
    if real_stats:
        print("成功获取真实抖音数据")
        new_stats = real_stats
    else:
        print("使用备用数据")
        new_stats = get_backup_stats()
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 写入数据
    with open('data/stats.json', 'w', encoding='utf-8') as f:
        json.dump(new_stats, f, ensure_ascii=False, indent=2)
    
    print("数据更新完成:")
    print(f"粉丝数: {new_stats['followers']}")
    print(f"获赞数: {new_stats['likes']}")
    print(f"作品数: {new_stats['videos']}")
    print(f"数据源: {new_stats['source']}")
    print(f"更新时间: {new_stats['lastUpdate']}")

if __name__ == "__main__":
    update_stats_file()
