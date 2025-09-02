import streamlit as st
import firebase_admin
from firebase_admin import firestore, credentials

# The error occurs because the "collection" object is not hashable.
# The best practice is to pass a hashable value (like a string)
# to the cached function, and get the unhashable object from inside.

# Initialize Firebase (this should only run once)
# Note: Replace with your actual Firebase credentials
try:
    cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    st.info("Firebase app already initialized.")

# Get a reference to the Firestore database
db = firestore.client()


# Use @st.cache_data for functions that return data frames
# This decorator needs all function arguments to be hashable.
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
    
    # Get the unhashable collection reference inside the function.
    collection_ref = db.collection(collection_name)
    
    # Fetch all documents and convert them to a list of dicts.
    docs = collection_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return data


# Example of how to call the corrected function.
if __name__ == "__main__":
    st.title("Firestore Data Loader")
    
    # Pass the collection name as a string, which is hashable.
    # The `load_data` function will now be properly cached.
    collection_name = "your_collection_name" 
    
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
