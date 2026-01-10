export async function onRequestPost(context) {
    try {
        const { request } = context;
        const body = await request.json();
        const { email } = body;

        // --- 临时模拟测试 (SIMULATION MODE) ---
        // 允许 test@test.com 直接通过验证，用于测试流程
        if (email.toLowerCase() === 'test@test.com') {
            return new Response(JSON.stringify({
                success: true,
                message: "Simulation Verified",
                transaction_id: "sim_mode_123"
            }), { headers: { "Content-Type": "application/json" } });
        }
        // ------------------------------------

        // 1. Validate Input
        if (!email) {
            return new Response(JSON.stringify({ error: "Email is required" }), {
                headers: { "Content-Type": "application/json" }, status: 400
            });
        }

        // 2. Call Payhip API
        // User API Key: 072b74a33fa1f6a16ed37875b816732ac0ef99be
        const PAYHIP_API_KEY = "072b74a33fa1f6a16ed37875b816732ac0ef99be";

        // Note: Payhip typically lists sales. We will fetch recent sales and filter, 
        // or hopefully searching by email works if their API supports filtering (documentation varies, assuming listing first).
        // Standard endpoint: https://payhip.com/api/v1/sales

        const payhipRes = await fetch("https://payhip.com/api/v1/sales?limit=100", {
            headers: {
                "x-api-key": PAYHIP_API_KEY
            }
        });

        if (!payhipRes.ok) {
            throw new Error(`Payhip API Failed: ${payhipRes.status}`);
        }

        const data = await payhipRes.json();
        const sales = data.sales || []; // Assuming standard structure

        // 3. Match Email (Case Insensitive)
        // Check for ANY specific paid transaction from this email.
        const match = sales.find(s =>
            s.email && s.email.toLowerCase().trim() === email.toLowerCase().trim() &&
            (s.status === "paid" || s.status === "completed") // Ensure valid status
        );

        if (match) {
            return new Response(JSON.stringify({
                success: true,
                message: "Verified",
                transaction_id: match.transaction_id
            }), {
                headers: { "Content-Type": "application/json" }
            });
        } else {
            return new Response(JSON.stringify({
                success: false,
                error: "No paid transaction found for this email."
            }), {
                headers: { "Content-Type": "application/json" }, status: 404
            });
        }

    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
            headers: { "Content-Type": "application/json" }, status: 500
        });
    }
}
