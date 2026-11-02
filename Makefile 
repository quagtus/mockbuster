include .env
export

RUN = docker compose run --rm odoo odoo

up:
	docker compose up -d

init:        ## create DB and install the module (with demo data)
	$(RUN) -d $(ODOO_DB) -i mockbuster --stop-after-init

update:      ## upgrade module after Python/data changes
	$(RUN) -d $(ODOO_DB) -u mockbuster --stop-after-init
	docker compose restart odoo

test:        ## fresh throwaway DB, run module tests
	docker compose run --rm odoo odoo -d $(ODOO_DB)_test -i mockbuster \
		--test-tags /mockbuster --stop-after-init --log-level=test
	docker compose run --rm odoo dropdb -h db -U $(POSTGRES_USER) --if-exists $(ODOO_DB)_test

logs:
	docker compose logs -f odoo

shell:
	$(RUN) shell -d $(ODOO_DB)

down:
	docker compose down