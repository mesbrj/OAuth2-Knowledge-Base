FROM oryd/hydra:latest

ENV DSN = memory
ENV URLS_SELF_ISSUER = http://localhost:4444
ENV URLS_LOGIN = http://localhost:3000/login
ENV URLS_CONSENT = http://localhost:3000/consent
#ENV SECRETS_SYSTEM = youReallyNeedToChangeThis
ENV LOG_LEVEL = debug

EXPOSE 4444 4445

CMD ["serve", "all", "--dev"]