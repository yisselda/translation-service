# Translation Service

Microservice providing text translation capabilities using Meta's NLLB-200 model.

## Features
- Support for 200+ languages including Haitian Creole
- REST API for translation
- Batch translation support
- Response caching with Redis

## Quick Start

```bash
docker-compose up
```

## API Endpoints

- `POST /api/v1/translate` - Translate text
- `POST /api/v1/translate/batch` - Translate multiple texts
- `GET /api/v1/languages` - Get supported languages

## Development

```bash
pip install -r requirements.txt
python -m app.main
```

## License
MIT
