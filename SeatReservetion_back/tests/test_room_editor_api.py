"""
Тестовый скрипт для проверки API редактора помещений
"""
import requests

BASE_URL = "http://localhost:8000"

def test_api():
    print("🔍 Тестирование API редактора помещений...\n")
    
    # Проверка health endpoint
    print("1. Проверка health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Проверка получения плана помещения
    print("2. Проверка GET /api/v1/rooms/1/plan...")
    response = requests.get(f"{BASE_URL}/api/v1/rooms/1/plan")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Response: {response.text}")
    print()
    
    # Проверка получения объектов помещения
    print("3. Проверка GET /api/v1/rooms/1/objects...")
    response = requests.get(f"{BASE_URL}/api/v1/rooms/1/objects")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Response: {response.text}")
    print()
    
    # Вывод всех доступных routes
    print("4. Проверка Swagger docs...")
    print(f"   Откройте: {BASE_URL}/docs")
    print("   Ищите раздел 'Room Objects'\n")

if __name__ == "__main__":
    test_api()
