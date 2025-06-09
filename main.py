import os
import random
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# ─── Load API Key ───────────────────────────────────────────────────────────────
load_dotenv()  # for local dev (.env)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("🚨 GEMINI_API_KEY not set! Check .env or Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ─── Your 52-card dict ────────────────────────────────────────────────────────────
cards = {
  "1": {
    "title": "First Step",
    "content": "Every journey begins with a single step. Lace up your boots and take that first leap toward growth. Whether it’s a new project or personal goal, progress starts now. Embrace the adventure and plant the seeds of success!"
  },
  "2": {
    "title": "Be Water",
    "content": "Flexibility is the ultimate strength. Inspired by Bruce Lee’s wisdom, the idea is to adapt like water—shaping yourself to challenges. Flow through obstacles, nourish your creativity, and let resilience carry you forward."
  },
  "3": {
    "title": "NOW",
    "content": "The past is gone, and the future is unknown. Embrace the present moment and measure where you are now. Your power lies in the here and now—seize the day!"
  },
  "4": {
    "title": "Five Constant Virtues",
    "content": "Align your life with wisdom, integrity, and compassion. Much like tending to a garden, personal growth requires care and nurturing. Cultivate these virtues daily and watch your life bloom with purpose and harmony."
  },
  "5": {
    "title": "Ying Yang",
    "content": "Balance lies in embracing opposites. The ebb and flow, the light and dark—all are essential parts of life’s journey. Harness the power of balance to move forward and thrive in every aspect of your life."
  },
  "6": {
    "title": "Sharpen the Saw",
    "content": "A dull tool leads nowhere. Invest in sharpening your skills and strengthening your mind. With consistent effort, cut through challenges and achieve more than ever before. Stay sharp and ready!"
  },
  "7": {
    "title": "PEACE Method",
    "content": "Climb life’s ladder one step at a time. Avoid shortcuts or stepping on others along the way. Build peace in your relationships and goals by balancing patience with determination."
  },
  "8": {
    "title": "Enneagram",
    "content": "Dig deep into your personality and motivations. Rake through the leaves of your mind to uncover hidden truths. Self-awareness is the key to unlocking your full potential and living authentically."
  },
  "9": {
    "title": "Ten Factors of Life",
    "content": "Unlock life’s mysteries by gaining wisdom. Gain clarity and direction as you uncover what truly matters. A life guided by understanding and purpose is one of fulfillment and growth."
  },
  "10": {
    "title": "21-Day Glasses",
    "content": "Seeing clearly sometimes means facing the truth, even when it’s uncomfortable. Shift your perspective and embrace the clarity that comes with honest self-reflection. Growth begins with an honest view of yourself."
  },
  "11": {
    "title": "Fightless Win",
    "content": "Victory doesn’t always mean conflict. By staying calm, composed, and confident, success becomes attainable without unnecessary battles. Let others panic while you maintain focus and achieve your goals with grace."
  },
  "12": {
    "title": "Growth Mindset",
    "content": "Getting your hands dirty is the first step to success. Challenges are opportunities to grow, and every failure becomes a lesson. With a growth mindset, you’ll turn obstacles into stepping stones for greatness."
  },
  "13": {
    "title": "Learn Earn Return",
    "content": "Plant seeds of wisdom and reap the rewards of good karma. Invest in yourself, grow your knowledge, and give back to others. True success is measured by the positive impact you leave behind."
  },
  "14": {
    "title": "Habit Contract",
    "content": "Smooth out the rough edges of your daily routines. Transform unproductive habits into polished, productive behaviors through commitment and focus. Consistency is the key to turning small changes into big results."
  },
  "15": {
    "title": "Do the Hard Things First",
    "content": "Tackle the tough tasks first, just like using the strongest tool in a Swiss knife. Facing challenges head-on makes the rest of the day feel lighter. Start strong and finish stronger!"
  },
  "16": {
    "title": "➕➖✖️➗",
    "content": "Find the perfect fit for every problem. Like a wrench tightening loose bolts, precision and the right strategies ensure success. Adjust, refine, and make everything fit perfectly."
  },
  "17": {
    "title": "5W1H",
    "content": "Get a firm grip on success by asking the right questions. Like a clamp holding everything securely in place, Who, What, When, Where, Why, and How strengthen your understanding and keep your plans steady and on track."
  },
  "18": {
    "title": "6 Persuasive Leadership",
    "content": "Leadership isn’t one-size-fits-all. With six approaches to persuasion, explore how to adapt and inspire effectively. Use the right tools for each situation to motivate your team and drive results."
  },
  "19": {
    "title": "7 Drucker Principles",
    "content": "Manage with precision and lead with purpose. The principles of Peter Drucker guide you to tighten your approach to management and unlock the full potential of your team."
  },
  "20": {
    "title": "80/20",
    "content": "Focus on the vital 20% that drives 80% of results. Prioritize what matters most and find balance in a world of distractions. Alignment with key priorities leads to transformative progress."
  },
  "21": {
    "title": "SWOT",
    "content": "Apply pressure where it matters most to make an impact. Identifying strengths, weaknesses, opportunities, and threats helps carve out a path to success with precision and confidence."
  },
  "22": {
    "title": "Weekly Goal",
    "content": "Planning is the foundation of progress. Setting achievable weekly goals ensures consistency and alignment with long-term visions. Like measuring twice to cut once, small steps lead to big wins."
  },
  "23": {
    "title": "Due Diligence Checklist",
    "content": "Preparation prevents mistakes. Double-check details and ensure you’re hitting the mark with precision. A solid foundation leads to stronger results and fewer missteps along the way."
  },
  "24": {
    "title": "SWIFT Conversation",
    "content": "Effective communication sharpens relationships. Delivering the right message at the right time ensures clarity and impact. One well-placed idea can inspire and energize your audience."
  },
  "25": {
    "title": "4Q Leadership",
    "content": "Shine a light for others to follow. Leading with clarity and purpose ensures that your team moves forward with confidence. Illuminate the path without overwhelming or blinding yourself or others."
  },
  "26": {
    "title": "OKR",
    "content": "Clear objectives lead to impactful results. Setting focused goals aligns efforts and prevents chaos. Precision and purpose ensure that every step contributes to meaningful outcomes."
  },
  "27": {
    "title": "Never Stop Creating",
    "content": "Creativity has no limits. A sponge absorbs inspiration from everywhere, reminding you to keep creating and finding joy in the process. It’s not about competition but about letting your imagination flow freely."
  },
  "28": {
    "title": "Life Experience Map",
    "content": "Every journey in life holds value. Chopsticks carefully pick up lessons from the past, helping you savor moments that shape who you are. Use these experiences to build a meaningful and enriched future."
  },
  "29": {
    "title": "We Rhyme We Kool",
    "content": "Laughter is the secret ingredient to healing. A cooking pot blends diverse flavors, just as humor and joy bring people together. Create connections that nourish the soul and brighten your day."
  },
  "30": {
    "title": "Vocab of the Day",
    "content": "Expanding your vocabulary sharpens communication. A cheese grater refines ingredients, just as enriching your lexicon refines how you express yourself. Words have power—choose them wisely and creatively."
  },
  "31": {
    "title": "Koolers Story",
    "content": "Every voice matters, and every story deserves to be shared. An apron protects the storyteller, symbolizing the value of celebrating unique experiences. Together, these voices weave a rich and inspiring tapestry."
  },
  "32": {
    "title": "Weekly Kool News",
    "content": "Collaboration fuels co-creation. A cutting board prepares ingredients for something extraordinary, just as sharing updates and ideas builds something greater, week by week."
  },
  "33": {
    "title": "Book Club",
    "content": "Knowledge and growth are everywhere. A notebook and pen symbolize the value of capturing wisdom, diving into books, and fueling curiosity. Learning unlocks new perspectives and infinite possibilities."
  },
  "34": {
    "title": "Advisory Board",
    "content": "Guidance leads to wisdom. A kitchen scale ensures balance, much like the wisdom of mentors and advisors helps weigh options and make informed decisions. Good advice is a recipe for success."
  },
  "35": {
    "title": "5 Kool Tenets",
    "content": "Life is measured by your values. A set of measuring cups helps find the perfect mix, reminding you to prioritize what matters and create a purposeful, fulfilling life."
  },
  "36": {
    "title": "Purpose Statement",
    "content": "Together, we can create a sustainable future. A water bottle sustains you on the journey, just as a clear purpose energizes and inspires meaningful, impactful actions."
  },
  "37": {
    "title": "Wellness Boosters",
    "content": "Protect your body, mind, and soul with small, consistent actions that nourish well-being. A set of cutlery represents habits that strengthen overall health and lead to lasting vitality."
  },
  "38": {
    "title": "Kool Foundation",
    "content": "Care is at the heart of every endeavor. A fry pan serves loved ones, symbolizing the importance of nurturing relationships and projects that matter most. Build a foundation of support and compassion."
  },
  "39": {
    "title": "KoolBook",
    "content": "Documenting knowledge creates a legacy. A recipe book preserves culinary secrets, much like capturing experiences and insights inspires and guides future generations. Share your story—it’s a gift."
  },
  "40": {
    "title": "25 Bullets Writing",
    "content": "Aim before you write. A set of 25 colorful pencils organizes thoughts and ideas, creating something vibrant and impactful. Intentional writing leads to clarity and creativity."
  },
  "41": {
    "title": "Innovation Day",
    "content": "Innovation can happen anywhere with anyone. Paper clips hold ideas together, inspiring connections between minds and concepts to spark breakthroughs. Collaboration is the catalyst for new possibilities."
  },
  "42": {
    "title": "4P Presentation",
    "content": "Deliver your pitch with precision and impact. A pin hits its target, just as a well-crafted presentation leaves a lasting impression. Clear, captivating communication drives success."
  },
  "43": {
    "title": "5 Branding Discipline",
    "content": "Highlight your brand’s purpose. Highlighter pens emphasize key points, showing the importance of focusing on identity and values. Stand out by staying true to your vision."
  },
  "44": {
    "title": "Lean Canvas",
    "content": "Design lean and adapt quickly. A paint canvas offers a space to sketch bold ideas, refine them, and bring them to life with agility and focus."
  },
  "45": {
    "title": "Emotion by Design",
    "content": "Create a legacy, not just a memory. A stapler connects ideas seamlessly, reminding you to design with intention and evoke emotions that build deeper connections."
  },
  "46": {
    "title": "Visual Thinking",
    "content": "A picture speaks a thousand words. A camera captures moments, encouraging you to visualize thoughts and communicate them effectively. Transform complex ideas into clear, memorable visuals."
  },
  "47": {
    "title": "4A Feedback",
    "content": "Feedback is essential for growth. An eraser refines a sketch, symbolizing actionable, appreciative, and effective exchanges. Decide what to keep or discard, and grow through constructive feedback."
  },
  "48": {
    "title": "Prompt Engineering",
    "content": "Let brilliance emerge from the fusion of mind and machine. An iPad blends technology and creativity, opening doors to innovative solutions and unlocking your full potential."
  },
  "49": {
    "title": "Social Ecosystem Map",
    "content": "Connections are the foundation of a thriving future. A drawing compass maps relationships, helping to visualize networks and build a stronger, more connected community."
  },
  "50": {
    "title": "Design Thinking",
    "content": "Empathy drives innovation. Post-it Notes capture ideas, showing how understanding people’s needs fosters creative solutions. Start with care, and let creativity flourish."
  },
  "51": {
    "title": "KoolLab",
    "content": "Ideas are boundless. A computer mouse navigates endless possibilities, encouraging you to explore, experiment, and innovate in a space where creativity knows no limits."
  },
  "52": {
    "title": "Disruptive Innovation Business",
    "content": "Disruption can pave the way for progress. A blank sheet of A4 paper represents challenging the status quo and reimagining the way things are done. Bold ideas drive transformation."
  }
}

# ─── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="🎴 KoolBox", layout="centered")
st.title("🎴 KoolBox")

# ─── Reset State ─────────────────────────────────────────────────────────────────
def reset():
    for k in ["question_input", "question", "card_key", "answer", "takeaway", "generated_image"]:
        st.session_state.pop(k, None)

# ─── Ask-button callback ─────────────────────────────────────────────────────────
def ask_koolbox():
    q = st.session_state.question_input.strip()
    if not q:
        st.warning("Please type a question first.")
        return

    # Store question
    st.session_state.question = q

    # Draw a random card
    try:
        key = random.choice(list(cards.keys()))
        st.session_state.card_key = key
        card = cards[key]
    except NameError as e:
        st.error(f"Error accessing cards dictionary: {str(e)}")
        return

    # Build prompt for text answer and takeaway
    prompt = (
        f"{card['title']}\n"
        f"{card['content']}\n\n"
        "Provide a brief takeaway (1-2 sentences) summarizing the card's theme, followed by 'Answer to question:' and an answer to the question based on the card. "
        "Keep both concise and strip all markup styling. "
        "If the user asks in Chinese, reply in Chinese zh-hk."
        "If the card is not directly related, please still make up an insight that suit."
        f"\n\nTakeaway:\nAnswer to question: {q}"
    )

    # Call Gemini for text answer and takeaway
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            config=types.GenerateContentConfig(system_instruction=prompt),
            contents=q
        )
        # Split response into takeaway and answer
        response_text = res.text
        if "Answer to question:" in response_text:
            takeaway, answer = response_text.split("Answer to question:", 1)
            st.session_state.takeaway = takeaway.replace("Takeaway:", "").strip()
            st.session_state.answer = answer.strip()
        else:
            st.session_state.takeaway = "Unable to generate takeaway due to response format."
            st.session_state.answer = response_text.strip()
            st.warning("Response format issue: No 'Answer to question:' delimiter found.")
            # Debug: Log the response
            # st.write(f"Debug: Raw response: {response_text}")
    except Exception as e:
        st.error(f"Error generating text answer or takeaway: {str(e)}")
        return

    # Call Gemini for image generation based on the answer
    try:
        image_prompt = f"Create a visual representation of the following concept: {st.session_state.answer}"
        image_res = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        # Extract image data, ignore text
        for part in image_res.candidates[0].content.parts:
            if part.inline_data is not None:
                st.session_state.generated_image = part.inline_data.data
                break
        else:
            st.session_state.generated_image = None
            st.warning("No image generated by the model.")
    except Exception as e:
        st.session_state.generated_image = None
        st.error(f"Error generating image: {str(e)}")

# ─── New-session callback ────────────────────────────────────────────────────────
def new_session():
    reset()

# ─── Main UI ────────────────────────────────────────────────────────────────────
if "answer" in st.session_state:
    card = cards[st.session_state.card_key]

    st.subheader(card["title"])
    st.write(card["content"])

    st.markdown("---")
    st.markdown(f"**Your question:** {st.session_state.question}")

    # Display the card takeaway
    st.markdown("### 🎴 Card Takeaway")
    st.write(st.session_state.takeaway)

    # Display the text answer
    st.markdown("### 💡 Answer")
    st.write(st.session_state.answer)

    # Display the generated image
    if "generated_image" in st.session_state and st.session_state.generated_image:
        try:
            image = Image.open(BytesIO(st.session_state.generated_image))
            st.image(image, caption="Visual Representation", use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
    else:
        st.warning("No image available to display.")

    st.markdown("---")
    st.button("🔄 New Session", on_click=new_session)

else:
    st.text_area(
        "Ask KoolBox…",
        key="question_input",
        height=120,
        placeholder="E.g. How can I improve my focus today?"
    )
    st.button("🗣️ Ask KoolBox", on_click=ask_koolbox)
