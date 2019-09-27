# base image
FROM python:3.6.5-alpine


# set working directory
WORKDIR /app

# Install Dependencies (libffi-dev is necessary for cffi (bcrypt dependency))
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev libffi-dev


# Dealing with requirements (pip upgrade is necessary for bcrypt)
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip	install	-r	requirements.txt


# Coping project
COPY . /app


# run server
CMD python manage.py run -h 0.0.0.0