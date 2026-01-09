// Cloudflare Pages Functions - 诊断增强版
export async function onRequestPost(context) {
    const { request, env } = context;

    const corsHeaders = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    };

    try {
        // --- 诊断 1: 检查密钥 ---
        if (!env.DEEPSEEK_API_KEY) {
            console.error("Michael Error: DEEPSEEK_API_KEY is missing in env");
            return new Response(JSON.stringify({
                error: "诊断结果：CF 后台没配置好密钥！请检查变量名是否完全匹配 DEEPSEEK_API_KEY (全大写)。"
            }), { status: 500, headers: corsHeaders });
        }

        // --- 诊断 2: 解析数据 ---
        const body = await request.json();
        const { profession, state, action, filename } = body;
        console.log(`Michael Audit: Processing ${profession} in ${state}`);

        // --- 诊断 3: 调用 DeepSeek ---
        // 使用 OpenAI 官方库兼容的端点，提高稳定性
        const response = await fetch("https://api.deepseek.com/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${env.DEEPSEEK_API_KEY.trim()}`
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [
                    {
                        role: "system",
                        content: `你是一个极其专业的合规专家系统。
任务：针对 ${profession} 行业在 ${state} 地区的 ${action} 操作生成审计报告。
规则：引用 ${state} 法律，严禁提到 AI，语气冷峻。`
                    },
                    {
                        role: "user",
                        content: `文档：${filename}。请生成报告。`
                    }
                ],
                temperature: 0.1 // 降低随机性，确保专业度
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("DeepSeek API Error:", errorText);
            return new Response(JSON.stringify({
                error: `诊断结果：DeepSeek 接口报错 (${response.status})。可能是余额不足或密钥被封。`
            }), { status: 500, headers: corsHeaders });
        }

        const data = await response.json();
        const reportText = data.choices[0].message.content;

        return new Response(JSON.stringify({ report: reportText }), {
            headers: corsHeaders
        });

    } catch (err) {
        console.error("Michael System Crash:", err.message);
        return new Response(JSON.stringify({
            error: "诊断结果：后端代码崩溃。请联系 Michael 检查 functions 文件夹结构。" + err.message
        }), { status: 500, headers: corsHeaders });
    }
}

// 必须保留，解决前端拦截问题
export async function onRequestOptions() {
    return new Response(null, {
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    });
}
