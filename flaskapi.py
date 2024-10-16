from flask import Flask, request
from orderbook import Orderbook
from basic_bot import bBot1

collected_file_content = []
initiated_algos = []

app = Flask(__name__)

@app.route("/main")
def main():
    return "this is main page"

@app.route("/receive_file", methods = ["POST"])
def receive_file():
    file = request.files["file"]
    content = file.read().decode("utf-8")
    collected_file_content.append(content)

    return str("recieved code from " + file.filename)

@app.route("/run")
def run():
    if len(collected_file_content):
        for content in collected_file_content:
            local = {}
            exec(content, local)
            algo = local["Algo"]()
            initiated_algos.append(algo)
            print(algo.get_name())

    book = Orderbook(initiated_algos)
    print("everything initiated, running algo")
    book.main_loop(100)

    return "everything ran smoothly"

if __name__ == "__main__":
    app.run(port = 8000, debug=True)