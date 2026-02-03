import streamlit as st
import pandas as pd
import time

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
    page_title="Artificial Intelligence Based Car Advisory Chatbot for Malaysian Car Owners",
    page_icon="🚗"
)

st.title("🚗 Artificial Intelligence Based Car Advisory Chatbot for Malaysian Car Owners")
st.write("Ask me about car models, seat recommendations, driving usage, or maintenance!")

# -------------------------
# MEMORY
# -------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# TYPING EFFECT
# -------------------------

def type_writer(text, speed=0.02):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(f"**Bot:** {typed}")
        time.sleep(speed)

# -------------------------
# INTENT FUNCTIONS
# -------------------------

def greeting_reply(text):
    if any(word in text.lower() for word in ["hi", "hello", "hey"]):
        return (
            "👋 Hi! I provide car advice based on real datasets.\n\n"
            "You can ask:\n"
            "• *I drive mostly in city*\n"
            "• *Suggest me a 7 seater car*\n"
            "• *Tell me about Toyota Vios*\n"
            "• *How often should I service Perodua Myvi?*"
        )
    return None


# -------------------------
# DRIVING USAGE (CSV-BASED)
# -------------------------

def driving_usage_recommendation(text):
    text = text.lower()

    usage_map = {
        "city": "hatchback",
        "urban": "hatchback",
        "family": "mpv",
        "kids": "mpv",
        "highway": "sedan",
        "long distance": "sedan",
        "outstation": "sedan"
    }

    for keyword, car_type in usage_map.items():
        if keyword in text:
            results = cars[cars["type"].str.lower() == car_type]

            if results.empty:
                return "❌ No suitable cars found in the dataset."

            reply = f"🚗 **Recommended {car_type.title()} Cars for {keyword.title()} Driving:**\n\n"
            for _, row in results.iterrows():
                reply += f"• {row['brand']} {row['model']} ({row['engine']})\n"

            return reply

    return None


# -------------------------
# SEAT RECOMMENDATION
# -------------------------

def seat_recommendation(text):
    text = text.lower()
    for seat in ["5", "7"]:
        if f"{seat} seater" in text:
            results = cars[cars["seats"] == int(seat)]

            if results.empty:
                return "❌ No cars found with that seating capacity."

            reply = f"🚗 **{seat}-Seater Cars from Dataset:**\n\n"
            for _, row in results.iterrows():
                reply += f"• {row['brand']} {row['model']} ({row['type']})\n"
            return reply

    return None


# -------------------------
# MAINTENANCE (CSV-BASED)
# -------------------------

def maintenance_advice(text):
    text = text.lower()

    if "service" not in text and "maintenance" not in text:
        return None

    for _, row in maintenance.iterrows():
        full_name = f"{row['brand']} {row['model']}".lower()
        if full_name in text:
            return f"""
🛠 **Maintenance Schedule – {row['brand']} {row['model']}**

• Engine oil: every **{row['engine_oil_km']:,} km**
• Major service: every **{row['major_service_km']:,} km**
• Battery lifespan: **{row['battery_years']} years**
• Tyre rotation: every **{row['tyre_rotation_km']:,} km**
"""

    return "🛠 Please specify a car model found in the dataset."


# -------------------------
# CAR INFORMATION (CSV-BASED)
# -------------------------

def car_info(text):
    text = text.lower()
    for _, row in cars.iterrows():
        full_name = f"{row['brand']} {row['model']}".lower()
        if full_name in text:
            return f"""
🚘 **{row['brand']} {row['model']}**

• Engine: {row['engine']}
• Fuel: {row['fuel']}
• Seats: {row['seats']}
• Type: {row['type']}
"""
    return None


# -------------------------
# CHATBOT BRAIN
# -------------------------

def chatbot_reply(text):
    for func in [
        greeting_reply,
        driving_usage_recommendation,
        seat_recommendation,
        maintenance_advice,
        car_info
    ]:
        reply = func(text)
        if reply:
            return reply

    return (
        "🤔 I couldn’t find that in my dataset.\n\n"
        "Try asking:\n"
        "• *I drive mostly in city*\n"
        "• *Suggest me a 7 seater car*\n"
        "• *How often should I service Toyota Vios?*"
    )

# -------------------------
# UI
# -------------------------

user_input = st.text_input("You:", placeholder="Ask something...")

if st.button("Send") and user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", chatbot_reply(user_input)))

for sender, message in st.session_state.chat_history:
    if sender == "Bot":
        type_writer(message)
    else:
        st.write(f"**{sender}:** {message}")
