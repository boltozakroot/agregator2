# Ecotechstroy parser

Скрипт собирает дома с `https://ecotechstroy.ru/apiback/cards` и сохраняет поля:
- название
- площадь
- материал
- цена
- этажность
- ссылка на карточку дома

## Запуск

```bash
python run_parser.py --json output/houses.json --csv output/houses.csv
```

## Тесты

```bash
python -m unittest discover -s tests -v
```

## Автодеплой на Ubuntu 24.04 (158.160.168.209)

1. Добавьте в GitHub Secrets:
   - `SSH_PRIVATE_KEY` — приватный ключ для `ubuntu@158.160.168.209`
2. Убедитесь, что у пользователя `ubuntu` есть `sudo` без TTY-block для `systemctl/cp`.
3. Workflow `.github/workflows/deploy.yml`:
   - синхронизирует код в `/opt/ecotech-parser`
   - создает venv
   - устанавливает зависимости
   - обновляет systemd unit/timer
   - перезапускает `ecotech-parser.service`

Для первичной инициализации сервера можно выполнить:

```bash
./deploy/setup_server.sh <repo_url>
```

## Быстрая инструкция для новичков

- См. `docs/DEPLOY_FOR_BEGINNERS.md`
