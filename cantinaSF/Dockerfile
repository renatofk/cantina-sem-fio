FROM python:3.12-slim-bookworm

# Add user
RUN useradd wagtail

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip install --upgrade pip
RUN pip install "gunicorn==20.0.4"

# Set working directory
WORKDIR /app

# Copy project files and install requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy remaining project files
COPY . /app

# Run migrations
RUN python manage.py migrate --noinput

# Run collectstatic as root (to ensure all libs are accessible)
RUN python manage.py collectstatic --noinput --clear

# Set ownership after static collected
RUN chown -R wagtail:wagtail /app

# Switch to wagtail user for runtime
USER wagtail

# CMD in JSON form (to avoid signal issues)
CMD ["gunicorn", "cantinasf.wsgi:application", "--bind", "0.0.0.0:8000"]
