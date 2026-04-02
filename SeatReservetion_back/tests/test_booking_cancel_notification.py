#!/usr/bin/env python3
"""
Тест уведомления при отмене бронирования

Проверяет:
1. Создание бронирования
2. Отмена бронирования
3. Проверка отправки уведомления пользователю
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
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from datetime import date, timedelta


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def test_booking_cancellation():
    """Тест уведомления при отмене бронирования"""
    
    print_header("Тест уведомления при отмене бронирования")
    
    db = SessionLocal()
    
    try:
        # 1. Получаем статусы
        print("\n[1] Получение статусов...")
        confirmed_status = db.query(Status).filter(Status.name == "confirmed").first()
        cancelled_status = db.query(Status).filter(Status.name == "cancelled").first()
        
        print(f"   Confirmed: {confirmed_status.id} ({confirmed_status.name})")
        print(f"   Cancelled: {cancelled_status.id} ({cancelled_status.name})")
        
        # 2. Находим пользователя garussm@gmail.com
        print("\n[2] Поиск пользователя garussm@gmail.com...")
        test_user = db.query(Account).filter(Account.email == "garussm@gmail.com").first()
        
        if not test_user:
            print("   Пользователь не найден! Ищем Mgaruss...")
            test_user = db.query(Account).filter(Account.login == "Mgaruss").first()
        
        if not test_user:
            print("   Ошибка: Пользователь не найден!")
            return False
        
        if not test_user.email:
            print("   Ошибка: У пользователя нет email!")
            return False
        
        print(f"   Найден: {test_user.login} ({test_user.email})")
        
        # 3. Находим рабочее место в активном помещении
        print("\n[3] Поиск рабочего места...")
        workspace = db.query(Workspace).join(Room).join(Status).filter(
            Status.name == "active"
        ).first()
        
        if not workspace:
            print("   Ошибка: Нет активных рабочих мест!")
            return False
        
        room = db.query(Room).filter(Room.id == workspace.room_id).first()
        print(f"   Рабочее место: {workspace.name} в помещении '{room.name}'")
        
        # 4. Создаём бронирование
        print("\n[4] Создание бронирования...")
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
        
        # 5. Считаем уведомления до отмены
        print("\n[5] Подсчёт уведомлений до отмены...")
        notifications_before = db.query(Notification).filter(
            Notification.user_id == test_user.id
        ).count()
        print(f"   Уведомлений до отмены: {notifications_before}")
        
        # 6. Отменяем бронирование
        print("\n[6] Отмена бронирования...")
        test_booking.status_id = cancelled_status.id if cancelled_status else 14
        db.commit()
        
        # Вызываем отправку уведомления
        print("   Вызов send_booking_cancelled_notification...")
        try:
            notification_service = NotificationService(db)
            result = notification_service.send_booking_cancelled_notification(booking_id=test_booking.id)
            print(f"   Результат: {result}")
        except Exception as notif_error:
            print(f"   Ошибка при отправке уведомления: {notif_error}")
            import traceback
            traceback.print_exc()
        
        # 7. Проверяем уведомления
        print("\n[7] Проверка уведомлений...")
        notifications_after = db.query(Notification).filter(
            Notification.user_id == test_user.id
        ).count()
        print(f"   Уведомлений после отмены: {notifications_after}")
        
        # 8. Выводим новые уведомления
        if notifications_after > notifications_before:
            new_notifications = db.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.created_at >= test_booking.created_at
            ).all()
            
            print(f"\n   Найдено новых уведомлений: {len(new_notifications)}")
            for notif in new_notifications:
                print(f"\n   - Тип: {notif.notification_type}")
                print(f"     Тема: {notif.subject}")
                print(f"     Статус: {notif.status.name if notif.status else 'N/A'}")
                print(f"     Создано: {notif.created_at}")
                
                if notif.status and notif.status.name == "failed":
                    print("     ⚠️  Уведомление НЕ отправлено!")
                    print("     Причина: проблема с SMTP или email")
                elif notif.status and notif.status.name == "sent":
                    print("     ✅ Уведомление отправлено успешно!")
            
            return True
        else:
            print("\n   Ошибка: Уведомление не было создано!")
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


def check_user_email():
    """Проверка email пользователя"""
    
    print_header("Проверка email пользователей")
    
    db = SessionLocal()
    
    try:
        users = db.query(Account).all()
        for user in users:
            status = db.query(Status).filter(Status.id == user.status_id).first()
            print(f"\n   ID={user.id}")
            print(f"   Login={user.login}")
            print(f"   Email={user.email}")
            print(f"   Status={status.name if status else 'N/A'}")
            
            # Проверяем уведомления
            notif_count = db.query(Notification).filter(Notification.user_id == user.id).count()
            print(f"   Уведомлений: {notif_count}")
            
    finally:
        db.close()


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print(" SeatReservation - Тест отмены бронирования")
    print("=" * 60)
    
    # Проверка email пользователей
    check_user_email()
    
    # Запуск теста
    test_passed = test_booking_cancellation()
    
    # Итог
    print("\n" + "=" * 60)
    print(" ИТОГИ ТЕСТА")
    print("=" * 60)
    
    if test_passed:
        print(" ТЕСТ ПРОЙДЕН!")
        print("\n Уведомление об отмене бронирования было создано.")
        print(" Проверьте статус отправки и email ящик.")
    else:
        print(" ТЕСТ НЕ ПРОЙДЕН!")
        print("\n Уведомление не было создано или отправлено.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
