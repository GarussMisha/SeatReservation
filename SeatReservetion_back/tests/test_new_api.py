"""
Тестовый скрипт для проверки новых API endpoint'ов
"""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

def make_request(method, path, data=None):
    """Выполнить HTTP запрос"""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "data": json.loads(response.read().decode()) if response.status != 204 else None
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": e.read().decode() if e.read else "Unknown error"
        }

def test_endpoints():
    """Тестирование endpoint'ов"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ НОВЫХ API ENDPOINT'ОВ")
    print("=" * 60)
    
    # 1. Проверка health endpoint
    print("\n1. Проверка health endpoint...")
    result = make_request("GET", "/health")
    print(f"   Status: {result['status']}")
    if result['status'] == 200:
        print(f"   [OK] Backend работает")
    else:
        print(f"   [FAIL] Backend не работает")
        return
    
    # 2. Проверка доступности rooms
    print("\n2. Проверка доступности помещений...")
    result = make_request("GET", "/api/v1/rooms/")
    print(f"   Status: {result['status']}")
    if result['status'] == 200:
        rooms = result['data']
        print(f"   [OK] Найдено помещений: {len(rooms)}")
        if rooms:
            print(f"   Первое помещение: {rooms[0]['name']} (ID: {rooms[0]['id']})")
    else:
        print(f"   [FAIL] Ошибка получения помещений")
        return
    
    # 3. Проверка endpoint'а для получения рабочих мест с координатами
    print("\n3. Проверка GET /api/v1/rooms/{room_id}/workspaces/with-locations...")
    if rooms:
        room_id = rooms[0]['id']
        result = make_request("GET", f"/api/v1/rooms/{room_id}/workspaces/with-locations")
        print(f"   Status: {result['status']}")
        if result['status'] == 200:
            workspaces = result['data']
            print(f"   [OK] Найдено рабочих мест: {len(workspaces)}")
            if workspaces:
                ws = workspaces[0]
                print(f"   Первое место: {ws.get('name', 'N/A')} (x={ws.get('x', 0)}, y={ws.get('y', 0)})")
        else:
            print(f"   [FAIL] Ошибка: {result.get('error', 'Unknown')}")
    
    # 4. Проверка endpoint'а для сохранения плана
    print("\n4. Проверка POST /api/v1/rooms/{room_id}/plan...")
    if rooms:
        room_id = rooms[0]['id']
        test_plan = {
            "objects": [
                {
                    "object_type": "workspace",
                    "x": 100,
                    "y": 100,
                    "width": 100,
                    "height": 50,
                    "rotation": 0,
                    "is_active": True
                }
            ],
            "fieldWidth": 50,
            "fieldHeight": 50
        }
        result = make_request("POST", f"/api/v1/rooms/{room_id}/plan", test_plan)
        print(f"   Status: {result['status']}")
        if result['status'] == 200:
            print(f"   [OK] План сохранён успешно")
            data = result['data']
            print(f"   Создано объектов: {data.get('total_objects', 0)}")
        else:
            print(f"   [FAIL] Ошибка: {result.get('error', 'Unknown')}")
    
    # 5. Проверка endpoint'а для обновления названия
    print("\n5. Проверка PUT /api/v1/rooms/{room_id}/workspaces-on-plan/{wp_id}/name...")
    print(f"   [WARN] Требуется существующий workspace_on_plan ID")
    print(f"   Пропущено (нужен ID из БД)")
    
    # 6. Проверка endpoint'а для очистки плана
    print("\n6. Проверка DELETE /api/v1/rooms/{room_id}/plan...")
    if rooms:
        room_id = rooms[0]['id']
        result = make_request("DELETE", f"/api/v1/rooms/{room_id}/plan")
        print(f"   Status: {result['status']}")
        if result['status'] == 204:
            print(f"   [OK] План очищен успешно")
        else:
            print(f"   [FAIL] Ошибка: {result.get('error', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
