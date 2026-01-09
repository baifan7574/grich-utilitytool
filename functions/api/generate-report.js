// 针对 Cloudflare Pages Functions 架构的正式修正版
export async function onRequestPost(context) {
    const { request, env } = context;

    // 1. 跨域头配置 (确保前端网页能调动后端)
    const corsHeaders = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    };

    try {
        // 2. 核心诊断：验证密钥 (env 是从 context 中解构出来的)
        if (!env.DEEPSEEK_API_KEY) {
            return new Response(JSON.stringify({
                error: "Michael，系统仍然找不到密钥！请在 CF 后台确认变量名是否【全大写】为 DEEPSEEK_API_KEY，且已点击‘保存并部署’。"
            }), {
                status: 500,
                headers: corsHeaders
            });
        }

        // 3. 解析前端网页传来的数据
        const body = await request.json();
        const { profession, state, action, filename } = body;

        // 4. 调用 DeepSeek API (使用标准 OpenAI 兼容路径)
        const response = await fetch("https://api.deepseek.com/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${env.DEEPSEEK_API_KEY}`
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [
                    {
                        role: "system",
                        content: `你是一个严肃的合规专家。针对${profession}行业在${state}地区的${action}操作。严禁提到AI，语气必须专业、冷峻。`
                    },
                    {
                        role: "user",
                        content: `待审计文件：${filename}。请生成一份针对性的专家审计报告正文。`
                    }
                ],
                temperature: 0.3
            })
        });

        // 5. 检查 DeepSeek 响应是否正常
        if (!response.ok) {
            const errorData = await response.text();
            return new Response(JSON.stringify({ error: `DeepSeek 接口报错 (${response.status}): ${errorData}` }), {
                status: 500,
                headers: corsHeaders
            });
        }

        const data = await response.json();
        const reportText = data.choices[0].message.content;

        return new Response(JSON.stringify({ report: reportText }), {
            headers: corsHeaders
        });

    } catch (err) {
        return new Response(JSON.stringify({ error: "Michael，后端运行崩溃: " + err.message }), {
            status: 500,
            headers: corsHeaders
        });
    }
}

// 处理 OPTIONS 预检请求
export async function onRequestOptions() {
    return new Response(null, {
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    });
}
