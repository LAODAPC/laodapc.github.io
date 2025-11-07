import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import re
import json as json_lib

def get_redirect_url(short_url):
    """
    获取短链接的重定向URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(short_url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        return response.geturl()  # 获取重定向后的真实URL
    except Exception as e:
        print(f"获取重定向URL失败: {e}")
        return short_url

def extract_user_id_from_url(url):
    """
    从抖音URL中提取用户ID或sec_user_id
    """
    try:
        # 如果是短链接，先获取真实链接
        if 'v.douyin.com' in url:
            url = get_redirect_url(url)
            print(f"重定向后URL: {url}")
        
        # 提取sec_user_id
        sec_patterns = [
            r'sec_user_id=([^&]+)',
            r'user/([^?]+)',
            r'profile/([^/?]+)'
        ]
        
        for pattern in sec_patterns:
            match = re.search(pattern, url)
            if match:
                user_id = match.group(1)
                print(f"提取到用户ID: {user_id}")
                return user_id
        
        return None
    except Exception as e:
        print(f"提取用户ID失败: {e}")
        return None

def get_douyin_by_share_link():
    """
    使用分享链接获取抖音数据
    """
    try:
        # 使用你提供的分享链接
        share_link = "https://v.douyin.com/7Rn72odFtuc/"
        
        print(f"处理分享链接: {share_link}")
        user_id = extract_user_id_from_url(share_link)
        
        if not user_id:
            print("无法从链接中提取用户ID")
            return None
        
        # 方法1: 使用官方API
        api_url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={user_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://www.douyin.com/user/{user_id}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        print(f"调用官方API: {api_url}")
        
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json_lib.loads(response.read().decode('utf-8'))
            
            if data.get('status_code') == 0 and 'user' in data:
                user_info = data['user']
                print(f"API返回数据: {user_info}")
                
                return {
                    "followers": user_info.get('follower_count', 0),
                    "likes": user_info.get('total_favorited', 0),
                    "videos": user_info.get('aweme_count', 0),
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "official_api",
                    "source": "douyin_official"
                }
            else:
                print(f"API返回错误: {data}")
        
        # 方法2: 访问用户主页
        return get_user_stats_by_web(user_id)
        
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"分享链接获取失败: {e}")
        return None

def get_user_stats_by_web(user_id):
    """
    通过网页访问获取用户数据
    """
    try:
        user_url = f"https://www.douyin.com/user/{user_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.douyin.com/'
        }
        
        print(f"访问用户主页: {user_url}")
        
        req = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # 查找JSON数据
            json_pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
            match = re.search(json_pattern, html)
            
            if match:
                json_str = urllib.parse.unquote(match.group(1))
                data = json_lib.loads(json_str)
                print("找到RENDER_DATA")
                
                # 简化版数据提取
                followers = extract_from_json(data, ['follower_count', 'followerCount'])
                likes = extract_from_json(data, ['total_favorited', 'totalFavorited'])
                videos = extract_from_json(data, ['aweme_count', 'awemeCount'])
                
                if followers > 0:
                    return {
                        "followers": followers,
                        "likes": likes,
                        "videos": videos,
                        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "web_data",
                        "source": "douyin_web"
                    }
        
        return None
        
    except Exception as e:
        print(f"网页访问失败: {e}")
        return None

def extract_from_json(data, keys):
    """
    从JSON数据中提取指定键的值
    """
    def find_value(obj, target_keys):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in target_keys:
                    return value
                result = find_value(value, target_keys)
                if result is not None:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = find_value(item, target_keys)
                if result is not None:
                    return result
        return 0
    
    result = find_value(data, keys)
    return int(result) if result else 0

def get_fallback_stats():
    """
    备用方案：从文件读取上次的数据
    """
    try:
        with open('data/stats.json', 'r', encoding='utf-8') as f:
            current_data = json_lib.load(f)
            return {
                "followers": current_data.get("followers", 0),
                "likes": current_data.get("likes", 0),
                "videos": current_data.get("videos", 0),
                "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "fallback_data",
                "source": "previous_file"
            }
    except FileNotFoundError:
        return {
            "followers": 0,
            "likes": 0,
            "videos": 0,
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "no_data",
            "source": "initial"
        }

def update_stats_file():
    """更新数据文件"""
    print("开始通过分享链接获取抖音数据...")
    
    # 使用分享链接获取数据
    stats = get_douyin_by_share_link()
    
    # 如果失败，使用备用方案
    if not stats:
        print("使用备用数据...")
        stats = get_fallback_stats()
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 写入数据
    with open('data/stats.json', 'w', encoding='utf-8') as f:
        json_lib.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("数据更新完成:")
    print(f"粉丝数: {stats['followers']}")
    print(f"获赞数: {stats['likes']}")
    print(f"作品数: {stats['videos']}")
    print(f"数据源: {stats['source']}")
    print(f"状态: {stats['status']}")
    print(f"更新时间: {stats['lastUpdate']}")

if __name__ == "__main__":
    update_stats_file()
