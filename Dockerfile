FROM python:3.15-alpine@sha256:2699b90f4d562a22e2dd076c82f964032f64814204bff36d271a54ba4cc2c7e2
# Hue2Lox uses only the standard library. Remove unused package tooling and
# ensurepip's bundled wheels instead of shipping vulnerable vendored libraries.
RUN python -m pip uninstall --yes pip \
    && python -c "import pathlib, shutil, sysconfig; shutil.rmtree(pathlib.Path(sysconfig.get_path('stdlib')) / 'ensurepip')"
WORKDIR /app/src
COPY LICENSE NOTICE THIRD-PARTY-NOTICES.md /app/
COPY src/ /app/src/
COPY install/release-image.json /app/install/release-image.json
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
