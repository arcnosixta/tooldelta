# План первого публичного выпуска

Репозиторий опубликован: [arcnosixta/tooldelta](https://github.com/arcnosixta/tooldelta).
Ветка main сохраняет отдельные коммиты разработки с подробными русскими описаниями.
GitHub Actions запущен после отправки истории. PyPI-пакет и GitHub release пока
не опубликованы. Ниже сохранён план выпуска; создание репозитория уже выполнено.

1. Проверить имя ToolDelta на GitHub/PyPI перед выпуском. При конфликте выбрать
   другое имя и последовательно изменить пакет, CLI и документацию.
2. Создать публичный репозиторий, настроить remote и отправить main.
   Рекомендуемое описание: «Offline MCP contract diffs. Catch breaking tool
   changes before your agents do. Zero runtime dependencies.»
3. Использовать topics `mcp`, `json-schema`, `ai-agents`, `developer-tools`,
   `compatibility`, `python`, `offline`, `cli`. Включить private vulnerability reporting.
4. Дождаться первого GitHub Actions и исправить реальные проблемы совместимости.
   Локальная проверка Windows не заменяет CI на macOS/Linux.
5. Создать release 0.1.0 с wheel/sdist, changelog и явно обозначенным статусом alpha.
   Не публиковать пакет под чужим занятым именем.
6. Подготовить короткую запись экрана: demo → required workspace_id → enum output →
   hints read_file → экспорт отчёта. Длительность до 30–45 секунд.
7. После отдельного согласования опубликовать пост в подходящем MCP-сообществе
   или Show HN. Не создавать искусственные звёзды и не обещать полную безопасность.
8. Попросить первые 5–10 команд прислать обезличенные примеры контрактов.
   Приоритизировать баги и уменьшение шума по этим примерам.

Черновик поста на английском:

> I built ToolDelta, an offline diff for saved MCP tool catalogs. It catches
> changes like newly required parameters, tighter input limits, and wider response
> enums, then explains what callers need to review. It also highlights changed
> descriptions and untrusted capability hints. No server execution or API keys;
> standard-library Python, text/JSON/Markdown/HTML reports. It's an alpha with an
> explicit JSON Schema subset, not a full compatibility proof or security scanner.
> I'd especially welcome sanitized catalogs that produce noisy or missing findings.

Вставить ссылку на реальный репозиторий после публикации. Никакие сообщения
от имени пользователя не отправлены.
