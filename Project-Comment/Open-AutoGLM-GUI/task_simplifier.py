#!/usr/bin/env python3
"""
任务精简器模块 - AI驱动的任务描述精简工具
"""

import json
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI平台枚举"""
    DEEPSEEK = "deepseek"
    DOUBAO = "doubao"
    YUANBAO = "yuanbao"
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    GLM = "glm"
    WENXIN = "wenxin"
    TONGYI = "tongyi"


class TaskSimplifier:
    """任务精简器核心类"""
    
    def __init__(self, configs: Dict[AIProvider, Dict] = None):
        self.configs = configs or {}
        
    def _validate_config(self, provider: AIProvider, config: Dict) -> Dict[str, Any]:
        """
        验证配置参数的有效性
        
        Returns:
            包含验证结果的字典
        """
        try:
            # 验证API密钥
            api_key = config.get("api_key", "").strip()
            if not api_key:
                return {
                    "valid": False,
                    "error": f"{provider.value}平台的API密钥为空，请设置有效的API密钥",
                    "field": "api_key"
                }
            
            # 检查API密钥格式
            if provider == AIProvider.DEEPSEEK:
                if not api_key.startswith("sk-"):
                    return {
                        "valid": False,
                        "error": f"DeepSeek API密钥格式错误，正确格式应为: sk-xxxxx",
                        "field": "api_key"
                    }
                if len(api_key) < 20:
                    return {
                        "valid": False,
                        "error": f"DeepSeek API密钥长度不足，请检查是否完整",
                        "field": "api_key"
                    }
            
            elif provider == AIProvider.OPENAI:
                if not api_key.startswith("sk-"):
                    return {
                        "valid": False,
                        "error": f"OpenAI API密钥格式错误，正确格式应为: sk-xxxxx",
                        "field": "api_key"
                    }
                if len(api_key) < 20:
                    return {
                        "valid": False,
                        "error": f"OpenAI API密钥长度不足，请检查是否完整",
                        "field": "api_key"
                    }
            
            elif provider == AIProvider.DOUBAO:
                if len(api_key) < 16:
                    return {
                        "valid": False,
                        "error": f"豆包API密钥长度不足，请检查是否完整",
                        "field": "api_key"
                    }
            
            # 验证接口地址
            base_url = config.get("base_url", "").strip()
            if not base_url:
                return {
                    "valid": False,
                    "error": f"{provider.value}平台的接口地址为空，请设置正确的接口地址",
                    "field": "base_url"
                }
            
            # 验证URL格式
            if not (base_url.startswith("http://") or base_url.startswith("https://")):
                return {
                    "valid": False,
                    "error": f"接口地址格式错误，必须以http://或https://开头，当前地址: {base_url}",
                    "field": "base_url"
                }
            
            # 验证特定平台的URL
            if provider == AIProvider.DEEPSEEK:
                if "api.deepseek.com" not in base_url:
                    return {
                        "valid": False,
                        "error": f"DeepSeek接口地址不正确，正确地址应包含api.deepseek.com，当前地址: {base_url}",
                        "field": "base_url"
                    }
            
            elif provider == AIProvider.OPENAI:
                if "api.openai.com" not in base_url:
                    return {
                        "valid": False,
                        "error": f"OpenAI接口地址不正确，正确地址应包含api.openai.com，当前地址: {base_url}",
                        "field": "base_url"
                    }
            
            elif provider == AIProvider.DOUBAO:
                if "volcengine.com" not in base_url:
                    return {
                        "valid": False,
                        "error": f"豆包接口地址不正确，正确地址应包含volcengine.com，当前地址: {base_url}",
                        "field": "base_url"
                    }
            
            # 验证模型名称
            model = config.get("model", "").strip()
            if not model:
                return {
                    "valid": False,
                    "error": f"{provider.value}平台的模型名称为空，请选择有效的模型",
                    "field": "model"
                }
            
            # 验证特定平台的模型名称
            if provider == AIProvider.DEEPSEEK:
                valid_models = ["deepseek-chat", "deepseek-coder"]
                if model not in valid_models and not model.startswith("deepseek-"):
                    return {
                        "valid": False,
                        "error": f"DeepSeek模型名称不正确，常用模型: deepseek-chat, deepseek-coder，当前模型: {model}",
                        "field": "model"
                    }
            
            elif provider == AIProvider.OPENAI:
                valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
                if not any(model.startswith(vm) for vm in valid_models):
                    return {
                        "valid": False,
                        "error": f"OpenAI模型名称不正确，常用模型: gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o，当前模型: {model}",
                        "field": "model"
                    }
            
            elif provider == AIProvider.DOUBAO:
                if not (model.startswith("ep-") or model.startswith("doubao-")):
                    return {
                        "valid": False,
                        "error": f"豆包模型名称不正确，应以ep-或doubao-开头，当前模型: {model}",
                        "field": "model"
                    }
            
            # 验证超时设置
            timeout = config.get("timeout", 30)
            try:
                timeout = int(timeout)
                if timeout < 1 or timeout > 300:
                    return {
                        "valid": False,
                        "error": f"超时设置不合理，建议设置1-300秒之间，当前设置: {timeout}秒",
                        "field": "timeout"
                    }
            except (ValueError, TypeError):
                return {
                    "valid": False,
                    "error": f"超时设置格式错误，请输入数字，当前设置: {timeout}",
                    "field": "timeout"
                }
            
            # 验证最大Token数
            max_tokens = config.get("max_tokens", 200)
            try:
                max_tokens = int(max_tokens)
                if max_tokens < 1 or max_tokens > 8000:
                    return {
                        "valid": False,
                        "error": f"最大Token数设置不合理，建议设置1-8000之间，当前设置: {max_tokens}",
                        "field": "max_tokens"
                    }
            except (ValueError, TypeError):
                return {
                    "valid": False,
                    "error": f"最大Token数格式错误，请输入数字，当前设置: {max_tokens}",
                    "field": "max_tokens"
                }
            
            # 验证温度参数
            temperature = config.get("temperature", 0.1)
            try:
                temperature = float(temperature)
                if temperature < 0 or temperature > 2:
                    return {
                        "valid": False,
                        "error": f"温度参数设置不合理，应设置0-2之间，当前设置: {temperature}",
                        "field": "temperature"
                    }
            except (ValueError, TypeError):
                return {
                    "valid": False,
                    "error": f"温度参数格式错误，请输入数字，当前设置: {temperature}",
                    "field": "temperature"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"配置验证异常: {str(e)}",
                "field": "unknown"
            }

    async def simplify_task_async(self, task_description: str, provider: AIProvider) -> Dict[str, Any]:
        """
        异步精简任务描述
        
        Args:
            task_description: 原始任务描述
            provider: 使用的AI平台
            
        Returns:
            包含精简结果的字典
        """
        try:
            if provider not in self.configs:
                return {
                    "success": False,
                    "provider": provider.value,
                    "error": f"未找到{provider.value}平台的配置，请在API配置页面添加配置",
                    "simplified_task": task_description
                }
            
            config = self.configs[provider]
            
            # 首先验证配置
            validation = self._validate_config(provider, config)
            if not validation.get("valid"):
                return {
                    "success": False,
                    "provider": provider.value,
                    "error": validation.get("error"),
                    "field": validation.get("field"),
                    "simplified_task": task_description
                }
            
            # 根据不同平台调用相应的AI接口
            if provider == AIProvider.DEEPSEEK:
                result = await self._call_deepseek(task_description, config)
            elif provider == AIProvider.DOUBAO:
                result = await self._call_doubao(task_description, config)
            elif provider == AIProvider.YUANBAO:
                result = await self._call_yuanbao(task_description, config)
            elif provider == AIProvider.OPENAI:
                result = await self._call_openai(task_description, config)
            elif provider == AIProvider.GEMINI:
                result = await self._call_gemini(task_description, config)
            elif provider == AIProvider.CLAUDE:
                result = await self._call_claude(task_description, config)
            elif provider == AIProvider.GLM:
                result = await self._call_glm(task_description, config)
            elif provider == AIProvider.WENXIN:
                result = await self._call_wenxin(task_description, config)
            elif provider == AIProvider.TONGYI:
                result = await self._call_tongyi(task_description, config)
            else:
                result = {
                    "success": False,
                    "provider": provider.value,
                    "error": f"不支持的AI平台: {provider.value}",
                    "simplified_task": task_description
                }
            
            return result
            
        except Exception as e:
            logger.error(f"精简任务失败 ({provider.value}): {str(e)}")
            return {
                "success": False,
                "provider": provider.value,
                "error": str(e),
                "simplified_task": task_description
            }
    
    def simplify_task(self, task_description: str, provider: AIProvider) -> Dict[str, Any]:
        """
        同步精简任务描述
        
        Args:
            task_description: 原始任务描述
            provider: 使用的AI平台
            
        Returns:
            包含精简结果的字典
        """
        try:
            # 创建新的事件循环以避免GUI死锁
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.simplify_task_async(task_description, provider))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"精简任务失败: {str(e)}")
            return {
                "success": False,
                "provider": provider.value,
                "error": str(e),
                "simplified_task": task_description
            }
    
    async def simplify_task_multiple_providers(self, task_description: str, providers: List[AIProvider]) -> Dict[str, Any]:
        """
        使用多个AI平台精简任务，选择最佳结果
        
        Args:
            task_description: 原始任务描述
            providers: AI平台列表
            
        Returns:
            包含最佳精简结果的字典
        """
        try:
            results = []
            
            # 并发调用多个平台
            tasks = [self.simplify_task_async(task_description, provider) for provider in providers]
            provider_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(provider_results):
                if isinstance(result, Exception):
                    logger.error(f"平台 {providers[i].value} 调用异常: {str(result)}")
                    results.append({
                        "success": False,
                        "provider": providers[i].value,
                        "error": str(result),
                        "simplified_task": task_description
                    })
                else:
                    results.append(result)
            
            # 选择最佳结果
            successful_results = [r for r in results if r.get("success")]
            if successful_results:
                # 选择最简洁且保留关键信息的结果
                best_result = min(successful_results, key=lambda x: len(x.get("simplified_task", "")))
                best_result["all_results"] = results
                return best_result
            else:
                # 如果所有平台都失败，提供详细的错误汇总
                error_details = []
                for result in results:
                    provider = result.get("provider", "unknown")
                    error = result.get("error", "未知错误")
                    error_details.append(f"• {provider.upper()}: {error}")
                
                error_summary = f"所有AI平台都失败了:\n\n" + "\n".join(error_details[:3])  # 最多显示3个错误
                if len(error_details) > 3:
                    error_summary += f"\n\n还有{len(error_details)-3}个平台的错误..."
                
                return {
                    "success": False,
                    "error": error_summary,
                    "simplified_task": task_description,
                    "all_results": results
                }
                
        except Exception as e:
            logger.error(f"多平台精简任务失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "simplified_task": task_description
            }
    
    # AI平台调用方法
    async def _call_deepseek(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用DeepSeek API"""
        try:
            import aiohttp
            import json
            
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": config.get("model", "deepseek-chat"),
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的任务润色助手。请将用户提供的自然语言任务描述润色为简洁、明确、可执行的自动化指令。保留关键操作信息，去除冗余描述。"
                    },
                    {
                        "role": "user", 
                        "content": f"请润色以下任务：\n{task}"
                    }
                ],
                "max_tokens": config.get("max_tokens", 200),
                "temperature": config.get("temperature", 0.1)
            }
            
            timeout = aiohttp.ClientTimeout(total=config.get("timeout", 30))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        simplified = result["choices"][0]["message"]["content"].strip()
                        return {
                            "success": True,
                            "provider": "deepseek",
                            "simplified_task": simplified,
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "provider": "deepseek",
                            "error": f"API调用失败 ({response.status}): {error_text}",
                            "simplified_task": task
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "provider": "deepseek",
                "error": f"DeepSeek API请求超时({config.get('timeout', 30)}秒)，请检查网络或增加timeout设置",
                "simplified_task": task
            }
        except Exception as e:
            error_str = str(e)
            if "SSL" in error_str or "certificate" in error_str.lower():
                return {
                    "success": False,
                    "provider": "deepseek",
                    "error": f"DeepSeek SSL证书验证失败: {error_str}",
                    "simplified_task": task
                }
            elif "DNS" in error_str or "resolve" in error_str.lower():
                return {
                    "success": False,
                    "provider": "deepseek", 
                    "error": f"DeepSeek域名解析失败: {error_str}",
                    "simplified_task": task
                }
            else:
                return {
                    "success": False,
                    "provider": "deepseek",
                    "error": f"DeepSeek API调用异常: {error_str}",
                    "simplified_task": task
                }
    
    async def _call_doubao(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用豆包API"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": config.get("model", "ep-20241219143532-qz8wg"),
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的任务润色助手。请将用户提供的自然语言任务描述润色为简洁、明确、可执行的自动化指令。保留关键操作信息，去除冗余描述。"
                    },
                    {
                        "role": "user",
                        "content": f"请润色以下任务：\n{task}"
                    }
                ],
                "max_tokens": config.get("max_tokens", 200),
                "temperature": config.get("temperature", 0.1)
            }
            
            timeout = aiohttp.ClientTimeout(total=config.get("timeout", 30))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        simplified = result["choices"][0]["message"]["content"].strip()
                        return {
                            "success": True,
                            "provider": "doubao",
                            "simplified_task": simplified,
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "provider": "doubao",
                            "error": f"API调用失败 ({response.status}): {error_text}",
                            "simplified_task": task
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "provider": "doubao",
                "error": "请求超时，请检查网络连接或增加超时时间",
                "simplified_task": task
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "doubao",
                "error": str(e),
                "simplified_task": task
            }
    
    async def _call_yuanbao(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用腾讯元宝API"""
        try:
            # 使用OpenAI客户端库调用混元API
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            completion = await client.chat.completions.create(
                model=config.get("model", "hunyuan-lite"),
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的任务润色助手。请将用户提供的自然语言任务描述润色为简洁、明确、可执行的自动化指令。保留关键操作信息，去除冗余描述。"
                    },
                    {
                        "role": "user",
                        "content": f"请润色以下任务：\n{task}"
                    }
                ],
                max_tokens=config.get("max_tokens", 200),
                temperature=config.get("temperature", 0.1),
                extra_body={
                    "enable_enhancement": True,  # 混元自定义参数，启用增强功能
                }
            )
            
            simplified = completion.choices[0].message.content.strip()
            return {
                "success": True,
                "provider": "yuanbao",
                "simplified_task": simplified,
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                    "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                    "total_tokens": completion.usage.total_tokens if completion.usage else 0
                }
            }
                        
        except Exception as e:
            error_str = str(e)
            # 解析混元API的错误信息
            if "401" in error_str or "unauthorized" in error_str.lower():
                return {
                    "success": False,
                    "provider": "yuanbao",
                    "error": "腾讯元宝API密钥无效或已过期，请检查API密钥是否正确",
                    "simplified_task": task
                }
            elif "timeout" in error_str.lower():
                return {
                    "success": False,
                    "provider": "yuanbao",
                    "error": f"腾讯元宝API请求超时({config.get('timeout', 30)}秒)，请检查网络或增加timeout设置",
                    "simplified_task": task
                }
            elif "rate limit" in error_str.lower():
                return {
                    "success": False,
                    "provider": "yuanbao",
                    "error": "腾讯元宝API调用频率超限，请稍后重试",
                    "simplified_task": task
                }
            else:
                return {
                    "success": False,
                    "provider": "yuanbao",
                    "error": f"腾讯元宝API调用异常: {error_str}",
                    "simplified_task": task
                }
    
    async def _call_openai(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用OpenAI API"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": config.get("model", "gpt-3.5-turbo"),
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的任务润色助手。请将用户提供的自然语言任务描述润色为简洁、明确、可执行的自动化指令。保留关键操作信息，去除冗余描述。"
                    },
                    {
                        "role": "user",
                        "content": f"请润色以下任务：\n{task}"
                    }
                ],
                "max_tokens": config.get("max_tokens", 200),
                "temperature": config.get("temperature", 0.1)
            }
            
            timeout = aiohttp.ClientTimeout(total=config.get("timeout", 30))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        simplified = result["choices"][0]["message"]["content"].strip()
                        return {
                            "success": True,
                            "provider": "openai",
                            "simplified_task": simplified,
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "provider": "openai",
                            "error": f"API调用失败 ({response.status}): {error_text}",
                            "simplified_task": task
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "provider": "openai",
                "error": "请求超时，请检查网络连接或增加超时时间",
                "simplified_task": task
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "openai",
                "error": str(e),
                "simplified_task": task
            }
    
    async def _call_gemini(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用Google Gemini API"""
        return {
            "success": False,
            "provider": "gemini",
            "error": "Gemini API调用待实现",
            "simplified_task": task
        }
    
    async def _call_claude(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用Anthropic Claude API"""
        return {
            "success": False,
            "provider": "claude",
            "error": "Claude API调用待实现",
            "simplified_task": task
        }
    
    async def _call_glm(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用智谱GLM API"""
        return {
            "success": False,
            "provider": "glm",
            "error": "GLM API调用待实现",
            "simplified_task": task
        }
    
    async def _call_wenxin(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用百度文心千帆API"""
        try:
            import aiohttp
            import json
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # 构建请求数据
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"请将以下任务描述润色得更加清晰和易于理解，保持原意但表达更专业：\n\n{task}"
                    }
                ],
                "temperature": config.get("temperature", 0.1),
                "max_output_tokens": config.get("max_tokens", 200)
            }
            
            # 添加API密钥到URL或headers
            if "wenxin" in config['base_url']:
                # 文心千帆的认证方式
                data["access_token"] = config['api_key']
            
            timeout = aiohttp.ClientTimeout(total=config.get("timeout", 30))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    config['base_url'],
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        simplified = result.get("result", "").strip()
                        return {
                            "success": True,
                            "provider": "wenxin",
                            "simplified_task": simplified,
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "provider": "wenxin",
                            "error": f"API调用失败 ({response.status}): {error_text}",
                            "simplified_task": task
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "provider": "wenxin",
                "error": "请求超时，请检查网络连接或增加超时时间",
                "simplified_task": task
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "wenxin",
                "error": str(e),
                "simplified_task": task
            }
    
    async def _call_tongyi(self, task: str, config: Dict) -> Dict[str, Any]:
        """调用阿里通义千问API"""
        try:
            # 使用OpenAI客户端库调用通义千问API（兼容模式）
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            completion = await client.chat.completions.create(
                model=config.get("model", "qwen-plus"),
                messages=[
                    {
                        "role": "user",
                        "content": f"请将以下任务描述润色得更加清晰和易于理解，保持原意但表达更专业：\n\n{task}"
                    }
                ],
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 200)
            )
            
            simplified = completion.choices[0].message.content.strip()
            
            return {
                "success": True,
                "provider": "tongyi",
                "simplified_task": simplified,
                "usage": completion.usage.model_dump() if completion.usage else {}
            }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "provider": "tongyi",
                "error": "请求超时，请检查网络连接或增加超时时间",
                "simplified_task": task
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "tongyi",
                "error": str(e),
                "simplified_task": task
            }


class TaskSimplifierManager:
    """任务精简器管理类"""
    
    def __init__(self):
        self.simplifier = None
        self.config_file = "config/ai_config.json"
        self.load_config()
    
    def load_config(self):
        """加载AI配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 转换配置格式
                configs = {}
                for platform_name, platform_config in config_data.items():
                    try:
                        provider = AIProvider(platform_name)
                        configs[provider] = platform_config
                    except ValueError:
                        continue
                
                self.simplifier = TaskSimplifier(configs)
                logger.info(f"已加载 {len(configs)} 个AI平台配置")
            else:
                # 创建空的配置
                self.simplifier = TaskSimplifier()
                logger.info("未找到配置文件，使用默认配置")
                
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            self.simplifier = TaskSimplifier()
    
    def simplify_task(self, task_description: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        精简任务描述
        
        Args:
            task_description: 原始任务描述
            provider: 指定使用的AI平台，如果为None则使用最佳可用平台
            
        Returns:
            精简结果
        """
        if not self.simplifier:
            self.load_config()
        
        if provider:
            # 直接调用TaskSimplifier的同步方法
            return self.simplifier.simplify_task(task_description, AIProvider(provider))
        else:
            # 使用所有可用平台，选择最佳结果
            available_providers = [p for p in AIProvider 
                                 if p in self.simplifier.configs 
                                 and self.simplifier.configs[p].get("api_key")]
            
            if not available_providers:
                return {
                    "success": False,
                    "error": "没有配置可用的AI平台",
                    "simplified_task": task_description
                }
            
            # 直接调用TaskSimplifier的同步方法
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        self.simplifier.simplify_task_multiple_providers(
                            task_description, available_providers
                        )
                    )
                finally:
                    loop.close()
            except Exception as e:
                return {
                    "success": False,
                    "error": f"精简任务失败: {str(e)}",
                    "simplified_task": task_description
                }
    
    def get_available_providers(self) -> List[str]:
        """获取可用的AI平台列表"""
        if not self.simplifier:
            self.load_config()
        
        available_providers = []
        for provider in AIProvider:
            if provider in self.simplifier.configs and self.simplifier.configs[provider].get("api_key"):
                available_providers.append(provider.value)
        
        return available_providers
    
    def get_provider_status(self) -> Dict[str, bool]:
        """获取各AI平台的配置状态"""
        if not self.simplifier:
            self.load_config()
        
        status = {}
        for provider in AIProvider:
            status[provider.value] = (provider in self.simplifier.configs and 
                                    self.simplifier.configs[provider].get("api_key"))
        
        return status