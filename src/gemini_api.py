import os
from dotenv import load_dotenv
from google import genai  # 使用新的导入方式
from google.genai import types

class GeminiAPI:
    """Google Gemini API封装，使用Google Gen AI SDK"""

    def __init__(self, api_key=None):
        """
        初始化Google Gemini API

        Args:
            api_key (str, optional): API密钥，如果为None则从环境变量中读取
        """
        # 加载环境变量
        load_dotenv()

        # 从环境变量或参数获取API密钥
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("未提供Gemini API密钥，也未在环境变量中找到GEMINI_API_KEY")

        # 默认模型和配置
        self.model_name = os.getenv('GEMINI_MODEL_NAME', "gemini-2.5-pro")
        self.temperature = 0.7  # 默认温度参数

        # 设置API选项并初始化客户端
        self._configure_gemini_api()


    def _configure_gemini_api(self):
        """配置Google Gemini API客户端"""
        # 创建客户端实例
        proxy_url = os.getenv('GEMINI_BASE_URL')
        self.client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(api_version='v1beta', base_url=proxy_url, timeout=2400000))

        print(f"已初始化Gemini API客户端，使用模型: {self.model_name}")

    def generate_text(self, prompt):
        """
        使用Gemini API生成文本

        Args:
            prompt (str): 提示词

        Returns:
            str: 生成的文本
        """
        try:
            # 使用新的SDK调用方式
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature= self.temperature)
            )

            # 提取并返回生成的文本
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts'):
                return ''.join([part.text for part in response.parts if hasattr(part, 'text')])
            else:
                raise RuntimeError("API响应格式异常，无法提取生成的文本")

        except Exception as e:
            raise RuntimeError(f"Gemini API调用失败: {str(e)}")


    def generate_structured_content(self, prompt, response_schema):
        """
        使用Gemini API生成结构化内容

        Args:
            prompt (str): 提示词
            response_schema: Pydantic模型类，用于定义响应结构

        Returns:
            解析后的结构化对象
        """
        try:
            # 使用结构化输出配置
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )
            )

            # 提取文本内容
            if hasattr(response, 'text'):
                json_text = response.text
            elif hasattr(response, 'parts'):
                json_text = ''.join([part.text for part in response.parts if hasattr(part, 'text')])
            else:
                raise RuntimeError("API响应格式异常，无法提取生成的文本")

            # 解析为结构化对象
            return response_schema.model_validate_json(json_text)

        except Exception as e:
            raise RuntimeError(f"Gemini结构化输出API调用失败: {str(e)}")

    def generate_content_stream(self, prompt):
        """
        使用Gemini API生成流式文本输出

        Args:
            prompt (str): 提示词

        Yields:
            str: 生成的文本块
        """
        try:
            # 使用流式生成
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=self.temperature)
            )

            # 流式输出每个chunk
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text

        except Exception as e:
            raise RuntimeError(f"Gemini流式API调用失败: {str(e)}")

    def generate_text_with_stream(self, prompt, show_progress=True):
        """
        使用流式输出生成完整文本，可选择显示进度

        Args:
            prompt (str): 提示词
            show_progress (bool): 是否显示生成进度

        Returns:
            str: 完整的生成文本
        """
        try:
            full_text = ""

            for chunk_text in self.generate_content_stream(prompt):
                full_text += chunk_text
                if show_progress:
                    print(chunk_text, end="", flush=True)

            if show_progress:
                print()  # 换行

            return full_text

        except Exception as e:
            raise RuntimeError(f"流式文本生成失败: {str(e)}")

    def generate_structured_content_stream(self, prompt, response_schema):
        """
        使用Gemini API生成流式结构化内容输出

        Args:
            prompt (str): 提示词
            response_schema: Pydantic模型类，用于定义响应结构

        Yields:
            str: 生成的JSON文本块
        """
        try:
            # 使用流式生成结构化内容
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )
            )

            # 流式输出每个chunk
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text

        except Exception as e:
            raise RuntimeError(f"Gemini流式结构化输出API调用失败: {str(e)}")

    def generate_structured_content_with_stream(self, prompt, response_schema, show_progress=True):
        """
        使用流式输出生成完整结构化内容，可选择显示进度

        Args:
            prompt (str): 提示词
            response_schema: Pydantic模型类，用于定义响应结构
            show_progress (bool): 是否显示生成进度

        Returns:
            解析后的结构化对象
        """
        try:
            full_json_text = ""

            for chunk_text in self.generate_structured_content_stream(prompt, response_schema):
                full_json_text += chunk_text
                if show_progress:
                    print(chunk_text, end="", flush=True)

            if show_progress:
                print()  # 换行

            # 解析为结构化对象
            return response_schema.model_validate_json(full_json_text)

        except Exception as e:
            raise RuntimeError(f"流式结构化内容生成失败: {str(e)}")
