# Firefly III Toolkit API

Backend FastAPI do polautomatycznego matchowania i aktualizowania transakcji BLIK w Firefly III na podstawie plikow CSV z banku. Pozwala wrzucic wyciag, zobaczyc co pasuje do transakcji w Firefly, a nastepnie hurtowo uzupelnic opisy/notatki i oznaczyc transakcje tagiem.

## Status
Internal tool, aktywnie rozwijany (kontenery publikowane na GHCR z galezi `main`). Brak wlasnej bazy danych, stan ulotny.

## Architektura (high-level)
- FastAPI (`src/main.py`) z routerami:
  - `auth`: prosta lista uzytkownikow z `.env`, JWT (Bearer) wydawane przez `/api/auth/token`.
  - `system`: zdrowie i wersja `/api/system/*`.
  - `blik_files`: pipeline CSV -> podglad -> match -> apply.
- CSV ingest: plik zapisywany tymczasowo w `/tmp`, parsowany przez `BankCSVReader` (polski format daty/kwoty).
- Matchowanie: `TransactionProcessor.match` pobiera transakcje z Firefly (przez `fireflyiii-enricher-core`), filtruje opisem `BLIK_DESCRIPTION_FILTER`, odrzuca otagowane `TAG_BLIK_DONE`, wylicza kandydatow.
- Apply: zapis w Firefly — dopisanie szczegolow do opisu/notatek oraz tag `blik_done`. Wyniki matchowania buforowane w pamieci procesu (`MEM_MATCHES`); restart kasuje cache.
- Middleware/obsluga: CORS (konfigurowalne `ALLOWED_ORIGINS`), logowanie do `blik_sync.log` + stdout.
- Infra: obraz z wieloetapowego Dockerfile (uv + slim Python), healthcheck `/api/system/health`. Opcjonalny proxy Nginx (`infra/nginx-firefly.conf`) do przekierowania na instancje Firefly na hoscie.

## Stack technologiczny
- Backend: Python 3.12, FastAPI, Starlette, Pydantic v2, PyJWT, `fireflyiii-enricher-core`.
- Runtime: uvicorn, python-dotenv.
- Tooling: `uv` (package/deps), pytest, black, ruff, isort, mypy, commitizen.
- Infra: Docker, docker-compose, GH Actions (build & publish do GHCR).

## Wymagania
- Python >= 3.12.
- `uv` (https://github.com/astral-sh/uv) lub standardowy `pip`/`venv`.
- Dostep do Firefly III API + personal access token.
- Docker (opcjonalnie, do runtime/produkcji).

## Konfiguracja (.env)
Zacznij od `.env.example` i uzupelnij:
- `FIREFLY_URL` – URL API Firefly (np. `http://firefly:8080`); wymagane przez /statistics, /matches, /apply.
- `FIREFLY_TOKEN` – PAT z Firefly z uprawnieniami do transakcji.
- `USERS` – lista `user:pass` rozdzielona przecinkami (np. `user1:secret,user2:secret`).
- `SECRET_KEY` / `ALGORITHM` / `ACCESS_TOKEN_EXPIRE_MINUTES` – parametry JWT; `SECRET_KEY` musi byc spojny miedzy wydawaniem a walidacja.
- `ALLOWED_ORIGINS` – `*`, CSV (`a,b,c`) lub JSON lista; wykorzystywane w CORS.
- `DEMO_MODE` – flaga (obecnie niewykorzystana w kodzie).
- `BLIK_DESCRIPTION_FILTER` – fragment opisu uzywany do filtrowania transakcji w Firefly.
- `TAG_BLIK_DONE` – tag dodawany po apply.
> Uwaga: w `.env` nie dodawaj spacji wokol `=` (np. `BLIK_DESCRIPTION_FILTER="..."`), aby parsowanie zadzialalo przewidywalnie.

## Szybki start (lokalnie)
```bash
# 1) Zainstaluj zaleznosci
uv sync  # albo: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt (brak pliku? uzyj uv)

# 2) Konfiguracja
cp .env.example .env
# uzupelnij FIREFLY_URL, FIREFLY_TOKEN, USERS, SECRET_KEY itd.

# 3) Uruchom backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4) Smoke-test
curl http://localhost:8000/api/system/health
```
Autoryzacja:
```bash
# token (x-www-form-urlencoded)
curl -X POST http://localhost:8000/api/auth/token \
  -d 'username=user1&password=secret' \
  | jq -r .access_token
# uzywaj w Authorization: Bearer <token>
```
Przykladowy flow BLIK:
1. `POST /api/blik_files` z plikiem CSV (`file` w form-data) -> otrzymasz `id`.
2. `GET /api/blik_files/{id}` – podglad sparsowanych rekordow.
3. `GET /api/blik_files/{id}/matches` – zestawienie dopasowan i statystyki.
4. `POST /api/blik_files/{id}/matches` z `{ "tx_indexes": [<id_csv>, ...] }` dla rekordow, ktore maja dokladnie jeden match.

## Docker
Budowa lokalna:
```bash
docker build -t ff-iii-toolkit-api:local .
docker run --env-file .env -p 8000:8000 ff-iii-toolkit-api:local
```
Compose (backend + proxy do Firefly na hoscie `172.17.0.1:80` – dostosuj IP/port do swojej sieci):
```bash
cd infra
docker compose up -d
```
Zmodyfikuj `infra/nginx-firefly.conf`, jezeli Twoja instancja Firefly sluha gdzie indziej.

## CI/CD
- `.github/workflows/build.yml`: przy pushu do `main` lub tagu `v*` buduje obraz z `Dockerfile` i publikuje do GHCR jako `ghcr.io/<owner>/ff-iii-toolkit-api:{latest,sha,tag}`.
- Brak testow w pipeline; uruchamiaj lokalnie (`uv run pytest`) przed publikacja.

## Struktura repo
- `src/main.py` – uruchomienie FastAPI, rejestracja routerow/middleware.
- `src/api/routers/` – `auth`, `blik_files`, `system`.
- `src/api/models/` – Pydantic modele odpowiedzi/payloadow.
- `src/services/` – CSV parser, auth util, procesor transakcji + match/apply.
- `src/utils/` – logger, base64url helpery.
- `infra/` – `docker-compose.yml`, `nginx-firefly.conf`.
- `Dockerfile` – multi-stage build na `uv`.
- `makefile` – skroty (`make dev`, `make test`).
- `tests/` – testy `SimplifiedRecord.pretty_print`.

## Najczestsze problemy / troubleshooting
- 500 "Config error" na /statistics /matches /apply – brak `FIREFLY_URL` lub `FIREFLY_TOKEN`; uzupelnij `.env`.
- 401 po zalogowaniu – `SECRET_KEY`/`ALGORITHM` w srodowisku uruchomieniowym rozni sie od tego, na ktorym wydano token; ustaw spojnie i zrestartuj.
- Brak dopasowan – sprawdz, czy `BLIK_DESCRIPTION_FILTER` odpowiada opisom w Firefly i czy transakcje nie maja juz tagu `TAG_BLIK_DONE`.
- "No match data found" przy apply – cache `MEM_MATCHES` jest w pamieci procesu; po restarcie musisz ponownie wywolac `/matches`.
- CORS blokuje frontend – ustaw `ALLOWED_ORIGINS` na poprawny CSV/JSON lub `*` w `.env`.
- Pliki CSV nie znajduja sie – endpointy operuja na `/tmp/<id>.csv`; czyszczenie `/tmp` lub restart usuwa mozliwosc podgladu/apply.

## Debugowanie / rozwoj
- Logi: stdout + `blik_sync.log` w katalogu roboczym.
- Testy: `uv run pytest` lub `make test`.
- Lint/format (lokalnie, opcjonalnie): `uv run ruff check`, `uv run black .`, `uv run mypy`.

## Deployment (prod)
- Uzyj obrazu z GHCR (`ghcr.io/<owner>/ff-iii-toolkit-api:latest` lub konkretny tag). Wymagane podanie `.env`.
- Zapewnij dostep z kontenera do instancji Firefly (domyslnie healthcheck nasluchuje na `:8000`, proxy z `infra` zaklada Firefly na `172.17.0.1:80` – dostosuj do swojej sieci).
