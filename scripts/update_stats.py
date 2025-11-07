import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import re
import json as json_lib

def get_douyin_by_id():
    """
    使用您的抖音ID获取数据
    """
    try:
        # 使用您提供的抖音ID
        douyin_id = "self?from_tab_name=main&showTab=post"
        
        # 构建用户主页URL
        user_url = f"https://www.douyin.com/user/{douyin_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.douyin.com/'
        }
        
        print(f"访问抖音主页，ID: {douyin_id}")
        
        req = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # 方法1：查找JSON数据
            json_pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
            match = re.search(json_pattern, html)
            
            if match:
                json_str = urllib.parse.unquote(match.group(1))
                data = json_lib.loads(json_str)
                
                user_info = extract_user_info_from_json(data)
                if user_info:
                    return user_info
            
            # 方法2：正则匹配
            stats = extract_stats_with_regex(html)
            if stats:
                return stats
            
            # 方法3：查找sec_user_id
            sec_user_id = extract_sec_user_id(html)
            if sec_user_id:
                return get_user_stats_by_sec_id(sec_user_id)
        
        return None
        
    except Exception as e:
        print(f"抖音ID访问失败: {e}")
        return None

def extract_sec_user_id(html):
    """
    从HTML中提取sec_user_id
    """
    try:
        patterns = [
            r'"sec_uid":"([^"]+)"',
            r'sec_uid[=:]([^&"\']+)',
            r'sec_user_id[=:]([^&"\']+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                sec_id = match.group(1)
                print(f"找到sec_user_id: {sec_id}")
                return sec_id
        
        return None
    except Exception as e:
        print(f"提取sec_user_id失败: {e}")
        return None

def get_user_stats_by_sec_id(sec_user_id):
    """
    通过sec_user_id调用官方API
    """
    try:
        api_url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={sec_user_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://www.douyin.com/user/{sec_user_id}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        print(f"调用官方API，sec_user_id: {sec_user_id}")
        
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json_lib.loads(response.read().decode('utf-8'))
            
            if data.get('status_code') == 0 and 'user' in data:
                user_info = data['user']
                return {
                    "followers": user_info.get('follower_count', 0),
                    "likes": user_info.get('total_favorited', 0),
                    "videos": user_info.get('aweme_count', 0),
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "official_api",
                    "source": "douyin_official"
                }
        
        return None
        
    except Exception as e:
        print(f"官方API调用失败: {e}")
        return None

def extract_user_info_from_json(data):
    """
    从JSON数据中提取用户信息
    """
    try:
        # 递归查找用户信息
        def find_user_info(obj, depth=0):
            if depth > 10:  # 防止无限递归
                return None
                
            if isinstance(obj, dict):
                # 检查是否包含用户信息字段
                if any(key in obj for key in ['followerCount', 'follower_count', 'totalFavorited', 'total_favorited']):
                    return obj
                
                for key, value in obj.items():
                    result = find_user_info(value, depth + 1)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for item in obj:
                    result = find_user_info(item, depth + 1)
                    if result:
                        return result
            return None
        
        user_info = find_user_info(data)
        if user_info:
            return {
                "followers": user_info.get('followerCount', user_info.get('follower_count', 0)),
                "likes": user_info.get('totalFavorited', user_info.get('total_favorited', 0)),
                "videos": user_info.get('awemeCount', user_info.get('aweme_count', 0)),
                "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "web_json",
                "source": "douyin_web_json"
            }
    except Exception as e:
        print(f"JSON解析失败: {e}")
    
    return None

def extract_stats_with_regex(html):
    """
    使用正则表达式提取数据
    """
    try:
        # 粉丝数
        follower_patterns = [
            r'"followerCount":\s*"*(\d+)"*',
            r'"follower_count":\s*"*(\d+)"*',
            r'粉丝.*?(\d+)',
            r'关注者.*?(\d+)'
        ]
        
        # 获赞数
        like_patterns = [
            r'"totalFavorited":\s*"*(\d+)"*',
            r'"total_favorited":\s*"*(\d+)"*',
            r'获赞.*?(\d+)',
            r'点赞.*?(\d+)'
        ]
        
        # 作品数
        video_patterns = [
            r'"awemeCount":\s*"*(\d+)"*',
            r'"aweme_count":\s*"*(\d+)"*',
            r'作品.*?(\d+)'
        ]
        
        followers = extract_number(html, follower_patterns)
        likes = extract_number(html, like_patterns)
        videos = extract_number(html, video_patterns)
        
        if followers > 0:
            return {
                "followers": followers,
                "likes": likes if likes > 0 else 0,
                "videos": videos if videos > 0 else 0,
                "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "web_regex",
                "source": "douyin_web_regex"
            }
    
    except Exception as e:
        print(f"正则提取失败: {e}")
    
    return None

def extract_number(html, patterns):
    """从HTML中提取数字"""
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            try:
                num = int(match)
                if num > 0:
                    return num
            except:
                continue
    return 0

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
    print("开始自动获取抖音数据...")
    
    # 使用您的抖音ID获取数据
    stats = get_douyin_by_id()
    
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
