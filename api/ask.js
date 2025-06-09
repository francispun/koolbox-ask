// api/ask.js
const { GenerativeLanguageClient } = require("@google-ai/generativelanguage");
const fs   = require("fs");
const path = require("path");

// load deck once
const cards = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../cards.json"), "utf8")
);

// init Gemini client
const client = new GenerativeLanguageClient({
  apiKey: process.env.GEMINI_API_KEY
});

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end("Method Not Allowed");
  }

  // parse JSON body
  let body = "";
  req.on("data", (chunk) => body += chunk);
  await new Promise((r) => req.on("end", r));
  let data;
  try {
    data = JSON.parse(body);
  } catch {
    return res.status(400).json({ error: "Invalid JSON" });
  }

  const userQ = (data.question||"").trim();
  if (!userQ) return res.status(400).json({ error: "Empty question" });

  // pick a random card
  const keys = Object.keys(cards);
  const card = cards[ keys[Math.floor(Math.random()*keys.length)] ];

  // build the text prompt
  const prompt = `
${card.title}
${card.content}

Provide a brief takeaway (1-2 sentences) summarizing the card’s theme, followed by "Answer to question:" and an answer to the question based on the card. Keep both concise, strip all markup. If the user asks in Chinese, reply in zh-hk. If the card is not directly related, still make up an insight that suits.

Takeaway:
Answer to question: ${userQ}
`.trim();

  try {
    // call Gemini text
    const [textResp] = await client.generateText({
      model: "gemini-2.5-flash-preview-05-20",
      prompt
    });
    const raw = textResp.text || "";
    let takeaway, answer;
    if (raw.includes("Answer to question:")) {
      [takeaway, answer] = raw
        .split("Answer to question:")
        .map(s => s.replace(/^Takeaway:/, "").trim());
    } else {
      takeaway = raw.trim();
      answer   = raw.trim();
    }

    // call Gemini image
    const imgPrompt = `Create a visual representation of: ${answer}`;
    const [imgResp] = await client.generateImage({
      model: "gemini-2.0-flash-preview-image-generation",
      prompt: imgPrompt
    });
    const image = imgResp?.image?.imageBytes || null; // base64

    return res.json({ card, takeaway, answer, image });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
};
