import streamlit as st
import requests

# Supported languages
LANGUAGE_CODES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "తెలుగు (Telugu)": "te"
}

# Translation via LibreTranslate API
def translate_text(text, target_lang):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "en",
        "target": target_lang,
        "format": "text"
    }
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            return response.json().get("translatedText")
        else:
            return "⚠️ Translation failed."
    except:
        return "⚠️ Translation service error."

# Get nearby articles in selected language
def get_nearby_wikipedia_articles(lat, lon, lang="en", radius=10000, limit=10):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "geosearch",
        "gscoord": f"{lat}|{lon}",
        "gsradius": radius,
        "gslimit": limit,
        "format": "json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("query", {}).get("geosearch", [])
    else:
        return []

# Fetch article summary in selected language
def get_article_summary(title, lang="en"):
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Main Streamlit App
def main():
    st.set_page_config(page_title="NearbyWiki", page_icon="🌍")
    st.title("📍 NearbyWiki — Wikipedia Articles Near You")

    language = st.radio("🌐 Choose Language:", list(LANGUAGE_CODES.keys()), horizontal=True)
    lang_code = LANGUAGE_CODES[language]

    lat = st.text_input("📌 Latitude (e.g., 17.3850)")
    lon = st.text_input("📌 Longitude (e.g., 78.4867)")

    if lat and lon:
        try:
            lat_f = float(lat)
            lon_f = float(lon)

            # Try getting articles in selected language
            articles = get_nearby_wikipedia_articles(lat_f, lon_f, lang=lang_code)
            if not articles and lang_code != "en":
                st.info("🔁 No results found in selected language. Falling back to English.")
                articles = get_nearby_wikipedia_articles(lat_f, lon_f, lang="en")

            if articles:
                st.success(f"✅ Found {len(articles)} articles near ({lat_f}, {lon_f}):")

                for art in articles:
                    title = art.get("title")
                    dist = art.get("dist")

                    # Try fetching in selected language
                    summary_data = get_article_summary(title, lang=lang_code)
                    fallback_used = False

                    if not summary_data and lang_code != "en":
                        # Fallback to English if not found
                        summary_data = get_article_summary(title, lang="en")
                        fallback_used = True

                    if summary_data:
                        summary = summary_data.get("extract", "⚠️ No summary.")
                        thumbnail = summary_data.get("thumbnail", {}).get("source")
                        wiki_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page")

                        # Translate if fallback used
                        if fallback_used and lang_code != "en":
                            translated_summary = translate_text(summary, lang_code)
                            if translated_summary:
                                summary = translated_summary

                        with st.container():
                            cols = st.columns([1, 3])
                            with cols[0]:
                                if thumbnail:
                                    st.image(thumbnail, width=100)
                                else:
                                    st.write("📄")
                            with cols[1]:
                                st.markdown(f"### [{title}]({wiki_url})" if wiki_url else f"### {title}")
                                st.write(f"📏 Distance: {dist/1000:.2f} km")
                                with st.expander("🔎 Summary"):
                                    st.write(summary)
                        st.markdown("---")
            else:
                st.warning("⚠️ No nearby articles found.")
        except ValueError:
            st.error("❗ Please enter valid numbers for latitude and longitude.")

if __name__ == "__main__":
    main()
