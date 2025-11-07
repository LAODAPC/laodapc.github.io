import json
import os
import requests
from datetime import datetime
import re
import time

def get_douyin_stats_improved():
    """
    改进的抖音数据获取方法
    """
    try:
        # 方法1: 使用抖音网页版API
        print("尝试方法1: 网页版API...")
        
        # 你的抖音分享链接
        share_links = [
            "https://v.douyin.com/7Rn72odFtuc/",
            # 可以添加多个备用链接
        ]
        
        for share_link in share_links:
            try:
                # 获取重定向后的真实URL
                response = requests.get(share_link, allow_redirects=False, timeout=10)
                if response.status_code in [301, 302]:
                    final_url = response.headers['Location']
                    print(f"重定向到: {final_url}")
                    
                    # 提取sec_user_id
                    sec_match = re.search(r'sec_uid=([^&]+)', final_url)
                    if sec_match:
                        sec_user_id = sec_match.group(1)
                        print(f"找到sec_user_id: {sec_user_id}")
                        
                        # 使用移动端API（更稳定）
                        mobile_api_url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={sec_user_id}"
                        
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Mobile Safari/537.36',
                            'Accept': 'application/json, text/plain, */*',
                            'Accept-Language': 'zh-CN,zh;q=0.9',
                            'Referer': 'https://www.douyin.com/',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                        
                        response = requests.get(mobile_api_url, headers=headers, timeout=15)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status_code') == 0 and 'user' in data:
                                user_info = data['user']
                                return {
                                    "followers": user_info.get('follower_count', 0),
                                    "likes": user_info.get('total_favorited', 0),
                                    "videos": user_info.get('aweme_count', 0),
                                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "status": "official_api",
                                    "source": "douyin_mobile_api"
                                }
            except Exception as e:
                print(f"方法1失败: {e}")
                continue
        
        # 方法2: 使用公开数据接口
        print("尝试方法2: 公开接口...")
        try:
            # 这里可以使用第三方API或者模拟请求
            # 由于抖音限制严格，这里返回真实零数据而不是测试数据
            return get_real_zero_data()
        except Exception as e:
            print(f"方法2失败: {e}")
        
        # 所有方法都失败，返回真实零数据
        print("所有方法都失败，返回真实零数据")
        return get_real_zero_data()
        
    except Exception as e:
        print(f"数据获取异常: {e}")
        return get_real_zero_data()

def get_real_zero_data():
    """返回真实的零数据"""
    return {
        "followers": 0,
        "likes": 0,
        "videos": 0,
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "api_failed",
        "source": "real_zero"
    }

def get_fallback_stats():
    """备用数据 - 读取上次成功的数据"""
    try:
        if os.path.exists('data/stats.json'):
            with open('data/stats.json', 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                # 只有当之前有真实数据时才使用
                if current_data.get('source') != 'real_zero' and current_data.get('followers', 0) > 0:
                    return {
                        "followers": current_data.get("followers", 0),
                        "likes": current_data.get("likes", 0),
                        "videos": current_data.get("videos", 0),
                        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "cached_data",
                        "source": "previous_success"
                    }
        return get_real_zero_data()
    except Exception as e:
        print(f"读取备用数据失败: {e}")
        return get_real_zero_data()

def update_stats_file():
    """更新数据文件"""
    print("开始获取抖音数据...")
    
    # 尝试获取真实数据
    stats = get_douyin_stats_improved()
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 写入数据
    with open('data/stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("数据更新完成:")
    print(f"粉丝数: {stats['followers']}")
    print(f"获赞数: {stats['likes']}")
    print(f"作品数: {stats['videos']}")
    print(f"数据源: {stats['source']}")
    print(f"状态: {stats['status']}")

if __name__ == "__main__":
    update_stats_file()
