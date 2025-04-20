from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Optional

# 创建FastAPI应用
app = FastAPI(
    title="小红书内容提取API",
    description="提取小红书笔记的标题、描述、图片等信息",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 定义请求模型
class XHSRequest(BaseModel):
    text: str

# 定义响应模型
class XHSResponse(BaseModel):
    title: str = ""
    description: str = ""
    images: List[str] = []
    url: str = ""
    type: str = ""
    extracted_url: str = ""

def is_valid_xhs_url(url: str) -> bool:
    """
    检查是否是有效的小红书链接
    :param url: 要检查的URL
    :return: 是否有效
    """
    # 检查是否是小红书短链接
    if url.startswith('http://xhslink.com/'):
        return True
    # 检查是否是小红书原始链接
    if 'xiaohongshu.com' in url:
        return True
    return False

def extract_xhs_link(text: str) -> Optional[str]:
    """
    从文本中提取小红书链接
    :param text: 输入文本（可以是URL或分享文本）
    :return: 提取到的链接
    """
    # 如果输入本身就是有效的URL，直接返回
    if is_valid_xhs_url(text):
        return text
    
    # 否则尝试从文本中提取链接
    pattern = r'http://xhslink\.com/[a-zA-Z0-9/]+\b'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def get_html_content(url: str) -> Optional[str]:
    """
    获取网页内容
    :param url: 网页URL
    :return: HTML内容
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"获取网页内容失败: {str(e)}")

def extract_meta_info(html_content: str) -> XHSResponse:
    """
    提取页面信息
    :param html_content: HTML内容
    :return: 提取的信息字典
    """
    if not html_content:
        raise HTTPException(status_code=400, detail="HTML内容为空")
        
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_info = XHSResponse()
    
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if meta.get('name'):
            name = meta.get('name')
            content = meta.get('content', '')
            
            if name == 'og:title':
                meta_info.title = content
            elif name == 'description':  # 使用description而不是og:description
                meta_info.description = content
            elif name == 'og:image':
                meta_info.images.append(content)
            elif name == 'og:url':
                meta_info.url = content
            elif name == 'og:type':
                meta_info.type = content
    
    return meta_info

@app.post("/extract", response_model=XHSResponse)
async def extract_content(request: XHSRequest):
    """
    从小红书链接或分享文本中提取内容
    
    - **text**: 小红书链接或完整分享文本
    
    返回提取的内容信息，包括标题、描述、图片等
    """
    # 提取链接
    url = extract_xhs_link(request.text)
    if not url:
        raise HTTPException(status_code=400, detail="未能识别到有效的小红书链接")
    
    # 获取页面内容
    html_content = get_html_content(url)
    
    # 提取信息
    result = extract_meta_info(html_content)
    result.extracted_url = url
    
    return result

@app.get("/")
async def root():
    """API根路径，返回简单的欢迎信息"""
    return {"message": "欢迎使用小红书内容提取API"}

# 移除本地运行的代码，因为Vercel会使用自己的服务器配置 