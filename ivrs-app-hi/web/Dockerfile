# start by pulling the python image
FROM python:3.8

# switch working directory
WORKDIR /app

#RUN apk --update --upgrade add --no-cache gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
RUN python -m pip install --upgrade pip
# copy the requirements file into the image
COPY ./requirements.txt requirements.txt


# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

#EXPOSE 5000
EXPOSE 7007
# copy every content from the local file to the image
COPY . .
# configure the container to run in an executed manner
#ENTRYPOINT [ "python" ]
CMD ["python", "app.py" ]