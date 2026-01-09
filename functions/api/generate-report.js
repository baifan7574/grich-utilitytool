export async function onRequestPost(context) {
    try {
        // strict environment variable access
        const env = context.env;
        const { request } = context;
        const body = await request.json();
        const { profession, state, action, filename } = body;

        const DEEPSEEK_API_KEY = env.DEEPSEEK_API_KEY;

        if (!DEEPSEEK_API_KEY) {
            return new Response(JSON.stringify({ error: "Configuration Error: DEEPSEEK_API_KEY is missing in Cloudflare settings." }), { status: 500 });
        }

        const systemPrompt = `
你现在是 Michael's Compliance Engine 的核心审计专家。

【审计背景】
- 用户职业: ${profession}
- 所在区域: ${state}
- 触发动作: ${action}
- 处理文件: ${filename}

【报告产出要求】
1. 保持高度专业性，直接进入审计核心，拒绝任何形式的客套话。
2. 必须引用至少 2 条真实的行业合规标准或法律条文：
   - 法律行业 (Lawyer)：必须引用该州律师执业守则。
   - 医疗行业 (Healthcare)：必须引用 HIPAA 特定隐私条款。
3. 报告结构必须严谨：[审计摘要]、[潜在隐私泄露点识别]、[合规性法条依据]、[针对性改进建议]。
4. 语气要求：冷静、权威、学术化。
5. 底部版权标注：'Report validated by Michael's Compliance Model v1.0'。
`;

        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: "请根据上述背景生成一份完整的合规审计报告。" }
                ],
                temperature: 0.7
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            return new Response(JSON.stringify({
                error: `DeepSeek API Error (${response.status}): ${errorText}`
            }), { status: response.status });
        }

        const data = await response.json();
        const reportContent = data.choices[0].message.content;

        return new Response(JSON.stringify({ report: reportContent }), {
            headers: { "Content-Type": "application/json" },
        });

    } catch (err) {
        return new Response(JSON.stringify({ error: `Backend Exception: ${err.message}` }), { status: 500 });
    }
}
