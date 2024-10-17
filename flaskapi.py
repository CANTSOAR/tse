from flask import Flask, request
from orderbook import Orderbook
from basic_bot import bBot1

collected_file_content = []
initiated_algos = []
algo_results = {}

app = Flask(__name__)

@app.route("/results")
def main():
    if algo_results:
        return str(algo_results)

    return "no results to show"

@app.route("/receive_file", methods = ["POST"])
def receive_file():
    try:
        file = request.files["file"]
        content = file.read().decode("utf-8")
        collected_file_content.append(content)

        return str("recieved code from " + file.filename)
    except:
        return "file upload failure"

@app.route("/run")
def run():
    if collected_file_content:
        for content in collected_file_content:
            try:
                local = {}
                exec(content, local)
                algo = local["Algo"]()
                initiated_algos.append(algo)
            except:
                continue

    if initiated_algos:
        book = Orderbook(initiated_algos)
        book.main_loop(100)

        for algo in initiated_algos:
            algo_results[algo.get_name()] = algo.get_cash()

        return "everything ran smoothly"
    
    return "something went wrong"

if __name__ == "__main__":
    app.run(port = 8000, debug=True)