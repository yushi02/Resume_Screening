import streamlit as st
import pickle
import docx 
import PyPDF
import re
import nltk

nltk.download('punkt')
nltk.download('stopwords')

#loading models
clf = pickle.load(open('clf.pkl','rb'))
tfidfd = pickle.load(open('tfidf.pkl','rb'))
le = pickle.load(open('encoder.pkl', 'rb')) 

def clean_resume(resume_text):
    clean_text = re.sub('http\S+\s*', ' ', resume_text)
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\S+', '', clean_text)
    clean_text = re.sub('@\S+', '  ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)
    clean_text = re.sub('\s+', ' ', clean_text)
    return clean_text
# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


# Function to extract text from TXT with explicit encoding handling
def extract_text_from_txt(file):
    # Try using utf-8 encoding for reading the text file
    try:
        text = file.read().decode('utf-8')
    except UnicodeDecodeError:
        # In case utf-8 fails, try 'latin-1' encoding as a fallback
        text = file.read().decode('latin-1')
    return text


# Function to handle file upload and extraction
def handle_file_upload(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        text = extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        text = extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        text = extract_text_from_txt(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
    return text


# Function to predict the category of a resume
def pred(input_resume):
    # Preprocess the input text (e.g., cleaning, etc.)
    cleaned_text = cleanResume(input_resume)

    # Vectorize the cleaned text using the same TF-IDF vectorizer used during training
    vectorized_text = tfidf.transform([cleaned_text])

    # Convert sparse matrix to dense
    vectorized_text = vectorized_text.toarray()

    # Prediction
    predicted_category = svc_model.predict(vectorized_text)

    # get name of predicted category
    predicted_category_name = le.inverse_transform(predicted_category)

    return predicted_category_name[0]  # Return the category name


# Streamlit app layout
def main():
    st.set_page_config(page_title="Resume Category Prediction", page_icon="📄", layout="wide")

    st.title("Resume Category Prediction App")
    st.markdown("Upload a resume in PDF, TXT, or DOCX format and get the predicted job category.")

    # File upload section
    uploaded_file = st.file_uploader("Upload a Resume", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        # Extract text from the uploaded file
        try:
            resume_text = handle_file_upload(uploaded_file)
            st.write("Successfully extracted the text from the uploaded resume.")

            # Display extracted text (optional)
            if st.checkbox("Show extracted text", False):
                st.text_area("Extracted Resume Text", resume_text, height=300)

            # Make prediction
            st.subheader("Predicted Category")
            category = pred(resume_text)
            st.write(f"The predicted category of the uploaded resume is: **{category}**")

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")


if __name__ == "__main__":
    main()
