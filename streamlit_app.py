import streamlit as st
import feedparser
import datetime
import requests
import json
import os

st.set_page_config(layout="wide")

# Access the API key from Streamlit secrets
CAREERONESTOP_API_KEY = st.secrets["COS_API_KEY"]
CAREERONESTOP_USER_ID = st.secrets["COS_USER_ID"]
BASE_URL = "https://api.careeronestop.org/v1"

scrollable_block_css = """
<style>
.scrollable-block {
    max-height: 500px; /* Adjust the max height as needed */
    overflow-y: auto;
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
}
</style>
"""

RSS_FEED_OPTIONS = {
    "Computer Engineering Technology 1": st.secrets["RSS_CET_1"],
    "Mechanical Engineering Technology 1": st.secrets["RSS_MET_1"],
    "Computer Engineering Technology 2": st.secrets["RSS_CET_2"],
    "Mechanical Engineering Technology 2": st.secrets["RSS_MET_2"]
}

# Function to make the API request
def fetch_careeronestop_data(api_url, headers=None, params=None):
    """
    Makes a GET request to the specified CareerOneStop API URL with optional headers and parameters.

    Args:
        api_url (str): The full URL of the CareerOneStop API endpoint.
        headers (dict, optional): A dictionary of HTTP headers to include in the request. Defaults to None.
        params (dict, optional): A dictionary of query parameters to include in the request. Defaults to None.

    Returns:
        dict or None: The JSON response from the API as a Python dictionary,
                     or None if an error occurred.
    """
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON response: {e}")
        return None

def display_scrollable_rss_feed(rss_url, num_entries=5):
    feed = feedparser.parse(rss_url)
    feed_content = ""
    if feed.get('bozo') == 1:
        feed_content = f"<p style='color: red;'>Error fetching or parsing RSS feed: {feed.get('bozo_exception')}</p>"
    else:
        feed_content += f"<h3>{feed.get('feed', {}).get('title', 'RSS Feed')}</h3>"
        for entry in feed.entries[:num_entries]:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '#')
            description = entry.get('description', 'No Description')
            published = entry.get('published')
            published_parsed = entry.get('published_parsed')

            entry_markdown = f"<strong><a href='{link}' target='_blank'>{title}</a></strong><br>"
            if published_parsed:
                published_date = datetime.datetime(*published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
                entry_markdown += f"<small><em>{published_date}</em></small><br>"
            elif published:
                entry_markdown += f"<small><em>{published}</em></small><br>"
            entry_markdown += f"<div style='margin-left: 10px;'>{description}</div><hr>"
            feed_content += entry_markdown
    return f'<div class="scrollable-block">{feed_content}</div>'

st.title("TC2 Hub Toolkit")
col1, col2 = st.columns([0.65,0.35])

with col1:
    st.subheader("Certification Lookup")
    keyword = st.text_input("Keyword:")
    if st.button("Search Certifications"):
        if keyword:
            api_endpoint = f"{BASE_URL}/certificationfinder/{CAREERONESTOP_USER_ID}/{keyword}/0/0/0/0/0/0/0/0/0/20"
            headers = {
                "Authorization": f"Bearer {CAREERONESTOP_API_KEY}",
                "Accept": "application/json"
            }
            certification_data = fetch_careeronestop_data(api_endpoint, headers=headers)
            if certification_data and "CertList" in certification_data:
                cert_list = certification_data["CertList"]
                if cert_list:
                    st.subheader("Matching Certifications:")
                    for cert in cert_list:
                        st.write(f"**{cert.get('Name', 'N/A')}**")
                        badges_markdown = ""
                        agency_list = cert.get("CertAccredAgencyList")
                        if agency_list:
                            for agency in agency_list:
                                agency_name = agency.get("Name", "").upper()
                                if agency_name == "IN-DEMAND":
                                    badges_markdown += f':red-badge[In-Demand] '
                                elif agency_name == "MILITARY":
                                    badges_markdown += f':green-badge[Military] '
                                elif agency_name == "ANSI":
                                    badges_markdown += f':blue-badge[ANSI] '
                                elif agency_name == "JOB CORPS":
                                    badges_markdown += f':violet-badge[Job Corps] '
                                elif agency_name == "NCCA":
                                    badges_markdown += f':violet-badge[NCCA] '
                                elif agency_name == "NAM":
                                    badges_markdown += f':violet-badge[NAM] '
                                elif agency_name == "ABNS":
                                    badges_markdown += f':violet-badge[ABNS] '
                                elif agency_name == "ICAC":
                                    badges_markdown += f':violet-badge[ICAC] '
                        if badges_markdown:
                            st.markdown(f"{badges_markdown}", unsafe_allow_html=True)
                        st.write(f"Organization: {cert.get('Organization', 'N/A')}")
                        st.write(f"Description: {cert.get('Description', 'N/A')}")
                        if "Url" in cert and cert["Url"]:
                            st.markdown(f"[More Info]({cert['Url']})")
                        st.markdown("---")
                else:
                    st.info("No certifications found matching your criteria.")
            else:
                st.error("Failed to retrieve certification data or 'CertList' not found.")
        else:
            st.warning("Please enter a keyword to search for certifications.")

with col2:
    st.subheader("Job Postings (Handshake)")
    selected_feed = st.selectbox("Select a feed:", list(RSS_FEED_OPTIONS.keys()))
    if selected_feed:
        rss_url = RSS_FEED_OPTIONS[selected_feed]
        rss_display = display_scrollable_rss_feed(rss_url) # This function returns the content wrapped in <div class="scrollable-block">
        st.markdown(rss_display, unsafe_allow_html=True)
