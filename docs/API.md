API de Marés — Salinópolis

Base URL
- Local: http://127.0.0.1:8000/api/
- Produção: https://www.maresdesalinas.com.br/api/

Recursos
- TideDay (dias) — leitura
  - GET /api/tidedays/ — lista dias com marés (paginado)
  - GET /api/tidedays/?date=YYYY-MM-DD — filtra por data específica
  - GET /api/tidedays/?start=YYYY-MM-DD&end=YYYY-MM-DD — intervalo de datas
  - GET /api/tidedays/{id}/ — detalhe de um dia

- Tide (marés) — leitura e escrita
  - GET /api/tides/ — lista marés (paginado)
  - GET /api/tides/?date=YYYY-MM-DD — filtra por data do dia
  - POST /api/tides/ — cria/atualiza maré para um dia
  - GET /api/tides/{id}/ — detalhe
  - PUT/PATCH /api/tides/{id}/ — atualiza
  - DELETE /api/tides/{id}/ — remove

Modelos
- TideDay
  - id: integer
  - date: string (YYYY-MM-DD)
  - weekday: string (opcional)
  - tides: array[Tide]

- Tide
  - id: integer
  - order: integer (1..4)
  - time: string (HH:MM[:SS])
  - height: number (ex.: 4.61)
  - date: string (YYYY-MM-DD) — data do dia (write-only)
  - weekday: string — rótulo opcional do dia (write-only)

Exemplos
- Listar marés de um dia
  curl "http://127.0.0.1:8000/api/tidedays/?date=2025-01-12"

- Criar uma maré (MARE1)
  curl -X POST http://127.0.0.1:8000/api/tides/ \
    -H "Content-Type: application/json" \
    -d '{
          "order": 1,
          "time": "06:27",
          "height": 4.55,
          "date": "2025-01-12",
          "weekday": "DOM"
        }'

- Atualizar uma maré (por id)
  curl -X PATCH http://127.0.0.1:8000/api/tides/123/ \
    -H "Content-Type: application/json" \
    -d '{"height": 4.60}'

Observações
- A criação de maré via POST cria/atualiza o registro de Tide para o (date, order) informado. Se o TideDay (date) não existir, ele é criado.
- Autenticação: atualmente os endpoints são públicos. Em produção, recomenda-se adicionar autenticação (token/Session/OAuth) antes de permitir escrita.
- Paginação: endpoints de lista são paginados (PAGE_SIZE=50). Use os links next/previous no JSON.

