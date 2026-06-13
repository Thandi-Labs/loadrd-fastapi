# ---- Base ----
    FROM python:3.14.6-slim AS base
    WORKDIR /app
    
    # ---- Builder ----
    FROM base AS builder
    COPY requirements.txt .
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # ---- Final ----
    FROM base AS final
    
    # Copy installed dependencies from builder
    COPY --from=builder /install /usr/local
    
    # Create non-root user
    RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
    
    # Copy application code
    COPY . .
    
    # Ensure .env is not copied (use secrets/env vars at runtime)
    RUN rm -f .env
    
    # Set ownership
    RUN chown -R appuser:appgroup /app
    
    USER appuser
    
    EXPOSE 8000
    
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]