# Быстрый старт

## Запуск системы

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск серверов

**Терминал 1 - ML сервер (порт 8000):**
```bash
uvicorn src.api.main:app --reload --port 8000
```

**Терминал 2 - Web-интерфейс (порт 8001):**
```bash
uvicorn src.client.main:app --reload --port 8001
```

### 3. Использование

Откройте в браузере: **http://localhost:8001**

---

## Web-интерфейс

### Анализ изображений

1. Перейдите в раздел "Анализ изображений"
2. Загрузите фотографию лица пилота
3. Нажмите "Анализировать изображение"
4. Получите результат с рекомендациями

### Ввод данных пилота

1. Заполните параметры в форме:
   - Часы бодрствования
   - Часы сна
   - Количество принятых решений
   - И др.

2. Нажмите "Провести анализ усталости"
3. Получите:
   - Уровень усталости (Высокая/Умеренная/Низкая)
   - Рекомендуемое время отдыха
   - Конкретные действия

---

## API запросы

### Python

```python
from src.client.api_client import FatigueClient

client = FatigueClient()

# Анализ данных пилота
result = client.predict_tabular({
    "Hours_Awake": 12,
    "Decisions_Made": 55,
    "Task_Switches": 10,
    "Avg_Decision_Time_sec": 3.5,
    "Sleep_Hours_Last_Night": 5.0,
    "Caffeine_Intake_Cups": 3,
    "Stress_Level_1_10": 7.0,
    "Error_Rate": 0.15,
    "Cognitive_Load_Score": 0.8
})

print(f"Уровень усталости: {result['prediction']}")
print(f"Уверенность: {result['confidence']:.1%}")
```

### curl

```bash
curl -X POST http://localhost:8000/predict/tabular \
  -H "Content-Type: application/json" \
  -d '{
    "Hours_Awake": 12,
    "Decisions_Made": 55,
    "Task_Switches": 10,
    "Avg_Decision_Time_sec": 3.5,
    "Sleep_Hours_Last_Night": 5.0,
    "Caffeine_Intake_Cups": 3,
    "Stress_Level_1_10": 7.0,
    "Error_Rate": 0.15,
    "Cognitive_Load_Score": 0.8
  }'
```

---

## Переобучение моделей

### Tabular модель
```bash
python -m src.models.train_human_model
```

### CNN модель
```bash
python -m src.models.train_model
```

---

## Уровни усталости и рекомендации

### Высокая усталость
| Параметр | Значение |
|----------|----------|
| Отдых | 12-14 часов |
| Действие | Отстранение от полёта |

### Умеренная усталость
| Параметр | Значение |
|----------|----------|
| Отдых | 8-10 часов |
| Действие | Ограничение сложности рейса |

### Низкая усталость
| Параметр | Значение |
|----------|----------|
| Отдых | Обычный |
| Действие | Стандартные процедуры |

---

## Решение проблем

### "Сервер недоступен"
- Убедитесь что ML сервер запущен на порту 8000
- Перезапустите сервер: `Ctrl+C` → `uvicorn src.api.main:app --reload --port 8000`

### "Ошибка анализа"
- Проверьте введённые данные
- Убедитесь что значения в допустимых диапазонах
- Обновите страницу и попробуйте снова

### Низкая точность предсказаний
- Переобучите модель: `python -m src.models.train_human_model`

---

## Переменные окружения

```bash
# InfluxDB
export INFLUXDB_URL=http://localhost:8086
export INFLUXDB_TOKEN=your-token
export INFLUXDB_ORG=your-org
export INFLUXDB_BUCKET=fatigue-data

# URL сервера для клиента
export SERVER_URL=http://localhost:8000
```

---

## Контакты для поддержки

При возникновении проблем обращайтесь к руководству или в IT-отдел авиакомпании.
