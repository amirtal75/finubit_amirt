FROM python:3.9
WORKDIR /app
COPY load_tester.py /app/
RUN pip install requests prometheus_client
EXPOSE 5003

CMD ["python", "load_tester.py"]
