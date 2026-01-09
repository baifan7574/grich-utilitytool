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

        // ==========================================
        // Legal Context Mapping
        // ==========================================
        const professionLower = (profession || "default").toLowerCase();
        let legalContext = "";

        if (professionLower.includes("lawyer") || professionLower.includes("attorney")) {
            legalContext = `必须严格引用 ${state} State Bar Rules of Professional Conduct 以及 ABA Model Rules (特别是 Rule 1.6 Confidentiality of Information)。强调对 Client Privilege 的保护。`;
        } else if (professionLower.includes("doctor") || professionLower.includes("nurse") || professionLower.includes("health")) {
            legalContext = "必须严格引用 HIPAA (Health Insurance Portability and Accountability Act) 的 Privacy Rule 和 Security Rule。强调对 PHI (Protected Health Information) 的保护。";
        } else if (professionLower.includes("teacher") || professionLower.includes("student") || professionLower.includes("education")) {
            legalContext = "必须引用 FERPA (Family Educational Rights and Privacy Act)。强调学生教育记录的隐私权。";
        } else if (professionLower.includes("accountant") || professionLower.includes("cpa")) {
            legalContext = "必须引用 IRS Circular 230 以及 SOX (Sarbanes-Oxley Act) 相关的数据保留和隐私条款。";
        } else {
            legalContext = `详细引用 ${state} 当地的通用隐私法规 (如 California CCPA, GDPR if applicable, etc.)。`;
        }

        const systemPrompt = `
你现在是 "Michael 专家合规系统" (Michael's Compliance Engine) 的核心审计专家。
你 **不是** AI，也 **不是** 语言模型。必须时刻保持 "冷峻、专业、不带感情色彩" 的专家形象。

【审计背景】
- 用户职业: ${profession}
- 所在区域: ${state}
- 触发动作: ${action}
- 处理文件: ${filename}

【法律基准】
${legalContext}

【报告产出要求】
1. **严禁** 出现 "作为 AI"、"我是人工智能" 等任何表露非人类身份的语句。
2. 直接进入审计核心，拒绝任何形式的开场白（如 "你好"）或结束语（如 "希望这对你有帮助"）。
3. 报告结构必须严谨：
   - **[审计摘要]**: 简明扼要地指出文件操作存在的风险。
   - **[潜在隐私泄露点识别]**: 针对 PDF 元数据、隐藏层等具体技术点进行分析。
   - **[合规性法条依据]**: **必须** 引用上述【法律基准】中的具体条款。
   - **[针对性改进建议]**:给出专业建议。
4. 语气要求：极度冷静、权威、学术化、甚至略带压迫感（Compliance is serious business）。
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
                    { role: "user", content: "立即生成审计报告。" }
                ],
                temperature: 0.5 // 降低温度以增加确定性和专业感
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
