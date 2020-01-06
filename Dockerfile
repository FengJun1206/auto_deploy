FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY BackDB/requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt -i https://pypi.douban.com/simple
COPY . /code/

EXPOSE 5000 5001

CMD ["/usr/local/bin/gunicorn", "--chdir", "BackDB", "-w", "4", "-b", ":5000", "app:app"]
