export default {
	async fetch(request, env, ctx) {
		const url = new URL(request.url);
		const corsHeaders = {
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "GET,HEAD,POST,OPTIONS",
			"Access-Control-Allow-Headers": "Content-Type",
		};

		if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

		// --- Endpoint: Parse Statement (Synchronous - Wait and See) ---
		if (url.pathname === "/api/parse-statement" && request.method === "POST") {
			try {
				const { text } = await request.json();
				if (!text) return new Response(JSON.stringify({ detail: "No text" }), { status: 400, headers: corsHeaders });

				const prompt = `คุณคือนักบัญชีอัจฉริยะส่วนตัว (Personal Finance Expert) หน้าที่ของคุณคือวิเคราะห์ Statement และจัดทำบัญชีครัวเรือนอย่างละเอียด

1. วิเคราะห์และดึงรายการ (Transactions) ทั้งหมด:
   - จัดหมวดหมู่ที่เหมาะสมที่สุด (อาหาร, เดินทาง, ช้อปปิ้ง, บิล/ค่าใช้จ่าย, สุขภาพ, บันเทิง, อื่นๆ)
   - **Internal Transfer:** ตรวจสอบว่ารายการไหนคือการโอนเงินระหว่างบัญชีตนเอง (เช่น โอนเข้าบัญชีออมทรัพย์, จ่ายบัตรเครดิตตนเอง) ให้ระบุเป็น type: "transfer"
   - **Smart Grouping:** รวมชื่อร้านค้าที่คล้ายกันให้เป็นชื่อกลุ่มเดียวกัน (เช่น 7-Eleven สาขาต่างๆ ให้ใช้ group_name: "7-Eleven")

2. สรุปภาพรวม (Insights):
   - สรุปสั้นๆ 1-2 ประโยคว่าเดือนนี้ใช้เงินไปกับอะไรมากที่สุด และมีข้อสังเกตอะไรน่าสนใจหรือไม่

ข้อความจาก Statement:
${text}

ตอบกลับเป็น JSON เท่านั้นในรูปแบบนี้:
{
  "insights": "เดือนนี้คุณใช้เงินกับร้านสะดวกซื้อบ่อยครั้ง และมีการโอนเงินเก็บเข้าบัญชีออมทรัพย์เพิ่มขึ้น",
  "transactions": [
    {"date": "01/05", "amount": -150.0, "description": "7-11 Branch A", "group_name": "7-Eleven", "type": "expense", "tag": "อาหาร", "is_transfer": false}
  ]
}`;

				const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${env.GEMINI_API_KEY}`;
				const geminiResp = await fetch(geminiUrl, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						contents: [{ parts: [{ text: prompt }] }],
						generationConfig: { response_mime_type: "application/json" }
					})
				});

				const result = await geminiResp.json();
				if (result.error) throw new Error(result.error.message);
				if (!result.candidates || result.candidates.length === 0) throw new Error("AI ไม่ได้ส่งข้อมูลกลับมา");
				
				let rawText = result.candidates[0].content.parts[0].text;
				rawText = rawText.replace(/```json|```/g, "").trim();
				
				let transactions = [];
				let insights = "วิเคราะห์ข้อมูลเรียบร้อยแล้ว";

				try {
					const parsedData = JSON.parse(rawText);
					
					// Case 1: Standard Format { insights, transactions }
					if (parsedData.transactions && Array.isArray(parsedData.transactions)) {
						transactions = parsedData.transactions;
						insights = parsedData.insights || insights;
					} 
					// Case 2: Array only format [...]
					else if (Array.isArray(parsedData)) {
						transactions = parsedData;
					}
					// Case 3: Wrapped in another key
					else {
						for (let key in parsedData) {
							if (Array.isArray(parsedData[key])) {
								transactions = parsedData[key];
								break;
							}
						}
					}
				} catch (e) {
					throw new Error("AI ตอบกลับมาในรูปแบบที่ไม่ใช่ JSON ที่ถูกต้อง");
				}

				// Memory Cache Override
				const memoryData = await env.DB.prepare("SELECT group_name, tag FROM memory_cache").all();
				const memoryMap = Object.fromEntries(memoryData.results.map(r => [r.group_name, r.tag]));

				transactions.forEach(tx => {
					if (memoryMap[tx.group_name]) tx.tag = memoryMap[tx.group_name];
				});

				return new Response(JSON.stringify({ status: "success", transactions, insights }), { headers: corsHeaders });
			} catch (e) {
				return new Response(JSON.stringify({ detail: e.message }), { status: 500, headers: corsHeaders });
			}
		}

		// --- API: Get Latest ---
		if (url.pathname === "/api/get-latest-transactions" && request.method === "GET") {
			const userId = url.searchParams.get("userId");
			const { results } = await env.DB.prepare("SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 300").bind(userId).all();
			return new Response(JSON.stringify({ transactions: results }), { headers: corsHeaders });
		}

		// --- API: Save ---
		if (url.pathname === "/api/save-transactions" && request.method === "POST") {
			const { transactions, userId } = await request.json();
			const batch = [];
			for (const tx of transactions) {
				batch.push(env.DB.prepare("INSERT INTO transactions (date, amount, description, group_name, type, tag, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)")
					.bind(tx.date, tx.amount, tx.description, tx.group_name, tx.type, tx.tag, userId));
				batch.push(env.DB.prepare("INSERT OR REPLACE INTO memory_cache (group_name, tag) VALUES (?, ?)")
					.bind(tx.group_name, tx.tag));
			}
			await env.DB.batch(batch);
			return new Response(JSON.stringify({ status: "success" }), { headers: corsHeaders });
		}

		return new Response("IncomeandExpense API Active", { status: 200 });
	},
};
