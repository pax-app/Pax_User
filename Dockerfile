# base image
FROM python:3.8.0-alpine


# set working directory
WORKDIR /app

# Install Dependencies (libffi-dev is necessary for cffi (bcrypt dependency))
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev libffi-dev

# Dealing with requirements
RUN pip install --upgrade pip
RUN pip install Flask-SQLAlchemy
COPY ./requirements.txt /app/requirements.txt
RUN pip	install	-r	requirements.txt


# Coping project
COPY . /app


# run server
CMD ["gunicorn","project:create_app()"]