# stock-analysis-system

Automated daily multi-market data collection and report push pipeline.

## Run

```bash
cd /Users/michaelzhao/agents/stock1
source .venv/bin/activate
python main.py
```

## Configuration

Config priority:
1. Environment variables / `.env`
2. `config/local.yaml`
3. Built-in defaults

Create local config from template:

```bash
cp config/local.yaml.example config/local.yaml
```

Then fill in:
- `notion.token`
- `notion.page_id`
- `telegram.bot_token`
- `telegram.chat_id`

## Project Structure

- `main.py`: compatibility entrypoint
- `src/app.py`: runtime orchestration
- `src/data/fetcher.py`: data collection and report assembly
- `src/execution/notion.py`: Notion delivery
- `src/execution/telegram.py`: Telegram delivery
- `config.py`: config loading logic
- `scripts/run.sh`: shell runner
- `old_version_2026-02-12/`: archived legacy/unused files

## Notes

- Market data runs in a temporary directory now, so no `market_data_YYYY-MM-DD` folders are created under project root.
- `config/local.yaml` is ignored by git to protect secrets.
