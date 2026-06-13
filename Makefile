install:
	pip install -r requirements.txt

run:
	PORT=47375 bash ./start.sh

test:
	pytest tests/ -v --tb=short

seed:
	python seed.py
