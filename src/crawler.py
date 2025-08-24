"""
网页爬取模块
使用crawl4ai框架进行智能内容提取

创建时间：2024-12-19
项目：系列技术文章翻译
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin, urlsplit, urlunsplit
import re

from crawl4ai import AsyncWebCrawler
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from config import OUTPUT_DIR, ORIGIN_DIR, USER_AGENT, REQUEST_DELAY, MAX_RETRIES


class WebCrawler:
    """网页爬取器，使用crawl4ai进行智能内容提取"""

    def __init__(self):
        """初始化爬取器"""
        self.logger = logging.getLogger(__name__)
        self.user_agent = USER_AGENT
        self.request_delay = REQUEST_DELAY
        self.max_retries = MAX_RETRIES

        # 确保输出目录存在
        Path(ORIGIN_DIR).mkdir(parents=True, exist_ok=True)

        self.logger.info("网页爬取器初始化完成")

    async def fetch_dynamic_page_content(self, url: str, wait_time: float = 5.0, custom_js: List[str] = None) -> Optional[Dict]:
        """
        抓取动态内容页面，支持自定义等待时间和JS代码

        Args:
            url (str): 要抓取的URL
            wait_time (float): 等待时间（秒）
            custom_js (List[str]): 自定义JavaScript代码列表

        Returns:
            Optional[Dict]: 包含页面内容的字典，失败时返回None
        """
        self.logger.info(f"开始抓取动态页面: {url} (等待时间: {wait_time}秒)")

        # 默认JS代码
        default_js = [
            "window.scrollTo(0, document.body.scrollHeight);",  # 滚动到底部
            f"await new Promise(resolve => setTimeout(resolve, {int(wait_time * 1000)}));"  # 等待
        ]

        # 合并自定义JS代码
        js_code = default_js + (custom_js or [])

        async with AsyncWebCrawler(
            user_agent=self.user_agent,
            headless=True,
            verbose=True,
            browser_type="chromium",
            always_by_pass_cache=True
        ) as crawler:

            for attempt in range(self.max_retries):
                try:
                    result = await crawler.arun(
                        url=url,
                        word_count_threshold=10,
                        bypass_cache=True,
                        process_iframes=True,
                        remove_overlay_elements=True,
                        exclude_external_links=False,
                        exclude_external_images=False,
                        wait_for="body",
                        delay_before_return_html=wait_time,
                        js_code=js_code,
                        css_selector="body",
                        simulate_user=True,
                        override_navigator=True,
                        page_timeout=60000  # 60秒超时
                    )

                    if result.success:
                        page_data = {
                            'url': url,
                            'title': result.metadata.get('title', '') if result.metadata else '',
                            'html': result.html,
                            'links': getattr(result, 'links', []),
                            'images': getattr(result, 'images', []),
                            'metadata': result.metadata or {},
                            'success': True,
                            'timestamp': time.time(),
                            'dynamic_content': True
                        }

                        # 转换相对URL为绝对URL并保存HTML
                        converted_html = self.convert_relative_to_absolute_urls(result.html, url)
                        await self._save_original_html(url, converted_html)

                        self.logger.info(f"动态页面抓取成功: {url}")
                        return page_data

                    else:
                        error_msg = f"动态页面抓取失败 (尝试 {attempt + 1}/{self.max_retries}): {result.error_message}"
                        self.logger.warning(error_msg)

                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.request_delay * (attempt + 1))

                except Exception as e:
                    error_msg = f"动态页面抓取异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                    self.logger.error(error_msg)

                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.request_delay * (attempt + 1))

            self.logger.error(f"动态页面抓取最终失败: {url}")
            return None

    async def fetch_page_content(self, url: str) -> Optional[Dict]:
        """
        抓取单个页面的内容

        Args:
            url (str): 要抓取的URL

        Returns:
            Optional[Dict]: 包含页面内容的字典，失败时返回None
        """
        self.logger.info(f"开始抓取页面: {url}")

        async with AsyncWebCrawler(
            user_agent=self.user_agent,
            headless=True,
            verbose=True,
            browser_type="chromium",  # 使用Chromium以获得更好的JS支持
            always_by_pass_cache=True
        ) as crawler:

            for attempt in range(self.max_retries):
                try:
                    # 执行爬取
                    result = await crawler.arun(
                        url=url,
                        word_count_threshold=10,
                        bypass_cache=True,
                        process_iframes=True,
                        remove_overlay_elements=True,
                        exclude_external_links=False,
                        exclude_external_images=False,
                        wait_for="body",  # 等待body元素加载
                        delay_before_return_html=3.0,  # 等待3秒让JS执行
                        js_code=[
                            "window.scrollTo(0, document.body.scrollHeight);",  # 滚动到底部触发懒加载
                            "await new Promise(resolve => setTimeout(resolve, 2000));"  # 额外等待2秒
                        ],
                        css_selector="body",  # 确保获取完整内容
                        simulate_user=True,  # 模拟用户行为
                        override_navigator=True  # 覆盖navigator检测
                    )

                    if result.success:
                        # 提取页面信息
                        page_data = {
                            'url': url,
                            'title': result.metadata.get('title', '') if result.metadata else '',
                            'html': result.html,
                            'links': getattr(result, 'links', []),
                            'images': getattr(result, 'images', []),
                            'metadata': result.metadata or {},
                            'success': True,
                            'timestamp': time.time()
                        }

                        # 转换相对URL为绝对URL并保存HTML
                        converted_html = self.convert_relative_to_absolute_urls(result.html, url)
                        await self._save_original_html(url, converted_html)

                        self.logger.info(f"页面抓取成功: {url}")
                        return page_data

                    else:
                        error_msg = f"抓取失败 (尝试 {attempt + 1}/{self.max_retries}): {result.error_message}"
                        self.logger.warning(error_msg)

                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.request_delay * (attempt + 1))  # 递增延时

                except Exception as e:
                    error_msg = f"抓取异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                    self.logger.error(error_msg)

                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.request_delay * (attempt + 1))

            # 所有重试都失败
            self.logger.error(f"页面抓取最终失败: {url}")
            return None

    async def _save_original_html(self, url: str, html_content: str) -> str:
        """
        保存原始HTML到文件

        Args:
            url (str): 页面URL
            html_content (str): HTML内容

        Returns:
            str: 保存的文件路径
        """
        # 从URL生成文件名
        parsed_url = urlparse(url)
        filename = parsed_url.path.strip('/').split('/')[-1]
        if not filename or filename == '':
            filename = 'index'

        # 确保文件名有.html扩展名
        if not filename.endswith('.html'):
            filename += '.html'

        file_path = Path(ORIGIN_DIR) / filename

        # 如果文件已存在，添加序号
        counter = 1
        original_filename = filename
        while file_path.exists():
            name, ext = original_filename.rsplit('.', 1)
            filename = f"{name}_{counter}.{ext}"
            file_path = Path(ORIGIN_DIR) / filename
            counter += 1

        # 保存HTML内容
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"原始HTML已保存: {file_path}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"保存HTML文件失败: {str(e)}")
            raise

    async def batch_crawl(self, url_list: List[str]) -> List[Dict]:
        """
        批量爬取多个URL

        Args:
            url_list (List[str]): URL列表

        Returns:
            List[Dict]: 爬取结果列表
        """
        self.logger.info(f"开始批量爬取 {len(url_list)} 个页面")

        results = []
        successful_count = 0
        failed_urls = []

        for i, url in enumerate(url_list, 1):
            self.logger.info(f"进度: {i}/{len(url_list)} - 正在处理: {url}")

            # 添加请求间隔避免过于频繁
            if i > 1:
                await asyncio.sleep(self.request_delay)

            result = await self.fetch_page_content(url)

            if result:
                results.append(result)
                successful_count += 1
                self.logger.info(f"✅ 成功: {url}")
            else:
                failed_urls.append(url)
                # 添加失败的URL信息到结果中
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'Failed to fetch content',
                    'timestamp': time.time()
                })
                self.logger.error(f"❌ 失败: {url}")

        # 输出统计信息
        self.logger.info(f"批量爬取完成:")
        self.logger.info(f"  总数: {len(url_list)}")
        self.logger.info(f"  成功: {successful_count}")
        self.logger.info(f"  失败: {len(failed_urls)}")

        if failed_urls:
            self.logger.warning(f"失败的URL列表: {failed_urls}")

        return results

    def convert_relative_to_absolute_urls(self, html_content: str, base_url: str) -> str:
        """
        将HTML中的相对URL转换为绝对URL

        Args:
            html_content (str): HTML内容
            base_url (str): 基础URL

        Returns:
            str: 转换后的HTML内容
        """
        if not html_content:
            return html_content

        try:
            # 如果有BeautifulSoup，使用它来解析HTML（更准确）
            if BeautifulSoup:
                return self._convert_with_bs4(html_content, base_url)
            else:
                # 降级到正则表达式方法
                return self._convert_with_regex(html_content, base_url)

        except Exception as e:
            self.logger.warning(f"URL转换失败，返回原始内容: {str(e)}")
            return html_content

    def _convert_with_bs4(self, html_content: str, base_url: str) -> str:
        """使用BeautifulSoup进行URL转换"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 需要转换的属性映射
        url_attributes = {
            'a': ['href'],
            'link': ['href'],
            'script': ['src'],
            'img': ['src', 'data-src', 'srcset'],
            'source': ['src', 'srcset'],
            'video': ['src', 'poster'],
            'audio': ['src'],
            'iframe': ['src'],
            'embed': ['src'],
            'object': ['data'],
            'form': ['action'],
            'base': ['href']
        }

        for tag_name, attributes in url_attributes.items():
            tags = soup.find_all(tag_name)
            for tag in tags:
                for attr in attributes:
                    if tag.has_attr(attr):
                        original_url = tag[attr]
                        if original_url:
                            if attr == 'srcset':
                                # 处理srcset属性（可能包含多个URL）
                                tag[attr] = self._convert_srcset(original_url, base_url)
                            else:
                                # 处理单个URL
                                absolute_url = self._make_absolute_url(original_url, base_url)
                                if absolute_url != original_url:
                                    tag[attr] = absolute_url

        # 处理CSS中的URL
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                style_tag.string = self._convert_css_urls(style_tag.string, base_url)

        # 处理内联style属性中的URL
        tags_with_style = soup.find_all(attrs={'style': True})
        for tag in tags_with_style:
            tag['style'] = self._convert_css_urls(tag['style'], base_url)

        return str(soup)

    def _convert_with_regex(self, html_content: str, base_url: str) -> str:
        """使用正则表达式进行URL转换（备用方法）"""
        # 匹配常见的URL属性
        patterns = [
            (r'(href|src|action|data)=(["\'])([^"\']*?)\2', 3),
            (r'(srcset)=(["\'])([^"\']*?)\2', 3),
            (r'url\((["\']?)([^)]*?)\1\)', 2),  # CSS中的url()
        ]

        result = html_content
        for pattern, url_group in patterns:
            def replace_url(match):
                full_match = match.group(0)
                url = match.group(url_group)

                if url_group == 3 and match.group(1) == 'srcset':
                    # 处理srcset
                    new_srcset = self._convert_srcset(url, base_url)
                    return full_match.replace(url, new_srcset)
                else:
                    # 处理单个URL
                    absolute_url = self._make_absolute_url(url, base_url)
                    return full_match.replace(url, absolute_url)

            result = re.sub(pattern, replace_url, result, flags=re.IGNORECASE)

        return result

    def _convert_srcset(self, srcset: str, base_url: str) -> str:
        """转换srcset属性中的URL"""
        if not srcset:
            return srcset

        # srcset格式: "url1 descriptor1, url2 descriptor2, ..."
        parts = []
        for item in srcset.split(','):
            item = item.strip()
            if item:
                # 分离URL和描述符
                url_parts = item.split()
                if url_parts:
                    url = url_parts[0]
                    descriptor = ' '.join(url_parts[1:]) if len(url_parts) > 1 else ''

                    absolute_url = self._make_absolute_url(url, base_url)
                    if descriptor:
                        parts.append(f"{absolute_url} {descriptor}")
                    else:
                        parts.append(absolute_url)

        return ', '.join(parts)

    def _convert_css_urls(self, css_content: str, base_url: str) -> str:
        """转换CSS内容中的URL"""
        def replace_css_url(match):
            quote = match.group(1) or ''
            url = match.group(2)
            absolute_url = self._make_absolute_url(url, base_url)
            return f"url({quote}{absolute_url}{quote})"

        return re.sub(r'url\((["\']?)([^)]*?)\1\)', replace_css_url, css_content, flags=re.IGNORECASE)

    def _make_absolute_url(self, url: str, base_url: str) -> str:
        """将相对URL转换为绝对URL"""
        if not url or not base_url:
            return url

        # 跳过已经是绝对URL的情况
        if url.startswith(('http://', 'https://', 'ftp://', 'mailto:', 'tel:', 'data:', 'javascript:')):
            return url

        # 跳过锚点链接和查询参数
        if url.startswith(('#', '?')):
            return url

        try:
            # 使用urljoin进行URL合并
            absolute_url = urljoin(base_url, url)
            return absolute_url
        except Exception as e:
            self.logger.warning(f"URL转换失败 '{url}' with base '{base_url}': {str(e)}")
            return url

    def get_filename_from_url(self, url: str) -> str:
        """
        从URL生成文件名

        Args:
            url (str): URL地址

        Returns:
            str: 生成的文件名
        """
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')

        # 取最后一个非空部分作为文件名
        filename = None
        for part in reversed(path_parts):
            if part:
                filename = part
                break

        if not filename:
            filename = 'index'

        # 清理文件名中的特殊字符
        filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))

        return filename


def load_urls_from_file(file_path: str) -> List[str]:
    """
    从文件中加载URL列表

    Args:
        file_path (str): URL文件路径

    Returns:
        List[str]: URL列表
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if line and not line.startswith('#'):
                    urls.append(line)

        logging.getLogger(__name__).info(f"从 {file_path} 加载了 {len(urls)} 个URL")
        return urls

    except FileNotFoundError:
        logging.getLogger(__name__).error(f"URL文件不存在: {file_path}")
        return []
    except Exception as e:
        logging.getLogger(__name__).error(f"读取URL文件失败: {str(e)}")
        return []


# 便捷函数
async def crawl_single_page(url: str) -> Optional[Dict]:
    """便捷函数：爬取单个页面"""
    crawler = WebCrawler()
    return await crawler.fetch_page_content(url)


async def crawl_multiple_pages(url_list: List[str]) -> List[Dict]:
    """便捷函数：批量爬取多个页面"""
    crawler = WebCrawler()
    return await crawler.batch_crawl(url_list)


async def crawl_from_file(file_path: str) -> List[Dict]:
    """便捷函数：从文件读取URL并批量爬取"""
    urls = load_urls_from_file(file_path)
    if not urls:
        return []

    crawler = WebCrawler()
    return await crawler.batch_crawl(urls)


async def crawl_dynamic_page(url: str, wait_time: float = 5.0, custom_js: List[str] = None) -> Optional[Dict]:
    """便捷函数：爬取动态内容页面"""
    crawler = WebCrawler()
    return await crawler.fetch_dynamic_page_content(url, wait_time, custom_js)


async def crawl_dynamic_pages(url_list: List[str], wait_time: float = 5.0) -> List[Dict]:
    """便捷函数：批量爬取动态内容页面"""
    crawler = WebCrawler()
    results = []

    for url in url_list:
        result = await crawler.fetch_dynamic_page_content(url, wait_time)
        if result:
            results.append(result)
        else:
            results.append({
                'url': url,
                'success': False,
                'error': 'Failed to fetch dynamic content',
                'timestamp': time.time()
            })

        # 添加延时
        await asyncio.sleep(crawler.request_delay)

    return results



async def test_batch_crawl():
    """测试批量爬取"""
    print("\n=== 测试批量爬取 ===")

    config_file = "src/config/urls.txt"
    results = await crawl_from_file(config_file)

    successful = sum(1 for r in results if r.get('success'))
    total = len(results)

    print(f"批量爬取完成: {successful}/{total} 成功")

    for result in results:
        if result.get('success'):
            print(f"✅ {result['url']} - {result.get('title', 'N/A')}")
        else:
            print(f"❌ {result['url']} - 失败")


async def test_dynamic_page():
    """测试动态页面爬取"""
    print("\n=== 测试动态页面爬取 ===")

    test_url = "https://jax-ml.github.io/scaling-book/tpus/"
    result = await crawl_dynamic_page(test_url, wait_time=5.0)

    if result and result.get('success'):
        print(f"✅ 成功爬取动态页面: {test_url}")
        print(f"   标题: {result.get('title', 'N/A')}")
        print(f"   HTML长度: {len(result.get('html', ''))}")
        print(f"   链接数量: {len(result.get('links', []))}")
        print(f"   图片数量: {len(result.get('images', []))}")
        print(f"   动态内容: {result.get('dynamic_content', False)}")
    else:
        print(f"❌ 动态页面爬取失败: {test_url}")


async def main():
    """主测试函数"""
    # 导入日志配置
    from config.logging_config import setup_logging

    # 设置日志
    setup_logging('INFO')

    print("开始测试网页爬取功能...\n")

    # 测试动态页面爬取
    #await test_dynamic_page()

    # 测试批量爬取（如果URL文件存在）
    try:
        import os
        if os.path.exists("src/config/urls.txt"):
            await test_batch_crawl()
        else:
            print("\n⚠️  跳过批量爬取测试: src/config/urls.txt 文件不存在")
    except Exception as e:
        print(f"\n⚠️  批量爬取测试出错: {str(e)}")

    print("\n测试完成!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
