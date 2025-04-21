import streamlit as st
import requests
import json
import os

BASE_URL = "https://api.careeronestop.org/v1"

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

st.title("Career Certification Lookup")

keyword = st.text_input("Keyword:")

if st.button("Search Certifications"):
    if keyword:
        api_endpoint = f"{BASE_URL}/certificationfinder/{st.secrets["COS_USER_ID"]}/{keyword}/0/0/0/0/0/0/0/0/0/20"
        headers = {
            "Authorization": f"Bearer {st.secrets["COS_API_KEY"]}",
            "Accept": "application/json"
        }

        certification_data = fetch_careeronestop_data(api_endpoint, headers=headers)

        if certification_data and "CertList" in certification_data:
            cert_list = certification_data["CertList"]
            if cert_list:
                st.subheader("Matching Certifications:")
                for cert in cert_list:
                    st.write(f"**{cert.get('Name', 'N/A')}**")
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
