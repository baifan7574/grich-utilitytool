const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
};

function cleanText(value, fallback) {
    return String(value || fallback || "")
        .replace(/[<>]/g, "")
        .trim()
        .slice(0, 120);
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        if (!env.DEEPSEEK_API_KEY) {
            return new Response(JSON.stringify({
                error: "DEEPSEEK_API_KEY is not configured in Cloudflare Pages."
            }), { status: 500, headers: corsHeaders });
        }

        const body = await request.json();
        const profession = cleanText(body.profession, "professional");
        const state = cleanText(body.state, "United States");
        const action = cleanText(body.action, "PDF metadata audit");
        const filename = cleanText(body.filename, "uploaded document");

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
                        content: `You generate concise professional PDF metadata risk reports.
Write in English only.
Do not claim legal certification.
Do not invent exact statutes or case law.
Use practical language for a ${profession} in ${state}.
Return 5 short sections:
1. Executive Summary
2. Potential Metadata Risks
3. Recommended Actions
4. Professional Handling Notes
5. Disclaimer`
                    },
                    {
                        role: "user",
                        content: `Filename: ${filename}. Requested action: ${action}. Generate a report body suitable for a paid downloadable PDF.`
                    }
                ],
                temperature: 0.2
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("DeepSeek API Error:", errorText);
            return new Response(JSON.stringify({
                error: `DeepSeek API Error (${response.status}). Check key, balance, or provider status.`
            }), { status: 500, headers: corsHeaders });
        }

        const data = await response.json();
        const reportText = data?.choices?.[0]?.message?.content;

        if (!reportText) {
            return new Response(JSON.stringify({
                error: "DeepSeek returned an empty report."
            }), { status: 502, headers: corsHeaders });
        }

        return new Response(JSON.stringify({ report: reportText }), {
            headers: corsHeaders
        });
    } catch (err) {
        console.error("Report generation failed:", err.message);
        return new Response(JSON.stringify({
            error: "Report generation failed: " + err.message
        }), { status: 500, headers: corsHeaders });
    }
}

export async function onRequestOptions() {
    return new Response(null, {
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    });
}
