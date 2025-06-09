// server.js
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";
// Google GenAI node client
import { GenerativeLanguageClient } from "@google-ai/generativelanguage";

dotenv.config();
const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error("🚨 GEMINI_API_KEY not set in .env");
  process.exit(1);
}

const client = new GenerativeLanguageClient({
  apiKey: API_KEY,
  // override the default endpoint if needed:
  // apiEndpoint: "https://generativelanguage.googleapis.com",
});

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static("public"));

// ─── The 52‐card deck ─────────────────────────────────────────────────────────
const cards = JSON.parse(
  fs.readFileSync(path.join(__dirname, "cards.json"), "utf8")
);

// ─── POST /ask ────────────────────────────────────────────────────────────────
app.post("/ask", async (req, res) => {
  try {
    const userQ = (req.body.question || "").trim();
    if (!userQ) return res.status(400).json({ error: "Empty question" });

    // 1) pick a random card
    const keys = Object.keys(cards);
    const cardKey = keys[Math.floor(Math.random() * keys.length)];
    const card = cards[cardKey];

    // 2) build prompt
    const prompt = `
${card.title}
${card.content}

Provide a brief takeaway (1-2 sentences) summarizing the card’s theme, followed by "Answer to question:" and an answer to the question based on the card. Keep both concise and strip all markup styling.
If the user asks in Chinese, reply in zh-hk. If the card is not directly related, please still make up an insight that suits.

Takeaway:
Answer to question: ${userQ}
`;

    // 3) call Gemini text model
    const [textResp] = await client.generateText({
      model: "gemini-2.5-flash-preview-05-20",
      prompt,
    });
    let raw = textResp.text || "";
    let takeaway = "";
    let answer = "";
    if (raw.includes("Answer to question:")) {
      [takeaway, answer] = raw
        .split("Answer to question:")
        .map((s) => s.replace(/^Takeaway:/, "").trim());
    } else {
      takeaway = "（无法解析模型输出）";
      answer = raw.trim();
    }

    // 4) call Gemini image model
    const imagePrompt = `Create a visual representation of the following concept: ${answer}`;
    const [imgResp] = await client.generateImage({
      model: "gemini-2.0-flash-preview-image-generation",
      prompt: imagePrompt,
    });
    // The node client may return base64 directly as `imgResp.image`:
    const image = imgResp?.image?.imageBytes || null;

    // 5) return JSON
    res.json({ card, takeaway, answer, image });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

// ─── Start server ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server listening on http://localhost:${PORT}`);
});
