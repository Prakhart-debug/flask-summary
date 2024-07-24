import docx2txt
import spacy
import os
nlp=spacy.load('en_core_web_sm')
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from gensim.models import Word2Vec
from sklearn.cluster import DBSCAN
from hdbscan import HDBSCAN
import shutil


class Clustering:
    def invoke(directory,folder_name):
        if os.path.exists(folder_name):
            try:
                shutil.rmtree(folder_name)
                print(f"Existing '{folder_name}' Folder successfully deleted.")
            except Exception as e:
                print(f"Error deleting folder '{folder_name}': {e}")
        else:
            pass
        raw_documents = []
        documents = []
        filenames=[]
        for filename in os.listdir(directory):
            if filename.endswith(".docx"):
                file_path = os.path.join(directory, filename)
                content = docx2txt.process(file_path)
                raw_documents.append(content)  # Save a copy of the original document
                documents.append(Clustering.preprocess(content))
                filenames.append(filename)  # Save the preprocessed document


        vectorizer = TfidfVectorizer()  # Use bi-grams
        X = vectorizer.fit_transform(documents)

        affinity_propagation = AffinityPropagation()  # Using default parameters
        clusters = affinity_propagation.fit_predict(X)


        grouped_documents = defaultdict(list)
        for i, cluster in enumerate(clusters):
            grouped_documents[cluster].append(filenames[i])

        for cluster, docs in grouped_documents.items():
            print(f'Cluster {cluster}:')
            cluster_dir = folder_name + f'/Cluster {cluster+1}/'
            os.makedirs(cluster_dir)
            
            for i, doc in enumerate(docs):
                print(f'Document {i+1}:{doc}')
                #print(doc)
            for file_name in docs:
                #print(file_name)
                if file_name.endswith('.docx'):
                    destination_path = folder_name + f'/Cluster {cluster+1}/'
                    #shutil.rmtree(destination_path)
                    #  doc = Document()
                    #  doc.save(f'Clusters/Cluster {cluster+1}/{file_name}')
                    with open(destination_path + file_name, 'w') as fp:
                        pass
                    path = folder_name + f'/Cluster {cluster+1}/'
                    destination_file = os.path.join(path,file_name)
                    source_path = os.path.join(directory, file_name)
                    shutil.copy2(source_path, destination_file)
                    print(f"File '{file_name}' copied successfully to '{cluster+1}'")

    def preprocess(text):
        text=text.lower()
        doc=nlp(text)
        preprocessed_tokens = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space and token.text.strip():
                preprocessed_tokens.append(token.lemma_)
        return ' '.join(preprocessed_tokens) 
