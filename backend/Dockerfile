
FROM python:3.12-slim

# prevent python from writing .pyc files and stop buffering stdout stderr 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy only the requirements file first to optimize the docker's caching system (OverlayFS)
COPY requirements.txt .

# Install CPU-only PyTorch first.
# This prevents pip from pulling the CUDA/NVIDIA PyTorch dependencies.
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]