
export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405, headers: cors });

    try {
      const form = await request.formData();
      const img = form.get('image');
      const uid = form.get('uid');
      const name = form.get('name');

      if (!img || !uid) throw new Error("Missing data");

      // 1. ส่งรูปให้ AI อ่าน Text
      const aiRes = await env.AI.run('@cf/meta/llama-3.2-11b-vision-instruct', {
          image: [...new Uint8Array(await img.arrayBuffer())],
          prompt: "Extract date, time, and location text from this image. Return only the text.",
          max_tokens: 150
      });
      const text = aiRes.response || "No text found";

      // 2. บันทึกลง D1
      await env.DB.prepare("INSERT INTO attendance_logs (line_uid, line_name, extracted_text) VALUES (?, ?, ?)")
        .bind(uid, name, text).run();

      return new Response(JSON.stringify({ status: "success", text }), { headers: { ...cors, "Content-Type": "application/json" } });

    } catch (e) {
      return new Response(JSON.stringify({ status: "error", message: e.message }), { status: 500, headers: { ...cors, "Content-Type": "application/json" } });
    }
  }
};
