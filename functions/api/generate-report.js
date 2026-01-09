// Michael V3.7 - Cloudflare Pages Functions
// Core Logic: Diagnostic Enhanced + Force English Output

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
        // 使用 OpenAI 官方库兼容的端点
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
                        content: `You are Michael, a strict, cold, and professional expert compliance system.
Your Task: Audit the logic of the user's request for ${profession} in ${state} doing ${action}.
Rules:
1. STRICTLY OUTPUT IN ENGLISH ONLY. NO CHINESE CHARACTERS ALLOWED to avoid PDF rendering issues.
2. Maintain a professional, detached tone.
3. Cite relevant ${state} laws or federal regulations (e.g., ABA, HIPAA, SOX, FERPA).
4. Do not mention "AI" or "LLM". You are an expert algorithm.`
                    },
                    {
                        role: "user",
                        content: `Document: ${filename}. Please generate the audit report body.`
                    }
                ],
                temperature: 0.1 // 降低随机性
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("DeepSeek API Error:", errorText);
            return new Response(JSON.stringify({
                error: `Diag Alert: DeepSeek API Error (${response.status}). Check Balance or Keys.`
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
            error: "System Crash: " + err.message
        }), { status: 500, headers: corsHeaders });
    }
}

// OPTIONS Handler
export async function onRequestOptions() {
    return new Response(null, {
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    });
}
