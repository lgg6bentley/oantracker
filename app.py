import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase using Streamlit Secrets
try:
    cred = credentials.Certificate(json.loads(st.secrets["firebase_key"]))
    firebase_admin.initialize_app(cred)
except ValueError:
    st.info("Firebase app already initialized.")

# Get a reference to the Firestore database
db = firestore.client()

# Use @st.cache_data for functions that return data frames
@st.cache_data
def load_data(collection_name):
    """
    Loads all documents from a specified Firestore collection.
    
    Args:
        collection_name (str): The name of the collection to load.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a document.
    """
    st.write(f"Loading data from Firestore collection: {collection_name}")
    
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return data

# Main Streamlit app
def main():
    st.title("Firestore Data Loader")

    # Input for collection name
    collection_name = st.text_input("Enter Firestore collection name:", "your_collection_name")

    if collection_name:
        # Simulate a small collection for demonstration
        dummy_collection = db.collection(collection_name)
        dummy_data = {"name": "Test User", "score": 100, "date": firestore.SERVER_TIMESTAMP}
        dummy_collection.add(dummy_data)

        try:
            data_df = load_data(collection_name)
            st.write("Data loaded successfully:")
            st.dataframe(data_df)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()