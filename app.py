import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from google.cloud import storage as google_storage

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'  # Replace with your Firebase storage bucket name
})

# Initialize Firestore
db = firestore.client()
bucket = storage.bucket()

# Streamlit App
def upload_complaint():
    # Display the form to input complaint and upload an image
    st.title("Submit Your Complaint")

    # Complaint Text Input
    complaint_text = st.text_area("Enter your complaint:")

    # File Upload
    complaint_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    if st.button("Submit"):
        if complaint_text and complaint_image:
            # Upload image to Firebase Storage
            image_filename = complaint_image.name
            image_path = os.path.join("images", image_filename)

            # Save the uploaded image to Firebase storage
            blob = bucket.blob(image_path)
            blob.upload_from_file(complaint_image)

            # Save complaint data to Firestore
            complaint_ref = db.collection('complaints')
            complaint_ref.add({
                'complaint_text': complaint_text,
                'complaint_image_url': blob.public_url,  # Image URL from Firebase Storage
                'status': 'pending'
            })

            st.success("Your complaint has been submitted successfully!")
        else:
            st.error("Please enter complaint text and upload an image!")

# Show complaints from Firestore
def show_complaints():
    st.title("Complaints")
    complaints_ref = db.collection('complaints')
    complaints = complaints_ref.stream()

    for complaint in complaints:
        complaint_data = complaint.to_dict()
        st.subheader(f"Complaint ID: {complaint.id}")
        st.write(f"Complaint Text: {complaint_data['complaint_text']}")
        st.write(f"Status: {complaint_data['status']}")
        st.image(complaint_data['complaint_image_url'], caption='Complaint Image', use_column_width=True)
        st.write("---")

# Main function
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", ["Submit Complaint", "View Complaints"])

    if page == "Submit Complaint":
        upload_complaint()
    elif page == "View Complaints":
        show_complaints()

if __name__ == "__main__":
    main()


