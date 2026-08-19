.PHONY: seed-models dev-ml dev-agent dev-gateway dev-dashboard docker-up docker-down simulate

seed-models:
	bash scripts/seed_models.sh

dev-ml:
	cd services/ml-engine && pip install --break-system-packages -q -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

dev-agent:
	cd services/agent-core && pip install --break-system-packages -q -r requirements.txt && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

dev-gateway:
	cd services/gateway && pip install --break-system-packages -q -r requirements.txt && ML_ENGINE_URL=http://localhost:8001/predict AGENT_CORE_URL=http://localhost:8002/investigate python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-dashboard:
	cd services/dashboard && npm install && npm run dev

docker-up:
	cd deploy && docker compose up --build -d

docker-down:
	cd deploy && docker compose down

simulate:
	python3 scripts/simulate_attacks.py --count 30 --delay 0.4
