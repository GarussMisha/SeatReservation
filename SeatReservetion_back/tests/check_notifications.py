#!/usr/bin/env python3
"""
Проверка уведомлений для всех пользователей с бронированиями

Проверяет:
1. Все помещения и их статусы
2. Все бронирования по активным помещениям
3. Email пользователей
4. Тестирует отправку уведомления
"""

import sys
import os
import io

# Настройка кодировки для Windows консоли
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.room import Room
from app.models.workspace import Workspace
from app.models.booking import Booking
from app.models.account import Account
from app.models.status import Status
from app.services.notification_service import NotificationService


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def check_all_rooms_and_bookings():
    """Проверка всех помещений и бронирований"""
    
    print_header("Проверка всех помещений и бронирований")
    
    db = SessionLocal()
    
    try:
        # 1. Получаем все помещения
        print("\n[1] Все помещения:")
        rooms = db.query(Room).all()
        for room in rooms:
            status = db.query(Status).filter(Status.id == room.status_id).first()
            print(f"   - ID={room.id}, Name={room.name}, Status={status.name if status else 'N/A'} ({room.status_id})")
        
        # 2. Получаем все рабочие места
        print("\n[2] Все рабочие места:")
        workspaces = db.query(Workspace).all()
        for ws in workspaces:
            room = db.query(Room).filter(Room.id == ws.room_id).first()
            print(f"   - ID={ws.id}, Name={ws.name}, Room={room.name if room else 'N/A'}, Active={ws.is_active}")
        
        # 3. Получаем все бронирования
        print("\n[3] Все бронирования:")
        bookings = db.query(Booking).all()
        for booking in bookings:
            workspace = db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
            room = db.query(Room).filter(Room.id == workspace.room_id).first() if workspace else None
            user = db.query(Account).filter(Account.id == booking.account_id).first()
            status = db.query(Status).filter(Status.id == booking.status_id).first()
            
            print(f"\n   Бронирование ID={booking.id}:")
            print(f"     Пользователь: {user.login} ({user.email})")
            print(f"     Рабочее место: {workspace.name if workspace else 'N/A'}")
            print(f"     Помещение: {room.name if room else 'N/A'}")
            print(f"     Дата: {booking.booking_date}")
            print(f"     Статус: {status.name if status else 'N/A'} ({booking.status_id})")
        
        # 4. Проверка пользователей с email
        print("\n[4] Все пользователи и их email:")
        users = db.query(Account).all()
        for user in users:
            status = db.query(Status).filter(Status.id == user.status_id).first()
            print(f"   - ID={user.id}, Login={user.login}, Email={user.email}, Status={status.name if status else 'N/A'}")
        
        # 5. Проверка уведомлений
        print("\n[5] Все уведомления:")
        from app.models.notification import Notification
        notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(10).all()
        for notif in notifications:
            user = db.query(Account).filter(Account.id == notif.user_id).first()
            print(f"\n   - ID={notif.id}, Type={notif.notification_type}")
            print(f"     User: {user.login if user else 'N/A'} ({user.email if user else 'N/A'})")
            print(f"     Subject: {notif.subject}")
            print(f"     Status: {notif.status.name if notif.status else 'N/A'}")
            print(f"     Created: {notif.created_at}")
        
        # Тест отправки уведомления для конкретного помещения
        print("\n\n[6] Тест отправки уведомления для помещения:")
        print("   Помещения со статусом 'active':")
        active_rooms = db.query(Room).join(Status).filter(Status.name == "active").all()
        for room in active_rooms:
            print(f"     - ID={room.id}, Name={room.name}")
        
        test_room_id = input("\n   Введите ID помещения для теста (или Enter для пропуска): ").strip()
        
        if not test_room_id:
            return
        
        if test_room_id:
            try:
                test_room_id = int(test_room_id)
                room = db.query(Room).filter(Room.id == test_room_id).first()
                if not room:
                    print(f"   Помещение с ID={test_room_id} не найдено!")
                else:
                    print(f"\n   Отправка уведомления для помещения '{room.name}'...")
                    notification_service = NotificationService(db)
                    result = notification_service.send_room_disabled_notification(room_id=test_room_id)
                    
                    print(f"\n   Результат:")
                    print(f"     Success: {result['success']}")
                    print(f"     Message: {result['message']}")
                    print(f"     Notifications sent: {result['notifications_sent']}")
                    print(f"     Notifications failed: {result['notifications_failed']}")
                    
                    if result.get('details'):
                        print(f"\n   Детали:")
                        for detail in result['details']:
                            print(f"     - User {detail.get('user_id')}: {'OK' if detail.get('success') else 'FAIL'} - {detail.get('reason', 'N/A')}")
                    
            except ValueError:
                print("   Неверный формат ID!")
            except Exception as e:
                print(f"   Ошибка: {e}")
        
        # 6. Проверка активных бронирований в помещениях
        print("\n[6] Активные бронирования по помещениям:")
        active_rooms = db.query(Room).join(Status).filter(Status.name == "active").all()
        
        for room in active_rooms:
            workspaces = db.query(Workspace).filter(Workspace.room_id == room.id).all()
            workspace_ids = [ws.id for ws in workspaces]
            
            if workspace_ids:
                # Получаем статус "cancelled" для исключения
                cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
                
                query = db.query(Booking).filter(Booking.workspace_id.in_(workspace_ids))
                if cancelled_status:
                    query = query.filter(Booking.status_id != cancelled_status.id)
                
                bookings = query.all()
                
                print(f"\n   Помещение: {room.name} (ID={room.id})")
                print(f"     Рабочих мест: {len(workspace_ids)}")
                print(f"     Активных бронирований: {len(bookings)}")
                
                for booking in bookings:
                    user = db.query(Account).filter(Account.id == booking.account_id).first()
                    workspace = db.query(Workspace).filter(Workspace.id == booking.workspace_id).first()
                    print(f"       - Бронь ID={booking.id}: {user.login} ({user.email}) на {workspace.name}")
        
    except Exception as e:
        print(f"\n Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    print("\n" + "=" * 60)
    print(" SeatReservation - Проверка уведомлений помещений")
    print("=" * 60)
    
    check_all_rooms_and_bookings()
    
    print("\n" + "=" * 60)
    print(" Проверка завершена")
    print("=" * 60)


if __name__ == "__main__":
    main()
