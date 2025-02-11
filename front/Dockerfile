FROM python:3.9
WORKDIR /app
COPY server.py /app/
RUN pip install flask requests prometheus_client
EXPOSE 5002
CMD ["python", "server.py"]
