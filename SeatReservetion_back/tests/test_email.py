#!/usr/bin/env python3
"""
Тест отправки email через Resend SMTP
Запустите этот скрипт для проверки настройки email-уведомлений
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

from app.services.email_service import email_service
from app.core.config import settings


def print_config():
    """Вывод текущих настроек SMTP"""
    print("\n" + "=" * 60)
    print("📋 Текущие настройки SMTP:")
    print("=" * 60)
    print(f"  Host: {settings.smtp_host}")
    print(f"  Port: {settings.smtp_port}")
    print(f"  User: {settings.smtp_user}")
    print(f"  From: {settings.smtp_from_name} <{settings.smtp_from_email}>")
    print(f"  TLS:  {settings.smtp_use_tls}")
    print("=" * 60)


def test_send_email(to_email: str):
    """
    Тест отправки email
    
    Args:
        to_email: Email для тестирования
    """
    print(f"\n📬 Отправка тестового письма на: {to_email}")
    
    # Проверяем конфигурацию
    if not email_service.is_configured():
        print("❌ SMTP не настроен!")
        print(f"   Проверьте .env файл (SMTP_PASSWORD={settings.smtp_password})")
        return False
    
    # Тестовые данные
    subject = "🧪 Тестовое уведомление SeatReservation"
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .content { 
            padding: 30px; 
        }
        .success-box { 
            background-color: #d4edda; 
            border-left: 4px solid #28a745; 
            padding: 15px; 
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box {
            background-color: #e7f3ff;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background-color: #f9f9f9;
            color: #666;
            font-size: 12px;
        }
        .button {
            display: inline-block;
            background-color: #667eea;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin-top: 20px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Тестовое уведомление</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Seat Reservation System</p>
        </div>
        <div class="content">
            <p>Здравствуйте!</p>
            
            <div class="success-box">
                <strong>🎉 Отлично!</strong><br>
                Система уведомлений работает корректно.
            </div>
            
            <div class="info-box">
                <strong>📋 Детали теста:</strong><br>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Сервис: Resend SMTP</li>
                    <li>Хост: smtp.resend.com:465</li>
                    <li>Протокол: SSL/TLS</li>
                </ul>
            </div>
            
            <p>Это тестовое письмо от системы бронирования рабочих мест <strong>SeatReservation</strong>.</p>
            
            <p>Если вы получили это письмо, значит:</p>
            <ul>
                <li>✅ SMTP-настройки настроены правильно</li>
                <li>✅ Resend API ключ действителен</li>
                <li>✅ Email-уведомления готовы к работе</li>
            </ul>
            
            <a href="http://localhost:5173" class="button">Перейти в систему</a>
            
            <p style="margin-top: 30px;">С уважением,<br><strong>Команда Seat Reservation System</strong></p>
        </div>
        <div class="footer">
            <p>Это тестовое уведомление системы бронирования.</p>
            <p>Пожалуйста, не отвечайте на это письмо.</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Отправка
    result = email_service.send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )
    
    # Вывод результата
    if result["success"]:
        print("\n✅ Письмо успешно отправлено!")
        print(f"📅 Время отправки: {result['sent_at']}")
        print("\n📧 Проверьте почтовый ящик:", to_email)
        print("   Если письмо не пришло, проверьте папку 'Спам'")
        return True
    else:
        print("\n❌ Ошибка при отправке:")
        print(f"   {result['message']}")
        print("\n💡 Возможные причины:")
        print("   1. Неверный API ключ Resend")
        print("   2. Проблемы с интернет-соединением")
        print("   3. Превышен лимит отправок Resend")
        print("\n   Проверьте .env файл и логи приложения")
        return False


def test_notification_service():
    """Тест интеграции с NotificationService"""
    print("\n" + "=" * 60)
    print("🧪 Тест интеграции с NotificationService")
    print("=" * 60)
    
    try:
        from app.core.database import SessionLocal
        from app.services.notification_service import NotificationService
        
        db = SessionLocal()
        notification_service = NotificationService(db)
        
        # Проверяем, что сервис инициализирован
        print("✅ NotificationService инициализирован")
        
        # Проверяем email_service
        if notification_service.email_service.is_configured():
            print("✅ EmailService настроен")
        else:
            print("⚠️  EmailService не настроен")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print(" SeatReservation - Тест Email уведомлений")
    print("=" * 60)
    
    # Вывод настроек
    print_config()
    
    # Тест интеграции
    test_notification_service()
    
    # Запрос email для теста
    print("\n" + "=" * 60)
    default_email = "parussmikle@gmail.com"
    
    # Проверяем, есть ли аргумент командной строки
    if len(sys.argv) > 1:
        to_email = sys.argv[1].strip()
        print(f"\n Email для теста: {to_email}")
    else:
        print(f"\n Email для теста: {default_email} (по умолчанию)")
        to_email = default_email
    
    # Проверка формата email
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, to_email):
        print(f"\n Неверный формат email: {to_email}")
        return
    
    # Тест отправки
    success = test_send_email(to_email)
    
    # Итог
    print("\n" + "=" * 60)
    if success:
        print(" Тест успешно завершён!")
        print("\n Следующие шаги:")
        print("   1. Проверьте email ящик")
        print("   2. Протестируйте уведомления в приложении")
        print("   3. Настройте автоматическую отправку (планировщик)")
    else:
        print(" Тест завершён с ошибками")
        print("\n Рекомендации:")
        print("   1. Проверьте .env файл")
        print("   2. Убедитесь, что API ключ действителен")
        print("   3. Проверьте логи приложения")
    print("=" * 60)


if __name__ == "__main__":
    main()
