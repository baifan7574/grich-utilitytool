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

function fallbackReport(profession, state, action, filename, reason) {
    return `Executive Summary
This report was generated for ${filename} for a ${profession} in ${state}. The requested action was ${action}. The live analysis service could not complete the provider call, so this fallback report records the core handling guidance and the service reason: ${reason}.

Potential Metadata Risks
PDF files may contain author names, editing software, timestamps, hidden comments, revision history, embedded file paths, device identifiers, and other metadata that is not obvious when viewing the document normally.

Recommended Actions
Use the local processing tools to remove document title, author, subject, creator, and producer fields where possible. Download the processed file and review it manually before sending, filing, or storing it.

Professional Handling Notes
Do not treat this report as a legal, medical, tax, or regulatory certification. Use it as a practical risk checklist before sharing sensitive PDFs.

Disclaimer
This report is informational only. Final responsibility for professional filing, privacy review, and compliance remains with the user.`;
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        if (!env.DEEPSEEK_API_KEY) {
            const body = await request.json().catch(() => ({}));
            const profession = cleanText(body.profession, "professional");
            const state = cleanText(body.state, "United States");
            const action = cleanText(body.action, "PDF metadata audit");
            const filename = cleanText(body.filename, "uploaded document");
            return new Response(JSON.stringify({
                report: fallbackReport(profession, state, action, filename, "DEEPSEEK_API_KEY is not configured."),
                fallback: true
            }), { headers: corsHeaders });
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
                report: fallbackReport(profession, state, action, filename, `DeepSeek API Error (${response.status}). Check key, balance, or provider status.`),
                fallback: true
            }), { headers: corsHeaders });
        }

        const data = await response.json();
        const reportText = data?.choices?.[0]?.message?.content;

        if (!reportText) {
            return new Response(JSON.stringify({
                report: fallbackReport(profession, state, action, filename, "DeepSeek returned an empty report."),
                fallback: true
            }), { headers: corsHeaders });
        }

        return new Response(JSON.stringify({ report: reportText }), {
            headers: corsHeaders
        });
    } catch (err) {
        console.error("Report generation failed:", err.message);
        return new Response(JSON.stringify({
            report: fallbackReport("professional", "United States", "PDF metadata audit", "uploaded document", err.message),
            fallback: true
        }), { headers: corsHeaders });
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
