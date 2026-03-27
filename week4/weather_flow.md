# 天气查询程序的数据流向图

以下流程图展示了 `weather.py` 脚本运行时，数据如何在各个组件之间流动：

```mermaid
flowchart TD
    A[用户输入城市名<br>命令行参数] --> B[Python 脚本<br>weather.py]
    B --> C{参数校验}
    C -->|有效| D[构造 API 请求<br>https://wttr.in/城市?format=j1]
    C -->|无效| E[提示错误<br>并显示用法]
    D --> F[发送 HTTP GET 请求]
    F --> G[wttr.in 服务器]
    G --> H[返回 JSON 数据]
    H --> I[解析 JSON<br>提取核心字段]
    I --> J[温度、湿度、天气描述等]
    J --> K[格式化输出]
    K --> L[终端显示<br>用户看到天气信息]
    
    E --> L
