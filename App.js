import file from "./algo_base.py"

function App() {
  return (
    <>
    <p>submit files here</p>
    <form method="POST" enctype="multipart/form-data" action="http://127.0.0.1:8000/receive_file">
      <input type="file" name="files" accept=".py" multiple/>
      <button type="submit">upload</button>
    </form>
    <a href={file} download><pre>
      base file download</pre></a>
    </>
  );
}

export default App;