# HTTP-server

# Exemplo
python app.py

## criar
curl -s -X POST http://localhost:8080/tasks \
     -d '{"titulo":"Estudar sockets"}' | python -m json.tool

## listar
curl -s http://localhost:8080/tasks | python -m json.tool

## buscar por id
curl -s http://localhost:8080/tasks/1 | python -m json.tool

## atualizar
curl -s -X PUT http://localhost:8080/tasks/1 \
     -d '{"titulo":"Estudar sockets","feita":true}' | python -m json.tool

## deletar
curl -s -X DELETE http://localhost:8080/tasks/1 | python -m json.tool