import json
import os
from datetime import datetime

def update_stats_file():
    """强制更新为真实零数据"""
    print("强制更新数据文件...")
    
    # 使用真实零数据
    stats = {
        "followers": 0,
        "likes": 0,
        "videos": 0,
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "real_zero_data",
        "source": "forced_update"
    }
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 强制写入
    with open('data/stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("数据强制更新完成:")
    print(f"粉丝数: {stats['followers']}")
    print(f"获赞数: {stats['likes']}")
    print(f"作品数: {stats['videos']}")

if __name__ == "__main__":
    update_stats_file()
