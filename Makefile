install:
	#install commands
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#format code
	black *.py routers/*.py
lint:
	#pylint or #flake8
	pylint --disable=R,C *.py routers/*.py
test:
	#test
deply:
	#deploy
build:
	#build container
	#docker build -t deploy-books-app .
all: install lint test deploy