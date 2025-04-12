FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && dnf update -y \
    && dnf install -y gcc \
    && dnf clean all

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader -d ./nltk_data punkt_tab \
    && rm -f ./nltk_data/tokenizers/punkt_tab.zip

COPY haystack_utilities ./haystack_utilities
COPY lambda_function.py .

CMD [ "lambda_function.lambda_handler" ]