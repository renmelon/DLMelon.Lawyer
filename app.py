from flask import Flask, render_template, request, jsonify
import openai
from openai.error import OpenAIApiError

app = Flask(__name__)

# Configure OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    sentence_text = request.form.get('sentence')
    answers = get_analysis(sentence_text)
    result = generate_appeal_text(answers)
    return jsonify(result=result)

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

def get_analysis(sentence_text):
    prompts = [
        "Is this sentence good or bad for the involved party?",
        "What are the fundaments it has used to define the thesis?",
        "Based on local law and regulations, how can one overcome this sentence?"
    ]
    return ask_chatgpt(sentence_text, prompts)

def generate_appeal_text(answers):
    good_or_bad, fundamentals, strategy = answers
    if "bad" in good_or_bad.lower():
        return (f"The recent judgment was unfavorable. The decision was based on: {fundamentals}. "
                f"To overcome this judgment, consider these strategies: {strategy}.")
    else:
        return "The judgment was favorable. If there's another aspect to explore, please specify."

if __name__ == '__main__':
    app.run(debug=True)
