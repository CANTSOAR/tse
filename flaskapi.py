from flask import Flask, request
from orderbook import Orderbook
from basic_bot import bBot1

collected_file_names = []
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
        message = "recieved code from:"
        files = request.files.getlist("files")
        for file in files:
            content = file.read().decode("utf-8")
            collected_file_names.append(file.filename)
            collected_file_content.append(content)

            message += ("\n" + file.filename)

        return f"""
            <html>
            <body>
            <pre>{message}</pre>
            <a href = "/control">
            <button>go to control panel</button>
            </a>
            </body>
            </html>
        """
    except:
        return "file upload failure"
    
@app.route("/control")
def control():
    current_state = "files currently recieved:"
    for file in collected_file_names:
        current_state += ("\n" + file)

    return f"""
        <html>
        <body>
        <p>basic control panel</p>
        <pre>{current_state}</pre>
        <form action = "/run" method = "POST">
        <input type = "number" name = "ticks" min = "1" step = "1" placeholder = "# of ticks to run"/>
        <button type = "submit">run</button>
        </form>
        </body>
        </html>
    """

@app.route("/run", methods = ["POST"])
def run():
    if collected_file_content and not initiated_algos:
        for content in collected_file_content:
            try:
                local = {}
                exec(content, local)
                algo = local["Algo"]()
                initiated_algos.append(algo)
            except:
                continue

    if initiated_algos and "ticks" in request.form:
        book = Orderbook(initiated_algos)
        book.main_loop(int(request.form.get("ticks")))

        for algo in initiated_algos:
            algo_results[algo.get_name()] = algo.get_cash()

        total_sum2 = 0
        for participant in initiated_algos:
            total_sum2 += participant.get_cash()

        print(total_sum2)

        return """
            <html>
            <p>everything ran smoothly</p>
            <a href="/results">
            <button>view results</button>
            </a>
            </html>
        """
    
    return "something went wrong"

if __name__ == "__main__":
    app.run(port = 8000, debug=True)