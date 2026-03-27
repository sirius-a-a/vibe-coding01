#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行天气查询工具（增强版）
用法: python weather.py <城市名>
示例: python weather.py beijing
"""

import requests
import sys
import json
from datetime import datetime

def get_weather(city):
    """获取指定城市的天气信息"""
    
    # 使用 wttr.in 的 API
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None
        
        data = response.json()
        
        # ========== 提取当前天气信息 ==========
        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]
        
        # 日期时间（wttr.in 返回的是本地时间）
        obs_time = current.get("localObsDateTime", "")
        if obs_time:
            # 格式: 2026-03-27 03:00 PM
            obs_date = obs_time.split()[0] if obs_time else "N/A"
            obs_time_clean = " ".join(obs_time.split()[1:]) if obs_time else "N/A"
        else:
            obs_date = "N/A"
            obs_time_clean = "N/A"
        
        # 天气描述（中英文取决于城市，但都会显示）
        weather_desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
        
        # 天气图标映射（纯视觉美化）
        weather_icons = {
            "Sunny": "☀️", "Clear": "☀️", "Partly cloudy": "⛅", "Cloudy": "☁️",
            "Overcast": "☁️", "Mist": "🌫️", "Fog": "🌫️", "Light rain": "🌦️",
            "Moderate rain": "🌧️", "Heavy rain": "🌧️", "Thunderstorm": "⛈️",
            "Snow": "❄️", "Light snow": "❄️"
        }
        weather_icon = weather_icons.get(weather_desc.split(",")[0], "🌡️")
        
        # 温度
        temp_c = current.get("temp_C", "N/A")
        feels_like = current.get("FeelsLikeC", "N/A")
        
        # 湿度、风速、气压
        humidity = current.get("humidity", "N/A")
        wind_speed = current.get("windspeedKmph", "N/A")
        pressure = current.get("pressure", "N/A")
        
        # 额外信息
        uv_index = current.get("uvIndex", "N/A")
        visibility = current.get("visibility", "N/A")
        chance_of_rain = current.get("chanceofrain", "N/A")
        
        # 城市和国家
        city_name = area.get("areaName", [{}])[0].get("value", city)
        country = area.get("country", [{}])[0].get("value", "")
        
        # ========== 输出（只打印核心信息，过滤掉 JSON） ==========
        print("\n" + "=" * 45)
        print(f"🌍 {city_name}, {country}")
        print(f"📅 {obs_date}  {obs_time_clean}")
        print("=" * 45)
        print(f"{weather_icon} 天气: {weather_desc}")
        print(f"🌡️  温度: {temp_c}°C  (体感 {feels_like}°C)")
        print(f"💧 湿度: {humidity}%")
        print(f"💨 风速: {wind_speed} km/h")
        print(f"🔘 气压: {pressure} mb")
        print(f"☔ 降雨概率: {chance_of_rain}%")
        print(f"🕶️ 紫外线指数: {uv_index}")
        print(f"👀 能见度: {visibility} km")
        print("=" * 45)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return None
    except json.JSONDecodeError:
        print(f"❌ 数据解析错误，请检查城市名: {city}")
        return None

def main():
    if len(sys.argv) < 2:
        print("❌ 请提供城市名")
        print("用法: python weather.py <城市名>")
        print("示例: python weather.py beijing")
        sys.exit(1)
    
    city = " ".join(sys.argv[1:])
    print(f"🔍 正在查询 {city} 的天气...")
    get_weather(city)

if __name__ == "__main__":
    main()