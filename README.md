# Mockbuster

![tests](https://github.com/quagtus/mockbuster/actions/workflows/tests.yml/badge.svg)

A video rental store  module for **Odoo 17 Community** (*built as a practice project*).
It covers models, security, views, a cron job, a mail template, QWeb PDF reports and a SQL view report.

## Features

- Movies, actors and physical copies (DVD / Blu-ray / VHS)
- Rentals with sequence numbers state flow and chatter
- Search movies by actor, live availability per movie
- Daily cron: email reminder for overdue rentals
- PDF: rental receipt, popularity ranking
- Rental analysis (graph or pivot) on a PostgreSQL view
- Security groups: Clerk, Manager
- Demo data

## Requirements

- Docker with Compose v2
- `make` (optional, shortcuts only)

## Quick start

```bash
git clone https://github.com/quagtus/mockbuster.git
cd mockbuster
cp .env.example .env   # change the passwords
make init              # creates DB "mockbuster", installs the module with demo data
make up
```

| Service | URL | Login |
| --- | --- | --- |
| Odoo | http://localhost:8069 | admin / admin |
| Mailpit (catches all outgoing mail) | http://localhost:8025 | – |

Without make:

```bash
docker compose run --rm odoo odoo -d mockbuster -i mockbuster --stop-after-init
docker compose up -d
```

## Trying the features

- **Overdue reminder:** enable developer mode in Settings, then Technical → Scheduled Actions →
  *Mockbuster: send overdue reminders* → Run Manually. Run *Mail: Email Queue Manager* the same way;
  the email appears in Mailpit.
- **Rental receipt:** open a rental → *Print receipt*.
- **Popular movies:** Mockbuster → Reporting → Popular movies.

## Tests

```bash
make test
```

Installs the module into a throwaway database (`mockbuster_test`), runs the module's tests and drops the database.
GitHub Actions runs the same command on every push and pull request.

## Development

- XML views and QWeb templates reload automatically (`--dev=xml,qweb`).
- After Python or data changes: `make update`.

## Structure

```text
addons/mockbuster/
├── models/      movie, actor, dvd, rental
├── security/    groups, access rights
├── data/        sequence, mail template, cron
├── views/       list/form/search views, menus
├── report/      PDF reports, rental analysis (SQL view)
├── demo/        demo data
└── tests/       unit tests
```

## License

LGPL-3