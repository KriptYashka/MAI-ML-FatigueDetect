# Система Определения Усталости Пилотов

ML-сервис для определения усталости пилотов авиации по двум типам данных:
- **Изображения** - CNN-классификация лиц на признаки усталости
- **Tabular данные** - классификация по поведенческим параметрам

## Архитектура системы

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Клиент    │────▶│  FastAPI Server │────▶│   ML Models     │
│  (Браузер)  │     │    (Port 8000)  │     │                 │
└─────────────┘     └────────┬────────┘     └─────────────────┘
                             │
                    ┌────────▼────────┐
                    │    InfluxDB     │
                    │  (Time-Series)  │
                    └─────────────────┘
```

## Структура проекта

```
MAI_AI/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI ML сервер
│   ├── client/
│   │   ├── main.py              # Web-интерфейс (пилоты)
│   │   └── api_client.py        # Python API клиент
│   ├── models/
│   │   ├── train_model.py       # Обучение CNN
│   │   ├── predictor.py         # CNN классификатор
│   │   ├── train_human_model.py # Обучение tabular модели
│   │   └── human_predictor.py   # Tabular классификатор
│   ├── data/
│   │   ├── prepare_data.py       # Подготовка изображений
│   │   └── prepare_human_data.py # Подготовка tabular данных
│   └── services/
│       └── influxdb_service.py  # InfluxDB клиент
├── models/                       # Обученные модели
├── requirements.txt
└── README.md
```

## Контекст применения

Система разработана для **авиации** и интегрируется в:
- Предполётный медицинский контроль
- CRM (Crew Resource Management)
- Систему управления безопасностью (SMS)
- Мониторинг экипажа в рейсе

## Уровни усталости

| Уровень | Описание | Рекомендуемый отдых | Действия |
|---------|----------|---------------------|----------|
| **Высокая** (High) | Критическая усталость | 12-14 часов | Отстранение от полёта |
| **Умеренная** (Moderate) | Повышенная усталость | 8-10 часов | Ограничение сложности рейса |
| **Низкая** (Low) | Норма | Обычный | Стандартные процедуры |

## Датасеты

### 1. Face Fatigue Dataset (Изображения)
- **Источник:** Kaggle (rihabkaci99/fatigue-dataset)
- **Объём:** 2200 изображений (1100 усталых + 1100 бодрствующих)
- **Формат:** JPG изображения лиц
- **Точность модели:** 88.64%

### 2. Human Decision Fatigue Dataset (Tabular)
- **Источник:** Kaggle (sonalshinde123/human-decision-fatigue-behavioral-dataset)
- **Объём:** 25,000 записей
- **Признаки:** 9 параметров
- **Точность модели:** 97.82%

### Параметры для анализа

| Параметр | Описание | Диапазон | Важность для пилотов |
|----------|----------|----------|---------------------|
| Hours_Awake | Часы бодрствования | 0-48 | &#x2B50;&#x2B50;&#x2B50;&#x2B50;&#x2B50; |
| Decisions_Made | Принято решений | 0-∞ | &#x2B50;&#x2B50;&#x2B50;&#x2B50; |
| Task_Switches | Переключения задач | 0-∞ | &#x2B50;&#x2B50;&#x2B50; |
| Avg_Decision_Time_sec | Время решения (сек) | 0-∞ | &#x2B50;&#x2B50;&#x2B50; |
| Sleep_Hours_Last_Night | Сон прошлой ночью | 0-24 | &#x2B50;&#x2B50;&#x2B50;&#x2B50;&#x2B50; |
| Caffeine_Intake_Cups | Кофеин (чашки) | 0-∞ | &#x2B50;&#x2B50; |
| Stress_Level_1_10 | Уровень стресса | 1-10 | &#x2B50;&#x2B50;&#x2B50; |
| Error_Rate | Частота ошибок | 0-1 | &#x2B50;&#x2B50;&#x2B50;&#x2B50; |
| Cognitive_Load_Score | Когнитивная нагрузка | 0-1 | &#x2B50;&#x2B50;&#x2B50; |

## Запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Обучение моделей
```bash
# CNN для изображений
python -m src.models.train_model

# Tabular модель
python -m src.models.train_human_model
```

### Запуск сервисов
```bash
# ML сервер (порт 8000)
uvicorn src.api.main:app --reload --port 8000

# Web-клиент (порт 8001)
uvicorn src.client.main:app --reload --port 8001
```

### Доступ
- **Web-интерфейс:** http://localhost:8001
- **Документация API:** http://localhost:8000/docs

## Регламенты

Система учитывает следующие авиационные ограничения:

| Параметр | Дневной лимит | Недельный лимит |
|----------|---------------|-----------------|
| Часы полёта | 8-10 часов | 60 часов |
| Часы бодрствования | 14-16 часов | - |
| Минимальный сон | 10 часов (между сменами) | - |

## API Endpoints

### ML Server (порт 8000)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка статуса |
| POST | `/predict/image` | Анализ изображения лица |
| POST | `/predict/tabular` | Анализ tabular данных |
| POST | `/predict/batch/tabular` | Batch анализ |

## Примеры использования

### Python клиент
```python
from src.client.api_client import FatigueClient

client = FatigueClient(server_url="http://localhost:8000")

# Анализ данных пилота
result = client.predict_tabular({
    "Hours_Awake": 10,
    "Decisions_Made": 45,
    "Task_Switches": 8,
    "Avg_Decision_Time_sec": 3.0,
    "Sleep_Hours_Last_Night": 5.5,
    "Caffeine_Intake_Cups": 3,
    "Stress_Level_1_10": 7.0,
    "Error_Rate": 0.12,
    "Cognitive_Load_Score": 0.7
})

print(f"Уровень усталости: {result['prediction']}")
```

### curl
```bash
curl -X POST http://localhost:8000/predict/tabular \
  -H "Content-Type: application/json" \
  -d '{
    "Hours_Awake": 10,
    "Decisions_Made": 45,
    "Task_Switches": 8,
    "Avg_Decision_Time_sec": 3.0,
    "Sleep_Hours_Last_Night": 5.5,
    "Caffeine_Intake_Cups": 3,
    "Stress_Level_1_10": 7.0,
    "Error_Rate": 0.12,
    "Cognitive_Load_Score": 0.7
  }'
```

## InfluxDB интеграция

Сервис подключается к InfluxDB для:
- Хранения истории измерений усталости экипажа
- Временных рядов метрик
- Анализа трендов усталости
- Отчётности для руководства

Настройка через переменные окружения:
```bash
export INFLUXDB_URL=http://localhost:8086
export INFLUXDB_TOKEN=your-token
export INFLUXDB_ORG=your-org
export INFLUXDB_BUCKET=fatigue-data
```

## Безопасность

- Система является **вспомогательным инструментом**
- Не заменяет медицинский осмотр
- Окончательное решение о допуске - прерогатива медицинского персонала
- Все данные логируются для аудита
