import streamlit as st
import requests
import re


# ================= WIKIPEDIA FETCH =================
def get_wikipedia_text(topic, lines):

    topic = topic.replace(" ", "_")

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": topic,
        "redirects": 1
    }

    headers = {
        "User-Agent": "RevisionAssistant/1.0"
    }

    r = requests.get(url, params=params, headers=headers)
    data = r.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    text = page.get("extract", "")

    sentences = re.split(r'(?<=[.!?]) +', text)

    return sentences[:lines]


# ================= PROCESS CONTENT =================
def build_revision(sentences):

    full_text = " ".join(sentences)

    # Short summary
    short_summary = " ".join(sentences[:2])

    # Key points (important sentences)
    key_points = []
    for s in sentences:
        if any(word in s.lower() for word in ["is", "are", "used", "defined", "refers", "known", "means"]):
            key_points.append(s.strip())

    key_points = key_points[:6]

    # Concepts (important words)
    words = re.findall(r'\b[a-zA-Z]{5,}\b', full_text.lower())

    stopwords = {
        "these", "those", "which", "their", "there", "about",
        "would", "could", "should", "because", "being", "using"
    }

    concepts = []
    for w in words:
        if w not in stopwords and w not in concepts:
            concepts.append(w)

    concepts = concepts[:10]

    return short_summary, key_points, concepts


# ================= STREAMLIT UI =================
st.set_page_config(page_title="Smart Revision Assistant", layout="centered")

st.title("📚 Smart Revision Assistant")
st.write("Turn any topic into clean revision notes instantly.")

topic = st.text_input("Enter Topic")

lines = st.slider("How many lines of summary?", 5, 20, 8)

if st.button("Generate Revision Notes"):

    if topic.strip() == "":
        st.warning("Please enter a topic")
    else:

        with st.spinner("Fetching from Wikipedia..."):

            try:
                sentences = get_wikipedia_text(topic, lines)

                if not sentences:
                    st.error("No data found for this topic.")
                else:

                    short, points, concepts = build_revision(sentences)

                    st.subheader("📌 Quick Summary")
                    st.write(short)

                    st.subheader("🧠 Key Points")
                    for p in points:
                        st.write("•", p)

                    st.subheader("🔑 Important Concepts")
                    st.write(", ".join(concepts))

                    st.subheader("📄 Full Extract (for revision)")
                    st.write(" ".join(sentences))

            except Exception as e:
                st.error(f"Error: {e}")