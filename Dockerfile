FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install --prefer-binary -r requirements.txt
RUN pip3 install -r requirements-test.txt

EXPOSE 5000

ENV FLASK_APP=main
ENV FLASK_ENV=development

CMD ["python", "main.py"]
