FROM python:2.7

RUN pip install pyyaml gitpython docker bottle
RUN pip install jinja2

ADD . /code
WORKDIR /code

EXPOSE 8909

CMD ["python", "/code/post_script.py"]
