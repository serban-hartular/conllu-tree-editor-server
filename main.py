from flask import Flask, send_from_directory
import random
from flask import request
import json

from process_request import text_to_treelist

app = Flask(__name__)

# Path for our main Svelte page
@app.route("/old")
def base():
    return send_from_directory('client-old/public', 'index.html')

@app.route("/")
def test():
    return send_from_directory('client/public', 'index.html')


# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/rand")
def hello():
    n = random.randint(0, 100)
    print(n)
    return str(n)

@app.route("/echo", methods=['POST'])
def echo():
    obj = request.get_json()
    print(obj)
    obj['text'] = obj['text'] * 2
    print(json.dumps(obj))
    return json.dumps(obj)

@app.route("/parse", methods=['POST'])
def parse_text():
    return_obj = {'tree': dict(), 'error_msg': ''}
    obj = None
    try: # get json obj
        obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    try: # get members
        text = obj['text']
        lang = obj['lang']
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    parse_obj = text_to_treelist(text, lang)
    return_obj['tree'] = parse_obj
    return json.dumps(return_obj)


if __name__ == "__main__":
    app.run(debug=True)
