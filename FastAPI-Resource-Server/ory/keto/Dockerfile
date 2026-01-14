FROM oryd/keto:latest

COPY keto-config.yml /home/ory/keto.yml
COPY scopes_roles_permissions.json /home/ory/scopes_roles_permissions.json
COPY load-permissions.sh /home/ory/load-permissions.sh
COPY entry_point.sh /home/ory/entry_point.sh

RUN chmod +x /home/ory/*.sh

EXPOSE 4466 4467

ENTRYPOINT ["/home/ory/entry_point.sh"]