from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

SERVICES = {
    'parser': f'http://localhost:{config.SERVICE_PORTS["parser"]}',
    'lexicon': f'http://localhost:{config.SERVICE_PORTS["lexicon"]}',
    'grammar': f'http://localhost:{config.SERVICE_PORTS["grammar"]}',
    'crypto': f'http://localhost:{config.SERVICE_PORTS["crypto"]}'
}

@app.route('/process', methods=['POST'])
def process_text():
    try:
        # Step 1: Parse input text
        parsed = requests.post(f"{SERVICES['parser']}/parse", json={
            'text': request.json['text']
        }).json()

        # Step 2: Generate lexicon
        lexicon = requests.post(f"{SERVICES['lexicon']}/generate", json={
            'passphrase': request.json['passphrase'],
            'unique_words': parsed['unique_words']
        }).json()

        # Step 3: Analyze grammar
        grammar = requests.post(f"{SERVICES['grammar']}/analyze", json={
            'passphrase': request.json['passphrase'],
            'parsed_text': parsed
        }).json()

        # Step 4: Encrypt/Decrypt
        crypto = requests.post(f"{SERVICES['crypto']}/process", json={
            'lexicon': lexicon,
            'grammar': grammar,
            'operation': request.json['operation'],
            'text': request.json['text']
        }).json()

        return jsonify(crypto)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)