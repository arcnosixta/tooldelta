# Launch copy and distribution

Public links:

- Live demo: https://arcnosixta.github.io/tooldelta/
- Source: https://github.com/arcnosixta/tooldelta
- Release: https://github.com/arcnosixta/tooldelta/releases/tag/v0.2.0
- Reproducible real case: https://github.com/arcnosixta/tooldelta/tree/main/examples/filesystem

These are **drafts**, not claims that external posts have been sent. Choose a
community that permits project showcases, disclose your relationship to the
project, and stay available to discuss its limitations and implementation.

## Short English post

> ToolDelta compares saved MCP tool catalogs before a server update. In a captured
> Filesystem Server update, read_multiple_files.paths gained minItems: 1 — an empty
> array no longer fits the declared contract. Try the report and your own catalogs
> in your browser: https://arcnosixta.github.io/tooldelta/
>
> Same Python engine in the browser and CLI. Catalog contents stay on your device;
> the browser downloads a pinned Pyodide runtime. The CLI has no runtime dependencies.
> Alpha, with an explicit schema subset. I'd welcome sanitized examples that produce
> noisy or missed findings. Source: https://github.com/arcnosixta/tooldelta

## MCP community showcase

Title: **ToolDelta: compare MCP tool contracts locally before updating servers**

> We're developing ToolDelta, an open-source contract-review tool for saved tools/list
> results. The project was built with a coding assistant, and the real captured
> examples and comparison rules are available to inspect.
>
> It reports changes such as new required arguments, tighter input bounds and wider
> response enums. Input and output comparisons use opposite compatibility directions.
> Description changes, untrusted hints and unsupported JSON Schema semantics stay
> visible as review items.
>
> The demo opens without an account and includes an actual official Filesystem
> Server update, plus local comparison of your own catalogs. No catalog uploads.
>
> Live: https://arcnosixta.github.io/tooldelta/
> Source: https://github.com/arcnosixta/tooldelta
>
> This isn't a full compatibility proof or a security scanner. The most useful
> feedback would be a sanitized pair of real catalogs and a finding you'd change.

## Hacker News candidate

Title: **ToolDelta — offline MCP tool contract diffs with a browser demo**

Use a regular project submission unless the maintainer has personally used the
tool enough to explain it and answer questions. [Show HN guidelines](https://news.ycombinator.com/showhn.html)
ask for personally worked-on, non-trivial projects and exclude quickly generated
one-offs. Do not present assistant-generated work as a long-running established
project or request coordinated votes. A draft does not authorize automatic posting.

## Русский пост

> Сделали ToolDelta — утилиту для проверки изменений MCP-инструментов.
> Реальный пример: в новом каталоге Filesystem Server у read_multiple_files.paths
> появился minItems: 1, поэтому старый вызов с пустым массивом больше не подходит
> под объявленную схему.
>
> Демо без регистрации: https://arcnosixta.github.io/tooldelta/
> Можно сравнить свои JSON-каталоги прямо в браузере; содержимое файлов не
> отправляется на сервер. Python CLI работает офлайн и без runtime-зависимостей.
>
> Это альфа с ограниченным набором проверок, не сертификат безопасности.
> Будем рады обезличенным примерам, где проверка шумит или пропускает изменение.
> Исходники: https://github.com/arcnosixta/tooldelta

## First-week measurements

Measure visits and unique cloners using GitHub Insights, issue quality, submitted
fixtures and actual integrations. Stars are secondary; do not claim that tags,
posts or a release guarantee Trending placement. No analytics is installed in
the browser demo. Track voluntary feedback, not private catalog contents.
