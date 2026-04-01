#!/usr/bin/env python3
"""
Тест уведомления при отключении помещения

Проверяет:
1. Создание помещения
2. Создание рабочего места в помещении
3. Создание бронирования
4. Отключение помещения
5. Проверка отправки уведомления
"""

import sys
import os
import io

# Настройка кодировки для Windows консоли
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, create_and_initialize_tables
from app.models.room import Room
from app.models.workspace import Workspace
from app.models.booking import Booking
from app.models.account import Account
from app.models.status import Status
from app.services.notification_service import NotificationService
from datetime import date, timedelta


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def test_room_disable_notification():
    """Тест уведомления при отключении помещения"""
    
    print_header("Тест уведомления при отключении помещения")
    
    db = SessionLocal()
    
    try:
        # 1. Получаем статусы
        print("\n[1] Получение статусов...")
        active_status = db.query(Status).filter(Status.name == "active").first()
        inactive_status = db.query(Status).filter(Status.name == "inactive").first()
        confirmed_status = db.query(Status).filter(Status.name == "confirmed").first()
        
        if not active_status or not inactive_status:
            print(" Ошибка: Статусы 'active' или 'inactive' не найдены!")
            return False
        
        print(f"   Active статус: {active_status.id} ({active_status.name})")
        print(f"   Inactive статус: {inactive_status.id} ({inactive_status.name})")
        print(f"   Confirmed статус: {confirmed_status.id} ({confirmed_status.name})")
        
        # 2. Создаём тестовое помещение
        print("\n[2] Создание тестового помещения...")
        test_room = Room(
            name=f"Тестовое помещение {os.getpid()}",
            address="Тестовый адрес",
            description="Помещение для тестирования уведомлений",
            status_id=active_status.id
        )
        db.add(test_room)
        db.commit()
        db.refresh(test_room)
        print(f"   Помещение создано: ID={test_room.id}, Name={test_room.name}")
        
        # 3. Создаём рабочее место
        print("\n[3] Создание рабочего места...")
        test_workspace = Workspace(
            name="Рабочее место 1",
            room_id=test_room.id,
            is_active=True,
            status_id=10  # FREE
        )
        db.add(test_workspace)
        db.commit()
        db.refresh(test_workspace)
        print(f"   Рабочее место создано: ID={test_workspace.id}, Name={test_workspace.name}")
        
        # 4. Создаём тестового пользователя (или берём admin)
        print("\n[4] Получение пользователя...")
        test_user = db.query(Account).filter(Account.is_admin == True).first()
        if not test_user:
            print(" Ошибка: Администратор не найден!")
            return False
        
        # Если email нет или он тестовый - используем ваш email
        if not test_user.email or test_user.email == "admin@example.com":
            print(" Обновление email пользователя на тестовый...")
            test_user.email = "parussmikle@gmail.com"  # Ваш реальный email для тестов
            db.commit()
            print(f"   Email обновлён: {test_user.email}")
        
        print(f"   Пользователь: {test_user.login} ({test_user.email})")
        
        # 5. Создаём бронирование
        print("\n[5] Создание бронирования...")
        tomorrow = date.today() + timedelta(days=1)
        test_booking = Booking(
            booking_date=tomorrow,
            account_id=test_user.id,
            workspace_id=test_workspace.id,
            status_id=confirmed_status.id if confirmed_status else 13
        )
        db.add(test_booking)
        db.commit()
        db.refresh(test_booking)
        print(f"   Бронирование создано: ID={test_booking.id}, Date={tomorrow}")
        
        # 6. Отключаем помещение (меняем статус на inactive)
        print("\n[6] Отключение помещения (active -> inactive)...")
        
        # Сохраняем количество уведомлений до отключения
        notifications_before = db.query(Notification).filter(
            Notification.user_id == test_user.id
        ).count()
        print(f"   Уведомлений до отключения: {notifications_before}")
        
        # Меняем статус НАПРЯМУЮ (как в API)
        print("   Прямое изменение статуса в БД...")
        test_room.status_id = inactive_status.id
        
        # Вызываем отправку уведомлений ВРУЧНУЮ (как это делает API)
        print("   Вызов send_room_disabled_notification...")
        try:
            notification_service = NotificationService(db)
            result = notification_service.send_room_disabled_notification(room_id=test_room.id)
            print(f"   Результат: {result}")
        except Exception as notif_error:
            print(f"   Ошибка при отправке уведомления: {notif_error}")
        
        db.commit()
        print("   Помещение отключено!")
        
        # 7. Проверяем уведомления
        print("\n[7] Проверка уведомлений...")
        notifications_after = db.query(Notification).filter(
            Notification.user_id == test_user.id
        ).count()
        print(f"   Уведомлений после отключения: {notifications_after}")
        
        if notifications_after > notifications_before:
            new_notifications = db.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.created_at >= test_room.created_at
            ).all()
            
            print(f"\n   Найдено новых уведомлений: {len(new_notifications)}")
            for notif in new_notifications:
                print(f"\n   - Тип: {notif.notification_type}")
                print(f"     Тема: {notif.subject}")
                print(f"     Статус: {notif.status.name if notif.status else 'N/A'}")
                print(f"     Создано: {notif.created_at}")
            
            print("\n УВЕДОМЛЕНИЕ ОТПРАВЛЕНО!")
            return True
        else:
            print("\n Ошибка: Уведомление не было создано!")
            print("\n Возможные причины:")
            print("   1. Не сработала логика в update_room")
            print("   2. Ошибка в send_room_disabled_notification")
            print("   3. Не найдены активные бронирования")
            return False
        
    except Exception as e:
        db.rollback()
        print(f"\n Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Очистка
        print("\n[8] Очистка...")
        try:
            # Удаляем бронирования
            db.query(Booking).filter(Booking.workspace_id == test_workspace.id).delete()
            # Удаляем рабочие места
            db.query(Workspace).filter(Workspace.room_id == test_room.id).delete()
            # Удаляем помещение
            db.delete(test_room)
            db.commit()
            print("   Тестовые данные удалены")
        except:
            pass
        
        db.close()


def check_email_settings():
    """Проверка настроек email"""
    from app.core.config import settings
    from app.services.email_service import email_service
    
    print_header("Проверка настроек Email")
    
    print(f"  SMTP Host: {settings.smtp_host}")
    print(f"  SMTP Port: {settings.smtp_port}")
    print(f"  SMTP User: {settings.smtp_user}")
    print(f"  From Email: {settings.smtp_from_email}")
    print(f"  From Name: {settings.smtp_from_name}")
    
    if email_service.is_configured():
        print("\n Email сервис настроен!")
        return True
    else:
        print("\n Email сервис НЕ настроен!")
        print(" Проверьте .env файл")
        return False


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print(" SeatReservation - Тест уведомления при отключении помещения")
    print("=" * 60)
    
    # Проверка email настроек
    email_configured = check_email_settings()
    
    # Запуск теста
    test_passed = test_room_disable_notification()
    
    # Итог
    print("\n" + "=" * 60)
    print(" ИТОГИ ТЕСТА")
    print("=" * 60)
    
    if test_passed:
        print(" ТЕСТ ПРОЙДЕН!")
        print("\n Уведомление было создано при отключении помещения.")
        print(" Проверьте базу данных и email ящик пользователя.")
    else:
        print(" ТЕСТ НЕ ПРОЙДЕН!")
        print("\n Уведомление не было создано.")
        print(" Проверьте логи и код приложения.")
    
    print("=" * 60)


if __name__ == "__main__":
    # Импортируем Notification здесь чтобы избежать циклического импорта
    from app.models.notification import Notification
    main()
