// server.js
import express from "express";
import cors from "cors";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import fs from "fs";
import dotenv from "dotenv";
import { GenerativeLanguageClient } from "@google-ai/generativelanguage";

dotenv.config();
const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error("🚨 GEMINI_API_KEY not set in .env");
  process.exit(1);
}

// --- load deck via proper __dirname in ESM ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const cards = JSON.parse(
  fs.readFileSync(join(__dirname, "cards.json"), "utf8")
);

// --- init Gemini client ---
const client = new GenerativeLanguageClient({ apiKey: API_KEY });

const app = express();
app.use(cors());
app.use(express.json());
// serve all files in public/ at /
app.use(express.static(join(__dirname, "public")));

app.post("/ask", async (req, res) => {
  try {
    const userQ = (req.body.question || "").trim();
    if (!userQ) return res.status(400).json({ error: "Empty question" });

    // pick a random card
    const keys = Object.keys(cards);
    const cardKey = keys[Math.floor(Math.random() * keys.length)];
    const card = cards[cardKey];

    // build the prompt
    const prompt = `
${card.title}
${card.content}

Provide a brief takeaway (1-2 sentences) summarizing the card’s theme, 
followed by "Answer to question:" and an answer to the question based on the card. 
Keep both concise, strip all markup. If the user asks in Chinese, reply in zh-hk. 
If the card is not directly related, still make up an insight that suits.

Takeaway:
Answer to question: ${userQ}
`.trim();

    // call Gemini text
    const [textResp] = await client.generateText({
      model: "gemini-2.5-flash-preview-05-20",
      prompt,
    });
    const raw = textResp.text || "";
    let takeaway, answer;
    if (raw.includes("Answer to question:")) {
      [takeaway, answer] = raw
        .split("Answer to question:")
        .map((s) => s.replace(/^Takeaway:/, "").trim());
    } else {
      takeaway = raw.trim();
      answer = raw.trim();
    }

    // call Gemini image
    const imgPrompt = `Create a visual representation of: ${answer}`;
    const [imgResp] = await client.generateImage({
      model: "gemini-2.0-flash-preview-image-generation",
      prompt: imgPrompt,
    });
    const image = imgResp?.image?.imageBytes || null; // base64

    res.json({ card, takeaway, answer, image });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log(`🚀 Server running at http://localhost:${PORT}`)
);
