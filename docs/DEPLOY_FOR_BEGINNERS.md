# Деплой для чайников: Ecotech Parser на Ubuntu 24.04

Ниже — очень простая инструкция, как запустить автодеплой на сервер `158.160.168.209`.

---

## Что вы получите

После настройки:
- код будет автоматически выкатываться с GitHub на сервер;
- парсер будет запускаться по таймеру каждые 6 часов;
- результаты будут лежать на сервере в:
  - `/opt/ecotech-parser/output/houses.json`
  - `/opt/ecotech-parser/output/houses.csv`

---

## Что нужно заранее

1. Репозиторий на GitHub (куда уже запушен этот проект).
2. Доступ по SSH к серверу:
   - хост: `158.160.168.209`
   - пользователь: `ubuntu`
3. Локально установлен `ssh` (обычно уже есть на Linux/macOS; на Windows — через Git Bash/PowerShell).

---

## Шаг 1. Сгенерировать SSH-ключ для GitHub Actions

На вашем компьютере выполните:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/ecotech_deploy_key
```

Просто нажимайте Enter (можно без passphrase).

Появятся 2 файла:
- `~/.ssh/ecotech_deploy_key` (приватный)
- `~/.ssh/ecotech_deploy_key.pub` (публичный)

---

## Шаг 2. Добавить публичный ключ на сервер

Скопируйте ключ на сервер:

```bash
ssh-copy-id -i ~/.ssh/ecotech_deploy_key.pub ubuntu@158.160.168.209
```

Если `ssh-copy-id` нет, тогда вручную:

```bash
cat ~/.ssh/ecotech_deploy_key.pub
```

Скопируйте вывод, затем зайдите на сервер и добавьте в файл `~/.ssh/authorized_keys`.

---

## Шаг 3. Проверить вход по ключу

```bash
ssh -i ~/.ssh/ecotech_deploy_key ubuntu@158.160.168.209
```

Если вы вошли без пароля — всё ок.

---

## Шаг 4. Добавить приватный ключ в GitHub Secrets

1. Откройте GitHub репозиторий.
2. Перейдите: **Settings -> Secrets and variables -> Actions**.
3. Нажмите **New repository secret**.
4. Имя: `SSH_PRIVATE_KEY`
5. Значение: содержимое файла `~/.ssh/ecotech_deploy_key`

Команда, чтобы скопировать ключ:

```bash
cat ~/.ssh/ecotech_deploy_key
```

---

## Шаг 5. Первый деплой

Есть 2 варианта.

### Вариант A (рекомендуется): через GitHub Actions

Сделайте коммит в `main` (или вручную запустите workflow `Deploy parser to server`).

Workflow находится в:
- `.github/workflows/deploy.yml`

Что делает workflow:
1. Подключается к серверу по SSH.
2. Копирует проект в `/opt/ecotech-parser`.
3. Создает `.venv`.
4. Ставит зависимости.
5. Обновляет `systemd` unit/timer.
6. Запускает сервис.

### Вариант B: руками на сервере (первичная инициализация)

На сервере:

```bash
cd /opt
sudo git clone <ВАШ_GIT_URL> ecotech-parser
cd ecotech-parser
./deploy/setup_server.sh <ВАШ_GIT_URL>
```

---

## Шаг 6. Проверить, что всё работает

На сервере выполните:

```bash
systemctl status ecotech-parser.timer --no-pager
systemctl status ecotech-parser.service --no-pager
```

Проверить последний лог запуска:

```bash
journalctl -u ecotech-parser.service -n 100 --no-pager
```

Проверить файлы результата:

```bash
ls -lah /opt/ecotech-parser/output/
```

---

## Если что-то не работает

### Ошибка `Permission denied (publickey)`
Сделайте по порядку:

1. Проверьте, что **публичная часть** вашего deploy-ключа реально лежит на сервере:
   ```bash
   ssh ubuntu@158.160.168.209 "cat ~/.ssh/authorized_keys"
   ```
2. Если ключа нет — добавьте:
   ```bash
   ssh-copy-id -i ~/.ssh/ecotech_deploy_key.pub ubuntu@158.160.168.209
   ```
3. Проверьте вход этим же ключом локально:
   ```bash
   ssh -i ~/.ssh/ecotech_deploy_key ubuntu@158.160.168.209
   ```
4. В GitHub Secret `SSH_PRIVATE_KEY` вставьте **точно содержимое** `~/.ssh/ecotech_deploy_key` (приватный ключ, вместе с BEGIN/END строками).
5. Если раньше использовали другой ключ — удалите старый из `authorized_keys` и добавьте новый.

### Ошибка sudo/systemctl в workflow
- У пользователя `ubuntu` должны быть права на `sudo cp`, `sudo systemctl`

### Файлы не появляются в `output/`
- Проверьте логи:
  ```bash
  journalctl -u ecotech-parser.service -n 200 --no-pager
  ```

---

## Как обновлять проект дальше

Просто делаете push в `main`.

GitHub Actions сам задеплоит изменения на сервер `158.160.168.209`.
