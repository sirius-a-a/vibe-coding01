#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import os
from datetime import datetime

# ==================== 配置区域 ====================
DEEPSEEK_API_KEY = "sk-真实api"  # 替换成你的真实 Key
TAVILY_API_KEY = "tvly-真实api"  # 替换成你的 Tavily API Key
API_URL = "https://api.deepseek.com/chat/completions"
TAVILY_API_URL = "https://api.tavily.com/search"
MODEL = "deepseek-chat"
HISTORY_FILE = "deepseek_history.json"

# ==================== 辅助函数 ====================

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def check_need_search(user_input, conversation_context=None):
    """判断是否需要联网搜索"""
    messages = [
        {
            "role": "system",
            "content": "你是一个判断助手。你需要判断用户的问题是否需要联网搜索才能准确回答。\n\n"
                       "需要联网搜索的情况包括但不限于：\n"
                       "1. 询问实时信息（新闻、天气、股价、赛事结果等）\n"
                       "2. 询问最新动态、最新数据\n"
                       "3. 询问当前时间、日期相关的问题\n"
                       "4. 询问近期发生的事件\n"
                       "5. 询问需要最新资料的问题\n\n"
                       "不需要联网搜索的情况：\n"
                       "1. 通用知识问答\n"
                       "2. 编程问题\n"
                       "3. 数学问题\n"
                       "4. 常识性问题\n"
                       "5. 翻译、润色等文本处理\n\n"
                       "请只回复 '是' 或 '否'，不要有其他内容。"
        },
        {
            "role": "user",
            "content": f"用户问题：{user_input}\n\n是否需要联网搜索？"
        }
    ]
    
    try:
        response = call_deepseek_normal(messages, max_tokens=10, temperature=0)
        if response and response[0]:
            result = response[0].strip()
            return result == "是"
    except Exception as e:
        print(f"判断联网需求时出错: {e}")
    
    return False

def tavily_search(query):
    """调用 Tavily API 进行联网搜索"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TAVILY_API_KEY}"
    }
    
    data = {
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": 3
    }
    
    try:
        response = requests.post(TAVILY_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Tavily API 请求失败 (状态码: {response.status_code})")
            print(f"错误详情: {response.text}")
            return None
        
        result = response.json()
        return result
        
    except Exception as e:
        print(f"❌ Tavily API 调用失败: {e}")
        return None

def format_search_results(search_result):
    """格式化搜索结果，提取关键信息"""
    if not search_result:
        return "未能获取到搜索结果"
    
    # 优先使用 Tavily 的摘要
    if search_result.get("answer"):
        return search_result['answer']
    
    # 如果没有摘要，从搜索结果中提取
    if search_result.get("results"):
        first_result = search_result["results"][0]
        content = first_result.get("content", "")
        return content[:500]
    
    return "未找到相关信息"

def call_deepseek_normal(messages, temperature=0.7, max_tokens=2000):
    """非流式调用 DeepSeek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ API 请求失败 (状态码: {response.status_code})")
            print(f"错误详情: {response.text}")
            return None, None
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            return content, usage
        else:
            print("❌ API 返回数据格式异常")
            return None, None
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None, None

def process_with_search(user_input, messages_history):
    """处理需要联网搜索的请求"""
    print("\n🔍 正在联网搜索...")
    
    # 执行搜索
    search_result = tavily_search(user_input)
    
    if not search_result:
        print("⚠️ 联网搜索失败，将直接使用 AI 回答")
        return call_deepseek_normal(messages_history)
    
    # 提取搜索信息
    search_info = format_search_results(search_result)
    
    # 构建简洁的提示词，要求直接回答
    system_prompt = """你是一个智能助手。请基于搜索结果直接回答用户的问题。
要求：
1. 直接给出答案，不要冗长的解释
2. 不要列出多个来源
3. 不要说明你查看了哪些搜索结果
4. 简洁明了，一句话回答即可"""
    
    full_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"问题：{user_input}\n\n搜索结果：{search_info}\n\n请直接回答："}
    ]
    
    print("📡 正在生成回答...")
    return call_deepseek_normal(full_messages, temperature=0.3, max_tokens=500)

def process_normal(user_input, messages_history):
    """处理普通对话请求"""
    return call_deepseek_normal(messages_history)

def print_usage(usage):
    if usage:
        print(f"\n📊 Token 统计:")
        print(f"   - 输入 tokens: {usage.get('prompt_tokens', 0)}")
        print(f"   - 输出 tokens: {usage.get('completion_tokens', 0)}")
        print(f"   - 总计 tokens: {usage.get('total_tokens', 0)}")

def show_welcome():
    print("=" * 60)
    print("🌟 DeepSeek AI 助手 (支持联网搜索)")
    print("=" * 60)
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 使用模型: {MODEL}")
    print("💡 提示:")
    print("   - 直接输入问题开始对话")
    print("   - 系统会自动判断是否需要联网搜索")
    print("   - 输入 'clear' 清除当前对话历史")
    print("   - 输入 'save' 保存当前对话到文件")
    print("   - 输入 'history' 查看对话历史")
    print("   - 输入 'quit' 或 'exit' 退出程序")
    print("=" * 60)

# ==================== 主程序 ====================

def main():
    if DEEPSEEK_API_KEY == "sk-你的API_KEY":
        print("❌ 错误：请先在脚本中配置你的 DeepSeek API Key")
        print("获取地址: https://platform.deepseek.com/api_keys")
        sys.exit(1)
    
    if TAVILY_API_KEY == "tvly-你的API":
        print("⚠️ 警告：未配置 Tavily API Key，联网搜索功能将不可用")
        print("获取地址: https://app.tavily.com/")
    
    history = load_history()
    messages = history.copy() if history else []
    
    show_welcome()
    
    if messages:
        print(f"\n📂 已加载上次对话历史 ({len(messages)//2} 轮对话)")
        print("=" * 60)
    
    while True:
        try:
            print("\n你: ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！感谢使用 DeepSeek AI 助手")
                break
            elif user_input.lower() == 'clear':
                messages = []
                save_history([])
                print("✅ 对话历史已清除")
                continue
            elif user_input.lower() == 'save':
                save_history(messages)
                print(f"✅ 对话历史已保存到 {HISTORY_FILE}")
                continue
            elif user_input.lower() == 'history':
                if not messages:
                    print("📭 暂无对话历史")
                else:
                    print("\n📜 对话历史:")
                    print("=" * 40)
                    for i in range(0, len(messages), 2):
                        if i < len(messages):
                            print(f"👤 用户: {messages[i]['content'][:50]}...")
                        if i+1 < len(messages):
                            print(f"🤖 AI: {messages[i+1]['content'][:50]}...")
                        print("-" * 40)
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            print("\n⏳ 正在分析问题...")
            
            # 判断是否需要联网搜索
            need_search = False
            if TAVILY_API_KEY != "tvly-你的API":
                need_search = check_need_search(user_input, messages[:-1])
            
            # 根据判断结果选择处理方式
            if need_search:
                reply, usage = process_with_search(user_input, messages)
            else:
                print("💡 无需联网搜索")
                reply, usage = process_normal(user_input, messages)
            
            if reply:
                messages.append({"role": "assistant", "content": reply})
                print("\n🤖 DeepSeek: ", end="")
                print(reply)
                print_usage(usage)
                save_history(messages)
                total_rounds = len(messages) // 2
                print(f"💾 对话已保存 (共 {total_rounds} 轮)")
            else:
                messages.pop()
                print("❌ 本次对话失败，请重试")
                
        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，正在保存对话...")
            save_history(messages)
            print("✅ 对话已保存，再见！")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"❌ 发生意外错误: {e}")
            continue

if __name__ == "__main__":
    main()
