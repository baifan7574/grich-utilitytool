const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
};

export async function onRequestPost(context) {
    try {
        const { request, env } = context;
        const body = await request.json();
        const { email } = body;

        if (!email) {
            return new Response(JSON.stringify({ error: "Email is required" }), {
                headers: corsHeaders,
                status: 400
            });
        }

        if (!env.PAYHIP_API_KEY) {
            return new Response(JSON.stringify({ error: "PAYHIP_API_KEY is not configured." }), {
                headers: corsHeaders,
                status: 500
            });
        }

        const payhipRes = await fetch("https://payhip.com/api/v1/sales?limit=100", {
            headers: {
                "x-api-key": env.PAYHIP_API_KEY.trim()
            }
        });

        if (!payhipRes.ok) {
            throw new Error(`Payhip API Failed: ${payhipRes.status}`);
        }

        const data = await payhipRes.json();
        const sales = data.sales || [];

        const match = sales.find(s =>
            s.email &&
            s.email.toLowerCase().trim() === email.toLowerCase().trim() &&
            (s.status === "paid" || s.status === "completed")
        );

        if (!match) {
            return new Response(JSON.stringify({
                success: false,
                error: "No paid transaction found for this email."
            }), {
                headers: corsHeaders,
                status: 404
            });
        }

        return new Response(JSON.stringify({
            success: true,
            message: "Verified",
            transaction_id: match.transaction_id
        }), {
            headers: corsHeaders
        });
    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
            headers: corsHeaders,
            status: 500
        });
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
