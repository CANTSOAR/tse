function App() {
  return (
    <>
    <div>Hello</div>
    <form method="post" enctype="multipart/form-data" action="http://127.0.0.1:8000/receive_file">
      <input type="file" name="file" accept=".py"/>
      <button>upload</button>
    </form>
    </>
  );
}

export default App;
