FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY transaction_processor /var/task/transaction_processor
WORKDIR /var/task

CMD ["transaction_processor.app.handler"]
