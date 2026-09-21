# Ops Doctor — preflight для слабого Windows-хоста

Перед тяжёлым agency / compute_burst / nervous: один вызов решает,
можно ли стартовать.

## Двухслойный gate

1. **Hard BLOCK** — мало свободной RAM/диска или CPU в потолок (сейчас).
2. **SOFT_WARN** — CPU повышен *или* Echo видит странную **форму**
   CPU/RAM на скользящем окне истории (не один сэмпл).
3. **ALLOW** — иначе.

Echo не заменён порогами и не командует в одиночку: форма — второй слой.

## Установка

Сначала Echo (локально), потом Ops Doctor:

```bash
pip install -e D:\projects\echo
pip install -e "D:\projects\ops_doctor.[dev]"
```

Сэмплы по умолчанию: `%USERPROFILE%\.ops_doctor\samples.jsonl`
(override: `OPS_DOCTOR_STORE`).

## MCP (Cursor)

```json
{
  "ops_doctor": {
    "command": "C:\\Python314\\python.exe",
    "args": ["-m", "ops_doctor.presentation.mcp_server"],
    "env": {
      "OPS_DOCTOR_STORE": "C:\\Users\\YOU\\.ops_doctor\\samples.jsonl"
    }
  }
}
```

## Tools

| Tool | Назначение |
|---|---|
| `host_preflight(heavy=false)` | Сэмпл сейчас + hard/soft вердикт |
| `host_status()` | То же, `heavy=false` |

`heavy=true` — жёстче пол RAM/диска/CPU для burst.

## Тесты

```bash
.\make.ps1
```

## Потолок

Не планировщик задач и не полный observability-стек. История короткая
(~288 точек). Matrix Profile — O(n²m); окно shape по умолчанию малое.

## Лицензия

MIT
