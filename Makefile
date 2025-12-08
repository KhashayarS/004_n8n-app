install:
	#install commands
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#format code
	black *.py
lint:
	#pylint or #flake8
	pylint --disable=R,C *.py
test:
	#test
deply:
	#deploy
all: install lint test deploy