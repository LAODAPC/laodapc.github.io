import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import re
import json as json_lib

def get_redirect_url(short_url):
    """获取短链接的重定向URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(short_url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        final_url = response.geturl()
        print(f"重定向到: {final_url}")
        return final_url
    except Exception as e:
        print(f"获取重定向URL失败: {e}")
        return short_url

def extract_sec_user_id(url):
    """从URL中提取sec_user_id"""
    try:
        # 如果是短链接，先获取真实链接
        if 'v.douyin.com' in url:
            url = get_redirect_url(url)
        
        # 提取sec_user_id
        patterns = [
            r'sec_user_id=([A-Za-z0-9_-]+)',
            r'user/([A-Za-z0-9_-]+)',
            r'profile/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                sec_id = match.group(1)
                print(f"提取到sec_user_id: {sec_id}")
                return sec_id
        
        print("未找到sec_user_id")
        return None
    except Exception as e:
        print(f"提取sec_user_id失败: {e}")
        return None

def get_douyin_stats_api(sec_user_id):
    """通过官方API获取抖音数据"""
    try:
        api_url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={sec_user_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f'https://www.douyin.com/user/{sec_user_id}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        print(f"调用官方API: {api_url}")
        
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json_lib.loads(response.read().decode('utf-8'))
            print(f"API响应: {json_lib.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('status_code') == 0 and 'user' in data:
                user_info = data['user']
                return {
                    "followers": user_info.get('follower_count', 0),
                    "likes": user_info.get('total_favorited', 0),
                    "videos": user_info.get('aweme_count', 0),
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "official_api_success",
                    "source": "douyin_official_api"
                }
            else:
                print(f"API返回错误状态: {data.get('status_code')}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"HTTP错误 {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

def get_douyin_stats_web(sec_user_id):
    """通过网页解析获取数据"""
    try:
        user_url = f"https://www.douyin.com/user/{sec_user_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        print(f"访问网页: {user_url}")
        
        req = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8')
            
            # 方法1: 查找RENDER_DATA
            json_pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
            match = re.search(json_pattern, html)
            
            if match:
                json_str = urllib.parse.unquote(match.group(1))
                data = json_lib.loads(json_str)
                print("找到RENDER_DATA，尝试解析...")
                
                # 递归查找用户信息
                def find_user_info(obj, depth=0):
                    if depth > 8:
                        return None
                    if isinstance(obj, dict):
                        if 'follower_count' in obj or 'followerCount' in obj:
                            return obj
                        for value in obj.values():
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
                        "followers": user_info.get('follower_count', user_info.get('followerCount', 0)),
                        "likes": user_info.get('total_favorited', user_info.get('totalFavorited', 0)),
                        "videos": user_info.get('aweme_count', user_info.get('awemeCount', 0)),
                        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "web_parse_success",
                        "source": "douyin_web_parse"
                    }
            
            # 方法2: 正则匹配页面文本
            print("尝试正则匹配...")
            followers = extract_with_regex(html, ['粉丝.*?(\d+)', 'followerCount["\']?:\s*["\']?(\d+)'])
            likes = extract_with_regex(html, ['获赞.*?(\d+)', 'totalFavorited["\']?:\s*["\']?(\d+)'])
            videos = extract_with_regex(html, ['作品.*?(\d+)', 'awemeCount["\']?:\s*["\']?(\d+)'])
            
            if followers > 0:
                return {
                    "followers": followers,
                    "likes": likes,
                    "videos": videos,
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "web_regex_success",
                    "source": "douyin_web_regex"
                }
            
            return None
            
    except Exception as e:
        print(f"网页解析失败: {e}")
        return None

def extract_with_regex(html, patterns):
    """使用正则表达式提取数字"""
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
    """备用方案：读取上次数据"""
    try:
        if os.path.exists('data/stats.json'):
            with open('data/stats.json', 'r', encoding='utf-8') as f:
                current_data = json_lib.load(f)
                # 如果之前有真实数据，就保持
                if current_data.get('source') != 'integrated' and current_data.get('followers', 0) > 0:
                    return {
                        "followers": current_data.get("followers", 0),
                        "likes": current_data.get("likes", 0),
                        "videos": current_data.get("videos", 0),
                        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "fallback_previous",
                        "source": "previous_data"
                    }
        
        # 如果没有历史数据，返回0
        return {
            "followers": 0,
            "likes": 0,
            "videos": 0,
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "no_data",
            "source": "initial"
        }
    except Exception as e:
        print(f"读取备用数据失败: {e}")
        return {
            "followers": 0,
            "likes": 0,
            "videos": 0,
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "error",
            "source": "error_fallback"
        }

def update_stats_file():
    """更新数据文件"""
    print("开始获取真实抖音数据...")
    
    # 使用你的抖音分享链接
    share_link = "https://v.douyin.com/7Rn72odFtuc/"
    print(f"使用分享链接: {share_link}")
    
    # 提取sec_user_id
    sec_user_id = extract_sec_user_id(share_link)
    
    stats = None
    
    # 方法1: 官方API
    if sec_user_id:
        stats = get_douyin_stats_api(sec_user_id)
    
    # 方法2: 网页解析
    if not stats and sec_user_id:
        stats = get_douyin_stats_web(sec_user_id)
    
    # 方法3: 备用数据
    if not stats:
        print("所有方法都失败，使用备用数据...")
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
