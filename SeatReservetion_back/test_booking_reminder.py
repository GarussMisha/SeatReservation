#!/usr/bin/env python3
"""
Тест напоминаний о бронировании за 6 часов

Проверяет:
1. Создание бронирования на завтра
2. Запуск задачи напоминаний
3. Проверка отправки уведомления
"""

import sys
import os
import io
from datetime import date, timedelta

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
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.services.scheduler_service import SchedulerService


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def test_booking_reminder():
    """Тест напоминания о бронировании"""
    
    print_header("Тест напоминания о бронировании за 6 часов")
    
    db = SessionLocal()
    
    try:
        # 1. Получаем статусы
        print("\n[1] Получение статусов...")
        confirmed_status = db.query(Status).filter(Status.name == "confirmed").first()
        print(f"   Confirmed статус: {confirmed_status.id} ({confirmed_status.name})")
        
        # 2. Находим пользователя
        print("\n[2] Поиск пользователя...")
        test_user = db.query(Account).filter(Account.email == "parussmikle@gmail.com").first()
        
        if not test_user:
            print("   Пользователь не найден! Ищем admin...")
            test_user = db.query(Account).filter(Account.login == "admin").first()
        
        if not test_user:
            print("   Ошибка: Пользователь не найден!")
            return False
        
        if not test_user.email:
            print("   Ошибка: У пользователя нет email!")
            return False
        
        print(f"   Найден: {test_user.login} ({test_user.email})")
        
        # 3. Находим рабочее место
        print("\n[3] Поиск рабочего места...")
        workspace = db.query(Workspace).join(Room).join(Status).filter(
            Status.name == "active"
        ).first()
        
        if not workspace:
            print("   Ошибка: Нет активных рабочих мест!")
            return False
        
        room = db.query(Room).filter(Room.id == workspace.room_id).first()
        print(f"   Рабочее место: {workspace.name} в помещении '{room.name}'")
        
        # 4. Создаём бронирование НА ЗАВТРА
        print("\n[4] Создание бронирования на завтра...")
        tomorrow = date.today() + timedelta(days=1)
        
        test_booking = Booking(
            booking_date=tomorrow,
            account_id=test_user.id,
            workspace_id=workspace.id,
            status_id=confirmed_status.id if confirmed_status else 13
        )
        db.add(test_booking)
        db.commit()
        db.refresh(test_booking)
        print(f"   Бронирование создано: ID={test_booking.id}, Date={tomorrow}")
        
        # 5. Проверяем напоминания до запуска задачи
        print("\n[5] Проверка напоминаний до запуска...")
        reminders_before = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.notification_type == "booking_reminder"
        ).count()
        print(f"   Напоминаний до запуска: {reminders_before}")
        
        # 6. Запускаем задачу напоминаний ВРУЧНУЮ
        print("\n[6] Запуск задачи напоминаний...")
        try:
            notification_service = NotificationService(db)
            result = notification_service.send_booking_reminder_notification(
                booking_id=test_booking.id
            )
            print(f"   Результат: {result}")
        except Exception as notif_error:
            print(f"   Ошибка при отправке напоминания: {notif_error}")
            import traceback
            traceback.print_exc()
        
        # 7. Проверяем напоминания после запуска
        print("\n[7] Проверка напоминаний после запуска...")
        reminders_after = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.notification_type == "booking_reminder"
        ).count()
        print(f"   Напоминаний после запуска: {reminders_after}")
        
        # 8. Выводим новые уведомления
        if reminders_after > reminders_before:
            new_reminders = db.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.notification_type == "booking_reminder",
                Notification.created_at >= test_booking.created_at
            ).all()
            
            print(f"\n   Найдено новых напоминаний: {len(new_reminders)}")
            for notif in new_reminders:
                print(f"\n   - Тип: {notif.notification_type}")
                print(f"     Тема: {notif.subject}")
                print(f"     Статус: {notif.status.name if notif.status else 'N/A'}")
                print(f"     Создано: {notif.created_at}")
                
                if notif.status and notif.status.name == "sent":
                    print("     ✅ Напоминание отправлено успешно!")
                elif notif.status and notif.status.name == "failed":
                    print("     ⚠️  Напоминание НЕ отправлено!")
            
            return True
        else:
            print("\n   Ошибка: Напоминание не было создано!")
            return False
        
    except Exception as e:
        db.rollback()
        print(f"\n   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Очистка
        print("\n[8] Очистка...")
        try:
            db.query(Booking).filter(Booking.id == test_booking.id).delete()
            db.commit()
            print("   Тестовые данные удалены")
        except:
            pass
        
        db.close()


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print(" SeatReservation - Тест напоминаний о бронировании")
    print("=" * 60)
    
    # Запуск теста
    test_passed = test_booking_reminder()
    
    # Итог
    print("\n" + "=" * 60)
    print(" ИТОГИ ТЕСТА")
    print("=" * 60)
    
    if test_passed:
        print(" ТЕСТ ПРОЙДЕН!")
        print("\n Напоминание было создано и отправлено.")
        print(" Проверьте email ящик пользователя.")
    else:
        print(" ТЕСТ НЕ ПРОЙДЕН!")
        print("\n Напоминание не было создано или отправлено.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
