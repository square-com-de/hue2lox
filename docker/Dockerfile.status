FROM python:3.12-alpine
WORKDIR /app/src
COPY LICENSE NOTICE THIRD-PARTY-NOTICES.md /app/
COPY src/ /app/src/
ARG REGISTRY_SOURCE=config/registry.json
COPY ${REGISTRY_SOURCE} /app/config/registry.json
COPY web/ /app/web/
COPY catalog/ /app/catalog/
COPY trust/huebridge-ca.pem /app/trust/huebridge-ca.pem
COPY docker/entrypoint.py /app/entrypoint.py
# App state (credentials, control token, bridge registry) lives in one volume. Plain HTTP by default; set TLS_CERT/TLS_KEY for built-in HTTPS.
RUN mkdir /data && chown 10001:10001 /data
VOLUME /data
USER 10001:10001
EXPOSE 8443
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import os,ssl,urllib.request as u; t=os.environ.get('TLS_CERT'); r=u.urlopen(('https' if t else 'http')+'://127.0.0.1:'+os.environ.get('PORT','8443')+'/health',context=ssl.create_default_context(cafile=t) if t else None,timeout=3); assert r.status==200"]
ENTRYPOINT ["python", "-u", "/app/entrypoint.py"]
