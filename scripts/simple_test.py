import json
import os
from datetime import datetime

def update_stats_file():
    """简单的测试数据更新"""
    
    # 使用测试数据
    stats = {
        "followers": 888,
        "likes": 12345,
        "videos": 66,
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "test_data",
        "source": "manual_test"
    }
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 写入数据
    with open('data/stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("测试数据更新完成:")
    print(f"粉丝数: {stats['followers']}")
    print(f"获赞数: {stats['likes']}")
    print(f"作品数: {stats['videos']}")

if __name__ == "__main__":
    update_stats_file()
