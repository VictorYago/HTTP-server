import json
from http_server import HTTPServer, make_response

app   = HTTPServer(host="localhost", port=8080)
tasks: dict = {}
next_id     = 1


# ── GET /tasks ────────────────────────────

@app.get("/tasks")
def list_tasks(req):
    return make_response(200, list(tasks.values()))


# ── GET /tasks/* ──────────────────────────

@app.get("/tasks/*")
def get_task(req):
    tid = req["path"].split("/")[-1]
    if tid not in tasks:
        return make_response(404, {"erro": "Tarefa não encontrada"})
    return make_response(200, tasks[tid])


# ── POST /tasks ───────────────────────────

@app.post("/tasks")
def create_task(req):
    global next_id
    try:
        data = json.loads(req["body"])
    except Exception:
        return make_response(400, {"erro": "Body JSON inválido"})

    tid = str(next_id)
    next_id += 1
    tasks[tid] = {"id": tid, "titulo": data.get("titulo", ""), "feita": False}
    return make_response(201, tasks[tid])


# ── PUT /tasks/* ──────────────────────────

@app.put("/tasks/*")
def update_task(req):
    tid = req["path"].split("/")[-1]
    if tid not in tasks:
        return make_response(404, {"erro": "Tarefa não encontrada"})

    data = json.loads(req["body"])
    tasks[tid] = {"id": tid, **data}
    return make_response(200, tasks[tid])


# ── DELETE /tasks/* ───────────────────────

@app.delete("/tasks/*")
def delete_task(req):
    tid = req["path"].split("/")[-1]
    if tid not in tasks:
        return make_response(404, {"erro": "Tarefa não encontrada"})

    deleted = tasks.pop(tid)
    return make_response(200, {"deletada": deleted})


# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run()