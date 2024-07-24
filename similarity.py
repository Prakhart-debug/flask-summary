import docx
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Similarity:
    def read_docx(file_path):
        """ Function to read the contents of a .docx file. """
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error reading the document at {file_path}: {e}")
            return None
    
    def remove_redundancies(text):
        """ Function to remove redundancies (duplicate lines) from text. """
        lines = text.splitlines()
        unique_lines = list(dict.fromkeys(lines))  # Using dict.fromkeys to remove duplicates
        cleaned_text = '\n'.join(unique_lines)
        return cleaned_text
    
    def preprocess_text(text):
        """ Function to preprocess text data for similarity comparison. """
        # Tokenization
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphanumeric tokens
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        
        # Lemmatization
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        # Return preprocessed text as a single string
        return ' '.join(tokens)
    
    def calculate_similarity(text1, text2):
        """ Function to calculate cosine similarity between two texts. """
        preprocessed_text1 = Similarity.preprocess_text(text1)
        preprocessed_text2 = Similarity.preprocess_text(text2)
        
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([preprocessed_text1, preprocessed_text2])
        
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0][1]
        return cosine_sim
    
    def assess_ai_performance(input_file_path, output_file_path):
        print(input_file_path)
        print(output_file_path)
        """ Function to assess AI performance on document processing. """
        # Read input file
        input_text = Similarity.read_docx(input_file_path)
        
        if not input_text:
            return
        
        # Remove redundancies from input text
        cleaned_input_text = Similarity.remove_redundancies(input_text)
        
        # Read output file (assuming the output file is also a .docx for this example)
        output_text = Similarity.read_docx(output_file_path)
        
        if not output_text:
            return
        
        # Remove redundancies from output text
        cleaned_output_text = Similarity.remove_redundancies(output_text)
        
        # Calculate similarity between cleaned input and output texts
        similarity_score = Similarity.calculate_similarity(cleaned_input_text, cleaned_output_text)
        similarity_score = similarity_score*100
        # Print similarity score
        print(f"Similarity score between input and output documents: {similarity_score}")
        return similarity_score