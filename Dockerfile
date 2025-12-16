FROM python:3.13.11-slim-trixie

RUN mkdir -p /app
COPY . main.py /app/
WORKDIR /app/
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "main.py" ]
ENTRYPOINT [ "python" ]