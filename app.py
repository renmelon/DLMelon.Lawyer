from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import openai
from openai.error import OpenAIApiError
import PyPDF2
import os

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'  # Adicione sua própria chave secreta

# Configure OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/')
def index():
    return render_template('index.html')  # Este template deverá ter um campo de upload para PDFs.

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        flash('Nenhuma parte do arquivo')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        sentence_text = extract_text_from_pdf(filepath)
        answers = get_analysis(sentence_text)
        result = generate_appeal_text(answers)
        return jsonify(result=result)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()
    return text

def get_analysis(sentence_text):
    prompts = [
        "Is this sentence good or bad for the involved party?",
        "What are the fundaments it has used to define the thesis?",
        "Based on local law and regulations, how can one overcome this sentence?"
    ]
    return ask_chatgpt(sentence_text, prompts)

def ask_chatgpt(text, prompts):
    try:
        response = openai.Completion.create(
            model="gpt-4.0-turbo", 
            prompt="\n\n".join([f"{text}\n{prompt}" for prompt in prompts]),
            n=len(prompts),
            max_tokens=150
        )
        return [choice.text.strip() for choice in response.choices]
    except OpenAIApiError as error:
        return [str(error)] * len(prompts)

def generate_appeal_text(answers):
    good_or_bad, fundamentals, strategy = answers
    if "bad" in good_or_bad.lower():
        return (f"The recent judgment was unfavorable. The decision was based on: {fundamentals}. "
                f"To overcome this judgment, consider these strategies: {strategy}.")
    else:
        return "The judgment was favorable. If there's another aspect to explore, please specify."

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
