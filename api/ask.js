// api/ask.js
const fs   = require("fs");
const path = require("path");

const cards = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../cards.json"), "utf-8")
);
const API_KEY     = process.env.GEMINI_API_KEY;
const TEXT_MODEL  = "gemini-2.5-flash-preview-05-20";
const IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation";

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end("Method Not Allowed");
  }

  // —— parse JSON body ——
  let body = "";
  for await (const chunk of req) body += chunk;
  let data;
  try { data = JSON.parse(body); }
  catch { return res.status(400).json({ error: "Invalid JSON" }); }

  const userQ = (data.question || "").trim();
  if (!userQ) return res.status(400).json({ error: "Empty question" });

  // —— pick a random card ——
  const keys = Object.keys(cards);
  const card = cards[keys[Math.floor(Math.random() * keys.length)]];

  // —— build the prompt ——
  const prompt = `
${card.title}
${card.content}

Provide a brief takeaway (1-2 sentences) summarizing the card’s theme, followed by "Answer to question:" and an answer to the question based on the card. Keep both concise, strip all markup. If the user asks in Chinese, reply in zh-hk. If the card is not directly related, still make up an insight that suits.

Takeaway:
Answer to question: ${userQ}
`.trim();

  try {
    // —— call Gemini text endpoint ——
    const textResp = await fetch(
      `https://generativelanguage.googleapis.com/v1beta2/models/${TEXT_MODEL}:generateText?key=${API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: { text: prompt } }),
      }
    );
    const textJson = await textResp.json();
    const raw = textJson.candidates?.[0]?.output || "";

    let takeaway, answer;
    if (raw.includes("Answer to question:")) {
      [takeaway, answer] = raw
        .split("Answer to question:")
        .map((s) => s.replace(/^Takeaway:/, "").trim());
    } else {
      takeaway = raw.trim();
      answer = raw.trim();
    }

    // —— call Gemini image endpoint ——
    const imgResp = await fetch(
      `https://generativelanguage.googleapis.com/v1beta2/models/${IMAGE_MODEL}:generateImage?key=${API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: { text: answer } }),
      }
    );
    const imgJson = await imgResp.json();
    const image = imgJson.candidates?.[0]?.image?.imageBytes || null; // base64

    return res.status(200).json({ card, takeaway, answer, image });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e.message });
  }
};
