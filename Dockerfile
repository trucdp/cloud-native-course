FROM python:3.8
LABEL maintainer="Truc Dang Pham"

COPY ./project/techtrends /app
WORKDIR /app

#install dependences and init DB
RUN pip install -r requirements.txt
RUN python init_db.py

#Expose port 3111
EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py"]