.PHONY: install run

install:
	npm install

run:
	lsof -ti:8082 | xargs kill -9
	node app.js
