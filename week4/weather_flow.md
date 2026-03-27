# DeepSeek API 调用程序的数据流向图

以下流程图展示了 `api_fetch.py` 脚本运行时，数据如何在各个组件之间流动。

## 一、整体数据流向图

```mermaid
flowchart TD
    subgraph 用户交互层
        A[用户启动脚本] --> B[显示欢迎界面]
        B --> C[等待用户输入]
        C --> D{用户输入什么？}
    end

    subgraph 命令处理
        D -->|输入问题| E[添加到 messages 列表]
        D -->|输入 'clear'| F[清空对话历史]
        D -->|输入 'save'| G[保存历史到文件]
        D -->|输入 'history'| H[显示对话摘要]
        D -->|输入 'quit'| I[退出程序]
    end

    subgraph API 调用层
        E --> J[显示"正在思考..."]
        J --> K{选择调用模式}
        K -->|流式模式| L[call_deepseek_stream]
        K -->|非流式模式| M[call_deepseek_normal]
        L --> N[构造请求头<br>Authorization + Content-Type]
        M --> N
        N --> O[构造请求体<br>model + messages + stream]
        O --> P[发送 POST 请求<br>到 api.deepseek.com]
    end

    subgraph DeepSeek 云端
        P --> Q[DeepSeek 服务器]
        Q --> R{stream 参数}
        R -->|true| S[SSE 流式响应<br>逐块返回数据]
        R -->|false| T[一次性返回完整 JSON]
    end

    subgraph 响应处理
        S --> U[逐块接收并实时打印]
        T --> V[接收完整 JSON]
        U --> W[拼接完整回答]
        V --> W
        W --> X[提取 choices[0].message.content]
        X --> Y[计算 token 使用量]
        Y --> Z[将 AI 回答添加到 messages]
        Z --> AA[自动保存历史到文件]
        AA --> AB[显示 token 统计]
        AB --> C
    end

    subgraph 错误处理
        P -->|网络超时| AC[捕获异常]
        AC --> AD[显示错误信息]
        AD --> C
        Q -->|非 200 状态码| AE[返回错误响应]
        AE --> AC
    end

    F --> C
    G --> C
    H --> C
    I --> AF[保存历史后退出]