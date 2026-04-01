#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import os
from datetime import datetime

# ==================== 配置区域 ====================
MOONSHOT_API_KEY = "sk-真实api"
API_URL = "https://api.moonshot.cn/v1/chat/completions"
MODEL = "kimi-k2.5"
MAX_TOTAL_TOKENS = 30000
MAX_SEARCH_ROUNDS = 2
TEMPERATURE = 0.6
HISTORY_FILE = "kimi_history.json"

# 联网搜索工具定义
WEB_SEARCH_TOOL = {
    "type": "builtin_function",
    "function": {
        "name": "$web_search",
    }
}

# ==================== 辅助函数 ====================

def print_colored(text, color="green", end="\n"):
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
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

def check_token_limit(usage, operation_name=""):
    if not usage:
        return False, ""
    
    total_tokens = usage.get('total_tokens', 0)
    if total_tokens > MAX_TOTAL_TOKENS:
        warning_msg = f"⚠️ Token 消耗超限！本次消耗 {total_tokens} tokens，超过限制 {MAX_TOTAL_TOKENS}"
        if operation_name:
            warning_msg = f"⚠️ {operation_name} 消耗 {total_tokens} tokens，超过限制 {MAX_TOTAL_TOKENS}"
        return True, warning_msg
    return False, ""

def call_kimi_with_search(messages):
    """
    支持联网搜索的 Kimi API 调用
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MOONSHOT_API_KEY}"
    }
    
    current_messages = messages.copy()
    tools = [WEB_SEARCH_TOOL]
    
    total_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
    
    search_round = 0
    search_occurred = False
    
    while search_round <= MAX_SEARCH_ROUNDS:
        # 构建请求数据，明确禁用思考能力
        data = {
            "model": MODEL,
            "messages": current_messages,
            "stream": False,
            "temperature": TEMPERATURE,
            "max_tokens": 8192,
            "tools": tools,
            "tool_choice": "auto"
        }
        
        # 添加禁用思考能力的配置（根据官方文档）
        # 注意：这里使用 extra_body 字段来传递额外参数
        # 如果直接传递不被接受，可能需要调整
        
        # 尝试添加禁用思考的配置
        data["thinking"] = {"type": "disabled"}
        
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=120)
            
            if response.status_code != 200:
                error_msg = f"API 请求失败 (状态码: {response.status_code})\n错误详情: {response.text}"
                print_colored(f"❌ {error_msg}", "red")
                return None, None, error_msg
            
            result = response.json()
            
            if "choices" not in result or len(result["choices"]) == 0:
                error_msg = "API 返回数据格式异常"
                print_colored(f"❌ {error_msg}", "red")
                return None, None, error_msg
            
            usage = result.get("usage", {})
            total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
            total_usage["total_tokens"] += usage.get("total_tokens", 0)
            
            is_over, warning = check_token_limit(usage, f"第 {search_round + 1} 轮请求")
            if is_over:
                print_colored(f"\n{warning}", "red")
                return None, total_usage, warning
            
            choice = result["choices"][0]
            finish_reason = choice.get("finish_reason")
            message = choice.get("message", {})
            
            # 检查是否需要工具调用
            if finish_reason == "tool_calls" and message.get("tool_calls"):
                search_round += 1
                search_occurred = True
                tool_calls = message.get("tool_calls", [])
                
                print_colored(f"\n🔍 检测到工具调用请求 (第 {search_round} 轮)", "cyan")
                
                # 添加 assistant 消息
                assistant_message = {
                    "role": "assistant",
                    "content": message.get("content", ""),
                    "tool_calls": tool_calls
                }
                
                # 如果有 reasoning_content，也添加进去
                if "reasoning_content" in message:
                    assistant_message["reasoning_content"] = message["reasoning_content"]
                
                current_messages.append(assistant_message)
                
                # 执行每个工具调用
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_arguments = json.loads(tool_call["function"]["arguments"])
                    
                    if tool_name == "$web_search":
                        # 显示搜索信息
                        usage_tokens = tool_arguments.get("usage", {}).get("total_tokens", 0)
                        search_id = tool_arguments.get("search_result", {}).get("search_id", "")
                        print_colored(f"   🔍 联网搜索已执行", "cyan")
                        if usage_tokens > 0:
                            print_colored(f"   📊 搜索结果消耗: {usage_tokens} tokens", "yellow")
                        if search_id:
                            print_colored(f"   🆔 搜索ID: {search_id}", "cyan")
                        
                        # 对于内置的 $web_search，直接返回参数
                        tool_result = tool_arguments
                    else:
                        tool_result = {"error": f"未知工具: {tool_name}"}
                        print_colored(f"   ⚠️ 未知工具: {tool_name}", "red")
                    
                    # 添加工具执行结果
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                
                # 继续循环
                print_colored(f"\n🔄 正在根据搜索结果生成回答...", "cyan")
                continue
            
            # 获取最终回答
            final_content = message.get("content", "")
            
            if search_occurred:
                print_colored(f"\n✅ 联网搜索完成，共 {search_round} 轮搜索", "green")
            
            return final_content, total_usage, None
            
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请检查网络连接后重试"
            print_colored(f"❌ {error_msg}", "red")
            return None, total_usage, error_msg
        except Exception as e:
            error_msg = f"发生错误: {e}"
            print_colored(f"❌ {error_msg}", "red")
            return None, total_usage, error_msg
    
    error_msg = f"联网搜索次数超过限制 ({MAX_SEARCH_ROUNDS} 次)，已停止"
    print_colored(f"\n⚠️ {error_msg}", "red")
    return None, total_usage, error_msg

def print_usage(usage):
    if usage and usage.get('total_tokens', 0) > 0:
        print_colored(f"\n📊 Token 统计:", "yellow")
        print(f"   - 输入 tokens: {usage.get('prompt_tokens', 0)}")
        print(f"   - 输出 tokens: {usage.get('completion_tokens', 0)}")
        print(f"   - 总计 tokens: {usage.get('total_tokens', 0)}")
        print(f"   - 限制阈值: {MAX_TOTAL_TOKENS}")

def show_welcome():
    print("=" * 60)
    print_colored("🌟 Kimi AI 助手 (支持联网搜索)", "green")
    print("=" * 60)
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 使用模型: {MODEL}")
    print(f"🌐 联网搜索: 已启用（内置 $web_search 工具）")
    print(f"💰 Token 限制: 单次对话最多 {MAX_TOTAL_TOKENS} tokens")
    print(f"🔁 搜索轮次限制: 最多 {MAX_SEARCH_ROUNDS} 轮")
    print("💡 提示:")
    print("   - 联网搜索会自动触发（当询问实时信息、新闻、日期等）")
    print("   - 也可以明确要求：'搜索 xxx' 或 '帮我查一下 xxx'")
    print("   - 输入 'clear' 清除对话历史")
    print("   - 输入 'save' 保存对话")
    print("   - 输入 'history' 查看历史")
    print("   - 输入 'quit' 退出")
    print("=" * 60)

def get_system_prompt():
    return """你是 Kimi，由 Moonshot AI 提供的人工智能助手，你支持联网搜索功能。

重要信息：
- 你可以使用 $web_search 工具来搜索互联网获取实时信息
- 当用户询问实时信息（如当前日期、时间、新闻、天气等）时，你必须使用 $web_search 工具
- 当用户明确要求搜索时，你必须使用 $web_search 工具
- 你擅长中文和英文对话，回答准确、有帮助、安全

请记住：你有联网搜索能力，可以获取实时信息。对于任何需要实时数据的问题，都要使用搜索工具。"""

# ==================== 主程序 ====================

def main():
    if MOONSHOT_API_KEY == "sk-你的Kimi_API_KEY":
        print_colored("❌ 错误：请先在脚本中配置你的 Kimi API Key", "red")
        print("获取地址: https://platform.moonshot.cn")
        sys.exit(1)
    
    history = load_history()
    messages = history.copy() if history else []
    
    if not messages:
        messages.append({
            "role": "system",
            "content": get_system_prompt()
        })
        save_history(messages)
    
    show_welcome()
    
    if len(messages) > 1:
        print_colored(f"\n📂 已加载上次对话历史 ({len(messages)//2} 轮对话)", "yellow")
        print("=" * 60)
    
    while True:
        try:
            print_colored("\n你: ", "green", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            cmd = user_input.lower()
            if cmd in ['quit', 'exit', 'q']:
                print_colored("\n👋 再见！", "yellow")
                break
            elif cmd == 'clear':
                messages = [messages[0]] if messages and messages[0]["role"] == "system" else []
                save_history(messages)
                print_colored("✅ 对话历史已清除", "green")
                continue
            elif cmd == 'save':
                save_history(messages)
                print_colored(f"✅ 对话已保存到 {HISTORY_FILE}", "green")
                continue
            elif cmd == 'history':
                if len(messages) <= 1:
                    print_colored("📭 暂无对话历史", "yellow")
                else:
                    print_colored("\n📜 对话历史:", "blue")
                    print("=" * 40)
                    for i in range(1, len(messages), 2):
                        if i < len(messages):
                            user_msg = messages[i]['content']
                            print(f"👤 用户: {user_msg[:80]}{'...' if len(user_msg) > 80 else ''}")
                        if i+1 < len(messages):
                            ai_msg = messages[i+1]['content']
                            print(f"🤖 AI: {ai_msg[:80]}{'...' if len(ai_msg) > 80 else ''}")
                        print("-" * 40)
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            print_colored("\n⏳ Kimi 正在处理", "yellow", end="")
            print("...")
            
            reply, usage, error = call_kimi_with_search(messages)
            
            if reply:
                print_colored("\n🤖 Kimi: ", "blue", end="")
                print(reply)
                
                messages.append({"role": "assistant", "content": reply})
                print_usage(usage)
                save_history(messages)
                total_rounds = (len(messages) - 1) // 2
                print_colored(f"💾 对话已保存 (共 {total_rounds} 轮)", "yellow")
            elif error:
                messages.pop()
                print_colored(f"\n❌ 对话失败: {error}", "red")
                if usage and usage.get('total_tokens', 0) > 0:
                    print_colored(f"   已消耗 {usage['total_tokens']} tokens", "yellow")
            else:
                messages.pop()
                print_colored("\n❌ 对话失败，请重试", "red")
                
        except KeyboardInterrupt:
            print_colored("\n\n👋 保存对话并退出...", "yellow")
            save_history(messages)
            print_colored("✅ 再见！", "green")
            break
        except EOFError:
            break
        except Exception as e:
            print_colored(f"❌ 错误: {e}", "red")
            continue

if __name__ == "__main__":
    main()
