# 《如何扩展你的模型》中文翻译项目

> **原书价值**：这是一本揭开大语言模型扩展科学神秘面纱的权威技术指南，深入解析TPU和GPU的工作原理、LLM在真实硬件上的运行机制，以及如何在训练和推理过程中实现高效的模型并行化。

## 📖 关于原书《How to Scale Your Model》

[《How to Scale Your Model》](https://jax-ml.github.io/scaling-book/)是由Google DeepMind团队编写的技术电子书，专门讲解大语言模型的系统级优化。这本书解决了当今AI研究和工程中的核心问题：

### 为什么这本书如此重要？

- **填补理论与实践的鸿沟**：训练LLM常被视为"炼金术"，但本书将其科学化
- **硬件与算法的协同设计**：深入解析TPU/GPU架构如何影响模型设计
- **实用的工程指导**：提供具体的并行化策略和性能优化方案
- **前沿技术的系统梳理**：涵盖数据并行、张量并行、流水线并行等关键技术

### 核心内容概览

1. **Roofline分析**：理解计算、通信和内存限制
2. **TPU/GPU深度解析**：硬件架构与性能特性
3. **Transformer数学详解**：参数计算、FLOPs分析、内存需求
4. **并行化策略**：训练和推理的不同并行方案
5. **实战案例**：LLaMA-3在TPU上的训练和部署

## 📚 在线阅读

**在线阅读**：[《如何扩展你的模型》](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/scaling-book.html)

+ [第0部分：如何扩展你的模型全书大纲](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/scaling-book.html)
+ [第1部分：关于Roofline模型的一切](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/roofline.html)
+ [第2部分：如何理解TPU](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/tpus.html)
+ [第3部分：分片矩阵及其乘法](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/sharding.html)
+ [第4部分：你需要知道的所有Transformer数学知识](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/transformers.html)
+ [第5部分：如何为训练并行化Transformer](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/training.html)
+ [第6部分：在 TPU 上训练 LLaMA 3](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/applied-training.html)
+ [第7部分：Transformer 推理全解析](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/inference.html)
+ [第8部分：在 TPU 上服务 LLaMA 3-70B](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/applied-inference.html)
+ [第9部分：如何分析 TPU 程序](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/profiling.html)
+ [第10部分：在 JAX 中为 TPU 编程](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/jax-stuff.html)
+ [第11部分：如何理解 GPU](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/gpus.html)
+ [第12部分：结论与延伸阅读](https://skindhu.github.io/How-To-Scale-Your-Model-CN/article-trans/conclusion.html)

## 🚀 翻译难点：突破长文档翻译瓶颈

### 挑战：超长技术文档的翻译难题

原书单个章节动辄几万字，包含大量数学公式、代码块和复杂的HTML结构。传统翻译方法面临：
- **Token限制**：单次API调用无法处理完整章节
- **格式损坏**：数学公式和代码在翻译中易被破坏
- **上下文丢失**：分段翻译导致术语不一致

### 解决方案：智能HTML解析与占位符机制

本项目创新性地设计了一套完整的技术方案：

#### 1. **数学公式保护机制**
```python
# 核心思路：提取 → 占位 → 翻译 → 恢复
def _clean_body_for_translation(self, body_content: str) -> str:
    # 提取所有 <mjx-container> 数学公式标签
    mjx_containers = soup.find_all('mjx-container')
    for i, container in enumerate(mjx_containers):
        placeholder = f"MATH_PLACEHOLDER_{i:03d}"
        # 保存原始内容到存储字典
        self.math_content_store[placeholder] = str(container)
        # 用占位符替换
        container.replace_with(placeholder_tag)
```

#### 2. **分层翻译策略**
- **元数据翻译**：标题、描述单独处理
- **内容翻译**：Body部分智能清理后翻译
- **格式重组**：保持完整HTML结构

#### 3. **智能内容清理**
```python
# 移除不需要翻译的内容，减少Token消耗
- HTML注释自动过滤
- JavaScript代码保护
- CSS样式保持不变
- 数学公式占位符处理
```

#### 4. **术语一致性保障**
```python
self.terminology = {
    "TPU": "TPU",
    "roofline": "Roofline",
    "sharding": "分片",
    # ... 50+专业术语对照表
}
```

### 技术架构优势

- **🔄 完整流水线**：爬取 → 翻译 → 链接本地化 → 页头信息添加
- **🛡️ 格式保护**：数学公式、代码块、图表完美保留
- **⚡ 智能跳过**：已处理文件自动跳过，支持增量更新
- **📊 详细统计**：翻译进度、成功率、耗时等全程监控

## 🛠️ 技术栈

- **Python 3.8+** - 核心开发语言
- **crawl4ai** - 智能网页内容提取
- **Google Gemini API** - 高质量AI翻译引擎
- **BeautifulSoup4** - HTML解析和处理
- **Pydantic** - 数据验证和结构化响应

## 📁 项目结构

```
How-To-Scale-Your-Model-Trans/
├── main.py                 # 主程序入口，整合所有流程
├── src/                    # 核心源代码
│   ├── crawler.py         # 网页爬取模块
│   ├── translator.py      # 智能翻译引擎
│   ├── link_localizer.py  # 链接本地化处理
│   ├── header_info_adder.py # 页头信息添加
│   ├── gemini_api.py      # Gemini API封装
│   └── config/            # 配置管理
├── output/                # 输出目录（执行后才有）
│   ├── origin/           # 原始爬取的HTML文件
│   └── trans/            # 翻译后的HTML文件
└── requirements.txt      # 项目依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd How-To-Scale-Your-Model-Trans

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp env.example .env
# 编辑 .env 文件，添加你的 Gemini API Key
```

### 2. 配置URL列表

编辑 `src/config/urls.txt`，添加要翻译的URL：
```
https://jax-ml.github.io/scaling-book/
https://jax-ml.github.io/scaling-book/roofline
https://jax-ml.github.io/scaling-book/tpus
# ... 更多章节URL
```

### 3. 运行完整流水线

```bash
# 运行完整翻译流程
python main.py
```

这将自动执行：
1. 📡 **爬取网页**：从URLs获取原始HTML
2. 🌍 **智能翻译**：保护格式的高质量翻译
3. 🔗 **链接本地化**：转换外部链接为本地相对路径
4. 📝 **添加页头**：插入原文链接和译者信息


## 🤝 贡献指南

欢迎提交Issue和Pull Request！特别欢迎：
- 新的翻译引擎集成
- 更多文档格式支持
- 翻译质量优化建议
- 性能改进方案

## 📄 许可证

本项目采用 MIT 许可证。

---

**🌟 如果这个项目对你有帮助，请给个Star支持！**

**译者：北极的树** | **原书：Google DeepMind团队**

## 📱 关注作者

### 微信公众号
扫码关注作者的微信公众号，获取更多AI技术分享：

<img src="https://wechat-account-1251781786.cos.ap-guangzhou.myqcloud.com/wechat_account.jpeg" width="200" alt="微信公众号二维码">

### 其他项目
🔗 **也可以关注作者的另一个项目**：[《从零构建大语言模型》中文版](https://github.com/skindhu/Build-A-Large-Language-Model-CN)

一个从零开始构建大语言模型的完整教程，涵盖模型架构、训练技巧和实战案例。
