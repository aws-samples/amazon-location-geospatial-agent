build: install test

install:
	poetry install

test:
	poetry run coverage run -m pytest

create-session:
	mkdir -p geospatial-agent-session-storage/$(SESSION_ID)/data
	mkdir -p geospatial-agent-session-storage/$(SESSION_ID)/generated
	cp data/$(FILE_NAME) geospatial-agent-session-storage/$(SESSION_ID)/data
