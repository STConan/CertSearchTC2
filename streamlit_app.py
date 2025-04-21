import streamlit as st
import requests
import json
import os

# Access the API key from Streamlit secrets
CAREERONESTOP_API_KEY = st.secrets["COS_API_KEY"]
CAREERONESTOP_USER_ID = st.secrets["COS_USER_ID"]
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
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
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
        api_endpoint = f"{BASE_URL}/certificationfinder/{CAREERONESTOP_USER_ID}/{keyword}/0/0/0/0/0/0/0/0/0/20"
        headers = {
            "Authorization": f"Bearer {CAREERONESTOP_API_KEY}",
            "Accept": "application/json"  # Specify that we want JSON response
        }

        certification_data = fetch_careeronestop_data(api_endpoint, headers=headers)

        if certification_data:
            if "Certifications" in certification_data and certification_data["Certifications"]:
                st.subheader("Matching Certifications:")
                for cert in certification_data["Certifications"]:
                    st.write(f"**{cert.get('Title', 'N/A')}**")
                    st.write(f"Description: {cert.get('Summary', 'N/A')}")
                    st.write(f"Provider: {cert.get('OrganizationName', 'N/A')}")
                    if "CredentialURL" in cert and cert["CredentialURL"]:
                        st.markdown(f"[More Info]({cert['CredentialURL']})")
                    st.markdown("---")
            else:
                st.info("No certifications found matching your criteria.")
        else:
            st.error("Failed to retrieve certification data.")
    else:
        st.warning("Please enter a keyword to search for certifications.")

# --- Example for job data (adjust URL and parameters based on API docs) ---
st.subheader("Find Jobs (Example)")
job_title = st.text_input("Enter a job title:")
if st.button("Search Jobs"):
    if job_title:
        api_endpoint = f"{BASE_URL}/jobsearch"
        params = {
            "keyword": job_title,
            "user_id": CAREERONESTOP_USER_ID,
            "key": CAREERONESTOP_API_KEY,
            "format": "json"
            # Add other job search parameters
        }
        job_data = fetch_careeronestop_data(api_endpoint, params=params)
        if job_data and "Results" in job_data and job_data["Results"]:
            st.write("Job Data:")
            st.json(job_data) # Display the raw JSON for now
        elif job_data:
            st.info("No jobs found.")
        else:
            st.error("Failed to retrieve job data.")
    else:
        st.warning("Please enter a job title.")
