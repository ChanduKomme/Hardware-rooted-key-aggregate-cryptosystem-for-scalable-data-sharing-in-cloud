from flask import Flask, request, send_file, make_response
import os, json
app = Flask(__name__)
os.makedirs("storage", exist_ok=True)

@app.post("/upload")
def upload():
    f = request.files["file"]
    fn = request.form["filename"]
    hdr = json.loads(request.form["header"])
    open(f"storage/{fn}", "wb").write(f.read())
    open(f"storage/{fn}.hdr", "w").write(json.dumps(hdr))
    return "OK"

@app.get("/download/<fn>")
def download(fn):
    hdr = open(f"storage/{fn}.hdr").read()
    resp = make_response(send_file(f"storage/{fn}"))
    resp.headers["X-KAC-HEADER"] = hdr
    return resp

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
