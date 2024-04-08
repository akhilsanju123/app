from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import google.generativeai as genai
import google.ai.generativelanguage as glm
from io import BytesIO

gemini_api = "AIzaSyAKJxKabHwXQuH2Lt6sn53Fz7LZU8So0DQ"
genai.configure(api_key=gemini_api)

app = Flask(__name__)
CORS(app)

def genai_general(query):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query)
    return response.text

def pdf2txt(file):
    pdfFileObj = BytesIO(file.read())
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    data = []
    for pageObj in pdfReader.pages:
        data.append(pageObj.extract_text())

    pdfFileObj.close()

    return data

def genai_payroll(context, query):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("you are a payroll insight assistance can you answer the following query : "+query+" using the following content : "+' '.join(context))
    return response.text

@app.route('/')
def welcome():
    return "Welcome to the PDF Query Processor API!"
pdf_file_data = ""

@app.route('/extract_text', methods=['POST'])
def extract_text_r2r():
    global pdf_file_data
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    try:
        file = request.files['file']
        file_name = file.filename[:-4]
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file format'})

        pdf_file_data = pdf2txt(file)
        return jsonify({'text': 'PDF file processed successfully.', 'status':'success'})
    except Exception as e:
        return jsonify({'error':str(e), 'status':'failed'})

@app.route("/query_pdf", methods=["POST"])
def query_pdf():
    global pdf_file_data
    query = request.form.get("query")
    response = genai_payroll(pdf_file_data, query)
    return jsonify({'response':response, 'status':'success'})

@app.route("/general_qa", methods=["POST"])
def general_qa():
    query = request.form.get("query")
    response = genai_general(query)
    return jsonify({'response':response, 'status':'success'})

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=8004)
