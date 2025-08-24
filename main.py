#!/usr/bin/env python3
"""
主程序入口
整合所有翻译流程模块：爬虫 → 翻译 → 链接本地化 → 页头信息添加

创建时间：2024-12-19
项目：系列技术文章翻译
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# 添加src目录到Python路径
sys.path.insert(0, 'src')

# 导入各个模块
from crawler import WebCrawler, crawl_from_file
from translator import HTMLTranslator, translate_html_file
from link_localizer import LinkLocalizer
from header_info_adder import HeaderInfoAdder
from config.logging_config import setup_logging
from config.settings import Config


class TranslationPipeline:
    """翻译流水线，整合所有处理步骤"""

    def __init__(self, config: Config = None):
        """
        初始化翻译流水线

        Args:
            config (Config): 配置对象，如果未提供则使用默认配置
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)

        # 初始化各个组件
        self.crawler = None
        self.translator = None
        self.link_localizer = None
        self.header_adder = None

        # 流程统计信息
        self.stats = {
            'crawl_success': 0,
            'crawl_failed': 0,
            'translate_success': 0,
            'translate_failed': 0,
            'translate_skipped': 0,
            'localize_links': 0,
            'add_headers': 0,
            'total_time': 0
        }

        self.logger.info("翻译流水线初始化完成")

    async def initialize_components(self):
        """初始化所有组件"""
        try:
            self.logger.info("正在初始化各个组件...")

            # 初始化爬虫
            self.crawler = WebCrawler()
            self.logger.info("✅ 爬虫组件初始化完成")

            # 初始化翻译器
            self.translator = HTMLTranslator()
            self.logger.info("✅ 翻译器组件初始化完成")

            # 初始化链接本地化器
            self.link_localizer = LinkLocalizer()
            self.logger.info("✅ 链接本地化器初始化完成")

            # 初始化页头信息添加器
            self.header_adder = HeaderInfoAdder()
            self.logger.info("✅ 页头信息添加器初始化完成")

            self.logger.info("🎉 所有组件初始化完成")

        except Exception as e:
            self.logger.error(f"组件初始化失败: {str(e)}")
            raise

    async def step1_crawl_pages(self, urls_file: str = "src/config/urls.txt") -> bool:
        """
        步骤1：爬取网页内容

        Args:
            urls_file (str): URL配置文件路径

        Returns:
            bool: 是否成功
        """
        self.logger.info("=" * 60)
        self.logger.info("📡 步骤1：开始爬取网页内容")
        self.logger.info("=" * 60)

        try:
            # 检查URL文件是否存在
            if not Path(urls_file).exists():
                self.logger.error(f"URL配置文件不存在: {urls_file}")
                return False

            # 从文件读取URL并批量爬取
            results = await crawl_from_file(urls_file)

            if not results:
                self.logger.error("未能爬取到任何内容")
                return False

            # 统计结果
            success_count = sum(1 for r in results if r.get('success', False))
            failed_count = len(results) - success_count

            self.stats['crawl_success'] = success_count
            self.stats['crawl_failed'] = failed_count

            self.logger.info(f"✅ 爬取完成: 成功 {success_count} 个，失败 {failed_count} 个")

            return success_count > 0

        except Exception as e:
            self.logger.error(f"爬取阶段失败: {str(e)}")
            return False

    async def step2_translate_pages(self, force_translate: bool = False) -> bool:
        """
        步骤2：翻译爬取的HTML页面

        Args:
            force_translate (bool): 是否强制翻译，即使翻译文件已存在

        Returns:
            bool: 是否成功
        """
        self.logger.info("=" * 60)
        self.logger.info("🌍 步骤2：开始翻译HTML页面")
        self.logger.info("=" * 60)

        try:
            # 获取所有原始HTML文件
            origin_dir = Path(self.config.ORIGIN_DIR)
            html_files = list(origin_dir.glob("*.html"))

            if not html_files:
                self.logger.error(f"未找到原始HTML文件在目录: {origin_dir}")
                return False

            self.logger.info(f"找到 {len(html_files)} 个HTML文件需要翻译")

            success_count = 0
            failed_count = 0
            skipped_count = 0

            # 逐个翻译文件
            for html_file in html_files:
                try:
                    self.logger.info(f"处理文件: {html_file.name}")

                    # 使用translate_html_file函数，它会自动检查文件是否已存在
                    result = await translate_html_file(str(html_file), force_translate)

                    if result:
                        # 检查是否是跳过的文件
                        trans_dir = Path(self.config.TRANS_DIR)
                        target_file = trans_dir / html_file.name
                        if target_file.exists() and not force_translate:
                            if "跳过已翻译文件" in str(result) or result == str(target_file):
                                skipped_count += 1
                                self.logger.info(f"⏭️  {html_file.name} 已存在，跳过翻译")
                            else:
                                success_count += 1
                                self.logger.info(f"✅ {html_file.name} 翻译完成")
                        else:
                            success_count += 1
                            self.logger.info(f"✅ {html_file.name} 翻译完成")
                    else:
                        failed_count += 1
                        self.logger.error(f"❌ {html_file.name} 翻译失败")

                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"❌ {html_file.name} 翻译出错: {str(e)}")

            self.stats['translate_success'] = success_count
            self.stats['translate_failed'] = failed_count
            self.stats['translate_skipped'] = skipped_count

            self.logger.info(f"✅ 翻译阶段完成:")
            self.logger.info(f"   📁 总文件数: {len(html_files)}")
            self.logger.info(f"   ✅ 翻译成功: {success_count}")
            self.logger.info(f"   ⏭️  跳过文件: {skipped_count}")
            self.logger.info(f"   ❌ 翻译失败: {failed_count}")

            # 只要有文件被处理（翻译或跳过）就认为成功
            return (success_count + skipped_count) > 0

        except Exception as e:
            self.logger.error(f"翻译阶段失败: {str(e)}")
            return False

    async def step3_localize_links(self) -> bool:
        """
        步骤3：本地化链接

        Returns:
            bool: 是否成功
        """
        self.logger.info("=" * 60)
        self.logger.info("🔗 步骤3：开始本地化链接")
        self.logger.info("=" * 60)

        try:
            # 构建URL映射
            self.link_localizer.build_url_mapping()

            # 处理所有文件
            stats = self.link_localizer.process_all_files()

            self.stats['localize_links'] = stats.get('links_converted', 0)

            self.logger.info(f"✅ 链接本地化完成:")
            self.logger.info(f"   📁 处理文件: {stats.get('files_processed', 0)} 个")
            self.logger.info(f"   🔗 转换链接: {stats.get('links_converted', 0)} 个")

            return True

        except Exception as e:
            self.logger.error(f"链接本地化阶段失败: {str(e)}")
            return False

    async def step4_add_headers(self) -> bool:
        """
        步骤4：添加页头信息

        Returns:
            bool: 是否成功
        """
        self.logger.info("=" * 60)
        self.logger.info("📝 步骤4：开始添加页头信息")
        self.logger.info("=" * 60)

        try:
            # 处理所有文件
            stats = self.header_adder.process_all_files()

            self.stats['add_headers'] = stats.get('headers_added', 0)

            self.logger.info(f"✅ 页头信息添加完成:")
            self.logger.info(f"   📁 处理文件: {stats.get('files_processed', 0)} 个")
            self.logger.info(f"   🏷️  添加页头: {stats.get('headers_added', 0)} 个")

            return True

        except Exception as e:
            self.logger.error(f"页头信息添加阶段失败: {str(e)}")
            return False

    async def run_full_pipeline(self, urls_file: str = "src/config/urls.txt") -> Dict:
        """
        运行完整的翻译流水线

        Args:
            urls_file (str): URL配置文件路径

        Returns:
            Dict: 流程统计信息
        """
        start_time = time.time()

        self.logger.info("🚀 开始运行完整翻译流水线")
        self.logger.info("流程：爬虫 → 翻译 → 链接本地化 → 页头信息添加")

        try:
            # 初始化所有组件
            await self.initialize_components()

            # 步骤1：爬取网页
            if not await self.step1_crawl_pages(urls_file):
                self.logger.error("❌ 爬取阶段失败，终止流程")
                return self.stats

            # 步骤2：翻译页面
            if not await self.step2_translate_pages():
                self.logger.error("❌ 翻译阶段失败，终止流程")
                return self.stats

            # 步骤3：本地化链接
            if not await self.step3_localize_links():
                self.logger.error("❌ 链接本地化失败，终止流程")
                return self.stats

            # 步骤4：添加页头信息
            if not await self.step4_add_headers():
                self.logger.error("❌ 页头信息添加失败，终止流程")
                return self.stats

            # 计算总耗时
            self.stats['total_time'] = time.time() - start_time

            # 显示最终统计
            self.show_final_stats()

            return self.stats

        except Exception as e:
            self.logger.error(f"流水线执行失败: {str(e)}")
            return self.stats

    def show_final_stats(self):
        """显示最终统计信息"""
        self.logger.info("=" * 80)
        self.logger.info("🎉 翻译流水线执行完成！")
        self.logger.info("=" * 80)

        self.logger.info("📊 执行统计:")
        self.logger.info(f"   📡 爬取成功: {self.stats['crawl_success']} 个页面")
        self.logger.info(f"   📡 爬取失败: {self.stats['crawl_failed']} 个页面")
        self.logger.info(f"   🌍 翻译成功: {self.stats['translate_success']} 个页面")
        self.logger.info(f"   ⏭️  翻译跳过: {self.stats['translate_skipped']} 个页面")
        self.logger.info(f"   🌍 翻译失败: {self.stats['translate_failed']} 个页面")
        self.logger.info(f"   🔗 本地化链接: {self.stats['localize_links']} 个")
        self.logger.info(f"   📝 添加页头: {self.stats['add_headers']} 个")
        self.logger.info(f"   ⏱️  总耗时: {self.stats['total_time']:.2f} 秒")

        # 计算成功率
        total_pages = self.stats['crawl_success'] + self.stats['crawl_failed']
        if total_pages > 0:
            success_rate = (self.stats['translate_success'] / total_pages) * 100
            self.logger.info(f"   📈 成功率: {success_rate:.1f}%")

        self.logger.info("=" * 80)

        # 检查输出目录
        trans_dir = Path(self.config.TRANS_DIR)
        if trans_dir.exists():
            html_files = list(trans_dir.glob("*.html"))
            self.logger.info(f"✨ 翻译完成的文件位于: {trans_dir}")
            self.logger.info(f"📁 共生成 {len(html_files)} 个翻译文件")


# 便捷函数
async def run_full_translation(urls_file: str = "src/config/urls.txt") -> Dict:
    """
    便捷函数：运行完整翻译流程

    Args:
        urls_file (str): URL配置文件路径

    Returns:
        Dict: 执行统计信息
    """
    pipeline = TranslationPipeline()
    return await pipeline.run_full_pipeline(urls_file)


async def run_single_step(step: str, **kwargs) -> bool:
    """
    便捷函数：运行单个步骤

    Args:
        step (str): 步骤名称 ('crawl', 'translate', 'localize', 'headers')
        **kwargs: 步骤参数

    Returns:
        bool: 是否成功
    """
    pipeline = TranslationPipeline()
    await pipeline.initialize_components()

    if step == 'crawl':
        return await pipeline.step1_crawl_pages(kwargs.get('urls_file', 'src/config/urls.txt'))
    elif step == 'translate':
        return await pipeline.step2_translate_pages()
    elif step == 'localize':
        return await pipeline.step3_localize_links()
    elif step == 'headers':
        return await pipeline.step4_add_headers()
    else:
        raise ValueError(f"未知步骤: {step}")


async def main():
    """主函数"""
    # 设置日志
    setup_logging('INFO')

    print("=" * 80)
    print("🌍 JAX Scaling Book 翻译流水线")
    print("=" * 80)
    print("流程：爬虫 → 翻译 → 链接本地化 → 页头信息添加")
    print()

    # 检查必要文件
    urls_file = "src/config/urls.txt"
    if not Path(urls_file).exists():
        print(f"❌ 错误: URL配置文件不存在: {urls_file}")
        print("请确保该文件存在并包含要爬取的URL列表")
        return

    try:
        # 运行完整流水线
        stats = await run_full_translation(urls_file)

        if stats['translate_success'] > 0:
            print("\n🎉 翻译流水线执行成功！")
            print("您可以在 output/trans/ 目录中查看翻译结果")
        else:
            print("\n⚠️  翻译流水线执行完成，但没有成功翻译任何页面")
            print("请检查日志以了解详细信息")

    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
