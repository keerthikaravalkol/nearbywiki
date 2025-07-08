import streamlit as st
import requests

def get_nearby_wikipedia_articles(lat, lon, radius=10000, limit=10):
    url = "https://en.wikipedia.org/w/api.php"
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
        st.error(f"Failed to fetch nearby articles. Status code: {response.status_code}")
        return []

def get_article_summary(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def main():
    st.title("📍 NearbyWiki — Wikipedia Articles Near You")
    st.write("Enter latitude and longitude to find Wikipedia articles nearby.")

    lat = st.text_input("Latitude (e.g., 37.7749)")
    lon = st.text_input("Longitude (e.g., -122.4194)")

    if lat and lon:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            articles = get_nearby_wikipedia_articles(lat_f, lon_f)

            if articles:
                st.success(f"Found {len(articles)} articles near ({lat_f}, {lon_f}):")
                for art in articles:
                    title = art.get("title")
                    dist = art.get("dist")
                    summary_data = get_article_summary(title)
                    summary = summary_data.get("extract") if summary_data else "No summary available."
                    thumbnail = summary_data.get("thumbnail", {}).get("source") if summary_data else None
                    wiki_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page") if summary_data else None

                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            if thumbnail:
                                st.image(thumbnail, width=100)
                            else:
                                st.write("📝")
                        with cols[1]:
                            if wiki_url:
                                st.markdown(f"### [{title}]({wiki_url})")
                            else:
                                st.markdown(f"### {title}")
                            st.write(f"Distance: {dist/1000:.2f} km")
                            with st.expander("Summary"):
                                st.write(summary)
                        st.markdown("---")

            else:
                st.info("No articles found near this location.")
        except ValueError:
            st.error("Please enter valid numeric values for latitude and longitude.")

if __name__ == "__main__":
    main()
