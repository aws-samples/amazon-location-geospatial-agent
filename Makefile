build: install test

install:
	poetry install

test:
	poetry run coverage run -m pytest

create-session:
	mkdir -p geospatial-agent-session-storage/$(SESSION_ID)/data
	mkdir -p geospatial-agent-session-storage/$(SESSION_ID)/generated
	cp data/AB_NYC_2019.csv geospatial-agent-session-storage/$(SESSION_ID)/data
