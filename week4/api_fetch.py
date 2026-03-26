#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import os
from datetime import datetime

# ==================== 配置区域 ====================
DEEPSEEK_API_KEY = "sk-你的API"  # 替换成你的真实 Key
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
HISTORY_FILE = "deepseek_history.json"

# ==================== 辅助函数 ====================

def print_colored(text, color="green", end="\n"):
    """在终端打印彩色文字（支持 end 参数）"""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}", end=end)

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

def call_deepseek_stream(messages):
    """流式调用 DeepSeek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True, timeout=30)
        
        if response.status_code != 200:
            print_colored(f"❌ API 请求失败 (状态码: {response.status_code})", "red")
            print(f"错误详情: {response.text}")
            return None, None
        
        full_content = ""
        print_colored("\n🤖 DeepSeek: ", "blue", end="")
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    line = line[6:]
                    if line == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                print(content, end="", flush=True)
                                full_content += content
                    except json.JSONDecodeError:
                        continue
        
        print()
        estimated_tokens = len(full_content) // 2
        return full_content, {"prompt_tokens": 0, "completion_tokens": estimated_tokens, "total_tokens": estimated_tokens}
        
    except Exception as e:
        print_colored(f"❌ 发生错误: {e}", "red")
        return None, None

def call_deepseek_normal(messages):
    """非流式调用 DeepSeek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            print_colored(f"❌ API 请求失败 (状态码: {response.status_code})", "red")
            return None, None
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            return content, usage
        else:
            print_colored("❌ API 返回数据格式异常", "red")
            return None, None
            
    except Exception as e:
        print_colored(f"❌ 发生错误: {e}", "red")
        return None, None

def print_usage(usage):
    if usage:
        print_colored(f"\n📊 Token 统计:", "yellow")
        print(f"   - 输入 tokens: {usage.get('prompt_tokens', 0)}")
        print(f"   - 输出 tokens: {usage.get('completion_tokens', 0)}")
        print(f"   - 总计 tokens: {usage.get('total_tokens', 0)}")

def show_welcome():
    print("=" * 60)
    print_colored("🌟 DeepSeek AI 助手 (多轮对话版)", "green")
    print("=" * 60)
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 使用模型: {MODEL}")
    print("💡 提示:")
    print("   - 直接输入问题开始对话")
    print("   - 输入 'clear' 清除当前对话历史")
    print("   - 输入 'save' 保存当前对话到文件")
    print("   - 输入 'history' 查看对话历史")
    print("   - 输入 'quit' 或 'exit' 退出程序")
    print("=" * 60)

# ==================== 主程序 ====================

def main():
    if DEEPSEEK_API_KEY == "sk-你的API_KEY":
        print_colored("❌ 错误：请先在脚本中配置你的 DeepSeek API Key", "red")
        print("获取地址: https://platform.deepseek.com/api_keys")
        sys.exit(1)
    
    history = load_history()
    messages = history.copy() if history else []
    
    show_welcome()
    
    if messages:
        print_colored(f"\n📂 已加载上次对话历史 ({len(messages)//2} 轮对话)", "yellow")
        print("=" * 60)
    
    while True:
        try:
            print_colored("\n你: ", "green", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_colored("\n👋 再见！感谢使用 DeepSeek AI 助手", "yellow")
                break
            elif user_input.lower() == 'clear':
                messages = []
                save_history([])
                print_colored("✅ 对话历史已清除", "green")
                continue
            elif user_input.lower() == 'save':
                save_history(messages)
                print_colored(f"✅ 对话历史已保存到 {HISTORY_FILE}", "green")
                continue
            elif user_input.lower() == 'history':
                if not messages:
                    print_colored("📭 暂无对话历史", "yellow")
                else:
                    print_colored("\n📜 对话历史:", "blue")
                    print("=" * 40)
                    for i in range(0, len(messages), 2):
                        if i < len(messages):
                            print(f"👤 用户: {messages[i]['content'][:50]}...")
                        if i+1 < len(messages):
                            print(f"🤖 AI: {messages[i+1]['content'][:50]}...")
                        print("-" * 40)
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            print_colored("\n⏳ DeepSeek 正在思考...", "yellow")
            
            reply, usage = call_deepseek_stream(messages)
            
            if reply is None:
                print_colored("🔄 尝试使用非流式模式...", "yellow")
                reply, usage = call_deepseek_normal(messages)
            
            if reply:
                messages.append({"role": "assistant", "content": reply})
                print_usage(usage)
                save_history(messages)
                total_rounds = len(messages) // 2
                print_colored(f"💾 对话已自动保存 (共 {total_rounds} 轮)", "yellow")
            else:
                messages.pop()
                print_colored("❌ 本次对话失败，请重试", "red")
                
        except KeyboardInterrupt:
            print_colored("\n\n👋 检测到中断，正在保存对话...", "yellow")
            save_history(messages)
            print_colored("✅ 对话已保存，再见！", "green")
            break
        except EOFError:
            break
        except Exception as e:
            print_colored(f"❌ 发生意外错误: {e}", "red")
            continue

if __name__ == "__main__":
    main()