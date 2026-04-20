"""
Python клиент для системы определения усталости пилотов

Примеры использования:
    from src.client.api_client import FatigueClient
    
    client = FatigueClient()
    
    # Анализ данных пилота
    result = client.predict_tabular({
        "Hours_Awake": 10,
        "Decisions_Made": 45,
        "Task_Switches": 8,
        ...
    })
"""

import requests
import os
from typing import Dict, List

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")


class FatigueClient:
    """
    Клиент для взаимодействия с сервером определения усталости пилотов.
    
    Attributes:
        server_url: URL ML сервера
    """
    
    def __init__(self, server_url: str = SERVER_URL):
        self.server_url = server_url.rstrip('/')
        
    def check_connection(self) -> bool:
        """Проверка подключения к серверу."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def predict_from_image(self, image_path: str) -> Dict:
        """
        Анализ изображения лица пилота.
        
        Args:
            image_path: Путь к файлу изображения
            
        Returns:
            Dict с ключами: prediction, confidence, class_id
        """
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.server_url}/predict/image", files=files, timeout=60)
        response.raise_for_status()
        return response.json()
    
    def predict_from_url(self, image_url: str) -> Dict:
        """
        Анализ изображения по URL.
        
        Args:
            image_url: URL изображения
            
        Returns:
            Dict с ключами: prediction, confidence, class_id
        """
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        files = {'file': ('image.jpg', response.content, 'image/jpeg')}
        response = requests.post(f"{self.server_url}/predict/image", files=files, timeout=60)
        response.raise_for_status()
        return response.json()
    
    def predict_tabular(self, data: Dict) -> Dict:
        """
        Анализ tabular данных пилота.
        
        Args:
            data: Словарь с параметрами:
                - Hours_Awake: Часы бодрствования
                - Decisions_Made: Принято решений
                - Task_Switches: Переключения задач
                - Avg_Decision_Time_sec: Среднее время решения
                - Sleep_Hours_Last_Night: Сон прошлой ночью
                - Caffeine_Intake_Cups: Потребление кофеина
                - Stress_Level_1_10: Уровень стресса
                - Error_Rate: Частота ошибок
                - Cognitive_Load_Score: Когнитивная нагрузка
                
        Returns:
            Dict с ключами: prediction, probabilities, confidence
        """
        response = requests.post(
            f"{self.server_url}/predict/tabular",
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def predict_batch_tabular(self, data_list: List[Dict]) -> Dict:
        """
        Batch анализ tabular данных.
        
        Args:
            data_list: Список словарей с параметрами
            
        Returns:
            Dict с ключами: results, total
        """
        response = requests.post(
            f"{self.server_url}/predict/batch/tabular",
            json=data_list,
            timeout=120
        )
        response.raise_for_status()
        return response.json()


def demo():
    """
    Демонстрация использования клиента.
    """
    client = FatigueClient()
    
    print("=" * 60)
    print("  Система определения усталости пилотов")
    print("=" * 60)
    
    print(f"\nПроверка подключения к {client.server_url}...")
    if client.check_connection():
        print("Подключено!")
    else:
        print("Не подключено. Убедитесь что сервер запущен.")
        return
    
    print("\n" + "-" * 60)
    print("Пример 1: Анализ данных пилота")
    print("-" * 60)
    
    sample_data = {
        "Hours_Awake": 12,
        "Decisions_Made": 55,
        "Task_Switches": 10,
        "Avg_Decision_Time_sec": 3.5,
        "Sleep_Hours_Last_Night": 5.0,
        "Caffeine_Intake_Cups": 3,
        "Stress_Level_1_10": 7.0,
        "Error_Rate": 0.15,
        "Cognitive_Load_Score": 0.8,
    }
    
    try:
        result = client.predict_tabular(sample_data)
        print(f"Уровень усталости: {result['prediction']}")
        print(f"Уверенность: {result['confidence']:.1%}")
        print(f"Вероятности: {result['probabilities']}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "-" * 60)
    print("Пример 2: Batch анализ")
    print("-" * 60)
    
    batch_data = [
        {
            "Hours_Awake": 8, "Decisions_Made": 30, "Task_Switches": 5,
            "Avg_Decision_Time_sec": 2.0, "Sleep_Hours_Last_Night": 7,
            "Caffeine_Intake_Cups": 1, "Stress_Level_1_10": 3,
            "Error_Rate": 0.05, "Cognitive_Load_Score": 0.3,
        },
        {
            "Hours_Awake": 16, "Decisions_Made": 80, "Task_Switches": 15,
            "Avg_Decision_Time_sec": 5.0, "Sleep_Hours_Last_Night": 4,
            "Caffeine_Intake_Cups": 4, "Stress_Level_1_10": 8,
            "Error_Rate": 0.25, "Cognitive_Load_Score": 0.9,
        },
    ]
    
    try:
        results = client.predict_batch_tabular(batch_data)
        for i, result in enumerate(results['results']):
            print(f"Пилот {i+1}: {result['prediction']} (уверенность: {result['confidence']:.1%})")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    demo()
