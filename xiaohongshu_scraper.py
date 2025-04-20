import requests
from bs4 import BeautifulSoup
import re

def scrape_xiaohongshu(url):
    """
    爬取小红书内容
    :param url: 小红书链接
    :return: 包含标题、正文和图片链接的字典
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 发送GET请求获取页面内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 从meta标签中提取标题
        title_meta = soup.find('meta', {'name': 'og:title'})
        title = title_meta['content'] if title_meta else "未找到标题"
        
        # 提取正文内容 - 暂时保留为空，因为示例中没有提供正文的提取方式
        content = "正文内容需要根据实际HTML结构调整提取方式"
        
        # 提取图片链接 - 从meta标签中获取
        image_links = []
        for img_meta in soup.find_all('meta', {'name': 'og:image'}):
            if img_meta.get('content'):
                image_links.append(img_meta['content'])
        
        return {
            'title': title,
            'content': content,
            'image_links': image_links
        }
        
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except Exception as e:
        print(f"解析出错: {e}")
        return None

def main():
    # 测试链接
    test_url = "https://www.xiaohongshu.com/explore/68039f12000000001e00a45f"
    
    # 调用爬虫函数
    result = scrape_xiaohongshu(test_url)
    
    if result:
        print("标题:", result['title'])
        print("\n正文:", result['content'])
        print("\n图片链接:")
        for i, link in enumerate(result['image_links'], 1):
            print(f"{i}. {link}")

if __name__ == "__main__":
    main() 