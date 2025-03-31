import streamlit as st
import openai

# ----------------------------
# 🌟 Custom CSS for ChatGPT-like UI & Light Blue Background
# ----------------------------
st.markdown("""
    <style>
        .stApp { background-color: #e6f3ff; }
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #003366; }
        .stChatMessage { border-radius: 10px; padding: 10px; margin-bottom: 5px; background-color: #ffffff; border: 1px solid #0077b6; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# 🍽 Sidebar: API Key, History
# ----------------------------
st.sidebar.title("🔑 API Settings")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
if not openai_api_key:
    st.sidebar.info("Please enter your API key to continue.")
    st.stop()

# ✅ OpenAI Client
client = openai.OpenAI(api_key=openai_api_key)

# 🍽 Chat History in Sidebar
st.sidebar.title("📜 Chat History")
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    st.sidebar.write(f"🗨️ {msg['role'].capitalize()}: {msg['content'][:40]}...")

# ----------------------------
# 🚗 Main Title & Introduction
# ----------------------------
st.markdown("<h1 class='title'>🚗 Used Car Recommendation Chatbot</h1>", unsafe_allow_html=True)
st.write("Welcome! Tell us your budget, preferred car model, or mileage, and we'll recommend the best used cars for you.")

# ----------------------------
# 📜 System Prompt
# ----------------------------
SYSTEM_PROMPT = """You are a car recommendation assistant who helps users find the best used cars based on their budget, preferred car model, or mileage. 
Provide a structured response with:
- **Car Model** (with year) 🚗
- **Price Range** 💰
- **Mileage** 🛣️
- **Key Features** (e.g., fuel efficiency, safety features, etc.) 🔑
- **Pros and Cons** 📊

Then, provide the following:
- **Car Image** (Generate an AI-based image using DALL·E)
- **Carfax & CarMax Links**

### Example
**User:** "I have a budget of $15,000 and prefer a sedan with less than 50,000 miles."
**Assistant:**
**Car Model:** 2018 Honda Accord
**Price Range:** $14,000 - $16,000
**Mileage:** 45,000 miles
**Key Features:** Fuel-efficient, spacious interior, advanced safety features
**Pros and Cons:** Pros - Reliable, good resale value; Cons - Slightly higher maintenance cost
**Carfax Link:** [Carfax](https://www.carfax.com/Used-Honda-Accord_w123456)
**CarMax Link:** [CarMax](https://www.carmax.com/cars/honda/accord)
"""

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

# --------------------------------------
# 💬 Display Chat History
# --------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------------------------------
# 🚗 User Input & OpenAI ChatCompletion
# ------------------------------------------------
if user_input := st.chat_input("Tell us your budget, preferred car model, or mileage here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ OpenAI API Call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        temperature=0.7
    )

    # Extract AI Response
    assistant_reply = response.choices[0].message.content
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    # Save OpenAI Response
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # ----------------------------
    # 🎨 Generate Car Image with DALL·E
    # ----------------------------
    def generate_car_image(car_model):
        dalle_response = client.images.generate(
            model="dall-e-3",
            prompt=f"A high-quality image of a {car_model}, front view, studio lighting.",
            size="1024x1024"
        )
        return dalle_response.data[0].url

    # 提取车辆型号
    car_model = ""
    for line in assistant_reply.split("\n"):
        if "**Car Model:**" in line:
            car_model = line.replace("**Car Model:**", "").strip()
            break

    if car_model:
        car_image_url = generate_car_image(car_model)
        if car_image_url:
            st.image(car_image_url, caption=f"{car_model}", use_column_width=True)

        # ----------------------------
        # 🔗 生成 Carfax & CarMax 购买链接
        # ----------------------------
        carfax_link = f"[View on Carfax](https://www.carfax.com/Used-{car_model.replace(' ', '-')})"
        carmax_link = f"[View on CarMax](https://www.carmax.com/cars/{car_model.replace(' ', '-').lower()})"

        st.markdown(f"🔗 {carfax_link}  |  {carmax_link}")