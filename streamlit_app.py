import streamlit as st
import pandas as pd
import time
from datetime import datetime

# -------------------------
# LOAD DATA
# -------------------------

cars = pd.read_csv("cars.csv")
maintenance = pd.read_csv("maintenance.csv")

cars.columns = cars.columns.str.strip().str.lower()
maintenance.columns = maintenance.columns.str.strip().str.lower()

# -------------------------
# PAGE SETTINGS
# -------------------------

st.set_page_config(
    page_title="AI Based Car Advisory Chatbot",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Artificial Intelligence Based Car Advisory Chatbot")
st.write("Ask me about car models, seat recommendations, driving usage, maintenance, or car comparison!")

# -------------------------
# SESSION STATE INITIALIZATION
# -------------------------

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_chat" not in st.session_state:
    chat_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.current_chat = chat_id
    st.session_state.conversations[chat_id] = []

# -------------------------
# SIDEBAR – CHAT HISTORY
# -------------------------

st.sidebar.header("💬 Chat History")

for chat_id in st.session_state.conversations:
    if st.sidebar.button(chat_id):
        st.session_state.current_chat = chat_id

st.sidebar.divider()

if st.sidebar.button("🗑 Clear Current Chat"):
    st.session_state.conversations[st.session_state.current_chat] = []
    st.sidebar.success("Current chat cleared!")

if st.sidebar.button("➕ New Chat"):
    new_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.current_chat = new_id
    st.session_state.conversations[new_id] = []

# -------------------------
# TYPING EFFECT
# -------------------------

def type_writer(text, speed=0.01):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(f"**Bot:** {typed}")
        time.sleep(speed)

# -------------------------
# CHATBOT LOGIC
# -------------------------

def greeting_reply(text):
    if any(word in text.lower() for word in ["hi", "hello", "hey"]):
        return (
            "👋 Hi! I provide car advice based on real datasets.\n\n"
            "Try asking:\n"
            "• I drive mostly in city\n"
            "• Suggest me a 7 seater car\n"
            "• Compare Toyota Vios and Perodua Myvi\n"
            "• How often should I service Toyota Vios?"
        )
    return None


def car_comparison(text):
    if "compare" not in text.lower():
        return None

    found_cars = []

    for _, row in cars.iterrows():
        full_name = f"{row['brand']} {row['model']}".lower()
        if full_name in text.lower():
            found_cars.append(row)

    if len(found_cars) < 2:
        return "❌ Please specify **two car models** for comparison.\nExample: *Compare Toyota Vios and Perodua Myvi*"

    car1, car2 = found_cars[:2]

    return f"""
📊 **Car Comparison Result**

| Feature | {car1['brand']} {car1['model']} | {car2['brand']} {car2['model']} |
|--------|----------------|----------------|
| Engine | {car1['engine']} | {car2['engine']} |
| Fuel | {car1['fuel']} | {car2['fuel']} |
| Seats | {car1['seats']} | {car2['seats']} |
| Type | {car1['type']} | {car2['type']} |
"""


def driving_usage_recommendation(text):
    usage_map = {
        "city": "hatchback",
        "family": "mpv",
        "highway": "sedan"
    }

    for keyword, car_type in usage_map.items():
        if keyword in text.lower():
            results = cars[cars["type"] == car_type]
            if results.empty:
                return "❌ No suitable cars found."

            reply = f"🚗 **Recommended {car_type.title()} Cars:**\n\n"
            for _, row in results.iterrows():
                reply += f"• {row['brand']} {row['model']}\n"
            return reply
    return None


def seat_recommendation(text):
    for seat in ["5", "7"]:
        if f"{seat} seater" in text.lower():
            results = cars[cars["seats"] == int(seat)]
            reply = f"🚗 **{seat}-Seater Cars:**\n\n"
            for _, row in results.iterrows():
                reply += f"• {row['brand']} {row['model']}\n"
            return reply
    return None


def maintenance_advice(text):
    for _, row in maintenance.iterrows():
        full_name = f"{row['brand']} {row['model']}".lower()
        if full_name in text.lower():
            return f"""
🛠 **Maintenance – {row['brand']} {row['model']}**

• Engine oil: {row['engine_oil_km']} km  
• Major service: {row['major_service_km']} km  
• Battery lifespan: {row['battery_years']} years  
• Tyre rotation: {row['tyre_rotation_km']} km
"""
    return None


def car_info(text):
    for _, row in cars.iterrows():
        full_name = f"{row['brand']} {row['model']}".lower()
        if full_name in text.lower():
            return f"""
🚘 **{row['brand']} {row['model']}**

• Engine: {row['engine']}  
• Fuel: {row['fuel']}  
• Seats: {row['seats']}  
• Type: {row['type']}
"""
    return None


def chatbot_reply(text):
    for func in [
        greeting_reply,
        car_comparison,
        driving_usage_recommendation,
        seat_recommendation,
        maintenance_advice,
        car_info
    ]:
        reply = func(text)
        if reply:
            return reply

    return "🤔 I couldn't find that in my dataset. Try rephrasing."

# -------------------------
# CHAT UI
# -------------------------

user_input = st.text_input("You:", placeholder="Ask something...")

if st.button("Send") and user_input:
    st.session_state.conversations[st.session_state.current_chat].append(("You", user_input))
    st.session_state.conversations[st.session_state.current_chat].append(
        ("Bot", chatbot_reply(user_input))
    )

# -------------------------
# DISPLAY CHAT
# -------------------------

for sender, message in st.session_state.conversations[st.session_state.current_chat]:
    if sender == "Bot":
        type_writer(message)
    else:
        st.write(f"**{sender}:** {message}")

