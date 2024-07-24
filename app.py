from flask import Flask, render_template, request, redirect, jsonify, send_file
import os
import random
import string
import zipfile
import shutil
import json
import requests

app = Flask(__name__)

GROQ_API_URL = "https://api.groq.com/v1"  # Replace with the actual Groq API endpoint
GROQ_API_KEY = "YOUR_GROQ_API_KEY"  # Replace with your Groq API key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return redirect(request.url)

    file_objs = request.files.getlist('files')
    random_folder_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    if not os.path.exists(random_folder_name):
        os.makedirs(random_folder_name)
    for file_obj in file_objs:
        if file_obj.filename == '':
            continue
        file_path = os.path.join(random_folder_name, file_obj.filename)
        file_obj.save(file_path)
    return jsonify({"data": random_folder_name}), 200

@app.route('/get_similarity', methods=['GET'])
def get_similarity():
    folder = request.args.get('folder_name')
    with open('map.json', 'r') as file:
        data = json.load(file)
    data1 = data[folder]
    ret = ""
    for x in data1:
        input_file = os.path.join(folder + "_files", x["file_name"])
        output_file = x["output"].replace("\\",'/')
        sim_score = assess_similarity(input_file, output_file)
        ret += f"The Similarity score for {x['output'].replace(folder + '_summary/', '')} is {sim_score}<br>"

    del data[folder]
    with open('map.json', 'w') as file:
        json.dump(data, file, indent=4)
    return jsonify({"data": ret}), 200

def assess_similarity(input_file, output_file):
    url = f"{GROQ_API_URL}/similarity"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"input_file": open(input_file, 'rb'), "output_file": open(output_file, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    response_data = response.json()
    return response_data.get('similarity_score', 'N/A')

@app.route('/clean_files', methods=['GET'])
def clean_files():
    folder = request.args.get('folder_name')
    shutil.rmtree(folder)
    shutil.rmtree(folder + "_clusters")
    shutil.rmtree(folder + "_files")
    shutil.rmtree(folder + "_output")
    shutil.rmtree(folder + "_summary")
    return jsonify({"data": "Cleaned up files"}), 200

@app.route('/run_script', methods=['GET'])
def run_script():
    upload_folder = request.args.get('upload_folder')
    if not upload_folder:
        return "No files uploaded yet."

    try:
        cluster_folder_name = upload_folder + "_clusters"
        file_folder_name = upload_folder + "_files"
        summary_folder_name = upload_folder + "_summary"
        output_folder_name = upload_folder + "_output"
        os.makedirs(cluster_folder_name, exist_ok=True)
        os.makedirs(file_folder_name, exist_ok=True)
        os.makedirs(summary_folder_name, exist_ok=True)
        os.makedirs(output_folder_name, exist_ok=True)

        invoke_clustering(upload_folder, cluster_folder_name)
        invoke_merging(file_folder_name, cluster_folder_name)
        invoke_chunking(file_folder_name, summary_folder_name, upload_folder)

        zip_folder(summary_folder_name, os.path.join(output_folder_name, "Consolidated_Outputs.zip"))
    except Exception as e:
        return f"Error running script: {e}"
    return send_file(os.path.join(output_folder_name, "Consolidated_Outputs.zip"), as_attachment=True, download_name="Consolidated_Outputs.zip")

def invoke_clustering(upload_folder, cluster_folder_name):
    url = f"{GROQ_API_URL}/clustering"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"folder": open(upload_folder, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise Exception("Clustering API call failed")

def invoke_merging(file_folder_name, cluster_folder_name):
    url = f"{GROQ_API_URL}/merging"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {"file_folder": file_folder_name, "cluster_folder": cluster_folder_name}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception("Merging API call failed")

def invoke_chunking(file_folder_name, summary_folder_name, upload_folder):
    url = f"{GROQ_API_URL}/chunking"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {"file_folder": file_folder_name, "summary_folder": summary_folder_name, "upload_folder": upload_folder}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception("Chunking API call failed")

def zip_folder(folder_path, output_path):
    zip_obj = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zip_obj.write(os.path.join(root, file), 
                          os.path.relpath(os.path.join(root, file), 
                                          os.path.join(folder_path, '..')))
    zip_obj.close()

if __name__ == '__main__':
    app.run(debug=True)
