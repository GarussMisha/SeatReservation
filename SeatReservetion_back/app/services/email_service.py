"""
Email Service - сервис для отправки email уведомлений
Использует SMTP для отправки писем с поддержкой HTML шаблонов
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        self.use_tls = settings.smtp_use_tls

    def is_configured(self) -> bool:
        """Проверка, настроен ли SMTP"""
        return bool(self.smtp_user and self.smtp_password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Отправка email одному получателю

        Args:
            to_email: Email получателя
            subject: Тема письма
            html_content: HTML содержимое письма
            text_content: Текстовое содержимое (опционально)

        Returns:
            Словарь с результатом отправки
        """
        result = {
            "success": False,
            "message": "",
            "sent_at": None
        }

        if not self.is_configured():
            result["message"] = "SMTP не настроен. Проверьте переменные окружения"
            logger.warning(result["message"])
            return result

        if not to_email:
            result["message"] = "Email получателя не указан"
            logger.warning(result["message"])
            return result

        try:
            # Создаем письмо
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Добавляем текстовую и HTML версии
            if text_content:
                part_text = MIMEText(text_content, "plain", "utf-8")
                msg.attach(part_text)

            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_html)

            # Отправляем через SMTP
            # Для Resend: smtp.resend.com:465 с SSL
            if self.use_tls:
                # Используем SSL (для порта 465)
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()

            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            result["success"] = True
            result["message"] = "Письмо успешно отправлено"
            result["sent_at"] = datetime.now().isoformat()

            logger.info(f"Письмо отправлено на {to_email} с темой '{subject}'")

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Ошибка аутентификации SMTP: {str(e)}"
            result["message"] = error_msg
            logger.error(error_msg)

        except smtplib.SMTPConnectError as e:
            error_msg = f"Ошибка подключения к SMTP серверу: {str(e)}"
            result["message"] = error_msg
            logger.error(error_msg)

        except smtplib.SMTPException as e:
            error_msg = f"SMTP ошибка при отправке: {str(e)}"
            result["message"] = error_msg
            logger.error(error_msg)

        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            result["message"] = error_msg
            logger.error(error_msg)

        return result

    def send_email_batch(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Массовая рассылка email

        Args:
            recipients: Список получателей [{"email": "...", "name": "..."}, ...]
            subject: Тема письма
            html_content: HTML содержимое письма
            text_content: Текстовое содержимое (опционально)

        Returns:
            Словарь с результатами рассылки
        """
        results = {
            "total": len(recipients),
            "success": 0,
            "failed": 0,
            "details": []
        }

        for recipient in recipients:
            email = recipient.get("email")
            if not email:
                results["failed"] += 1
                results["details"].append({
                    "email": email,
                    "success": False,
                    "message": "Email не указан"
                })
                continue

            result = self.send_email(email, subject, html_content, text_content)

            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "email": email,
                "success": result["success"],
                "message": result["message"]
            })

        return results

    @staticmethod
    def create_booking_cancelled_html(
        user_name: str,
        workspace_name: str,
        room_address: str,
        booking_date: str,
        reason: str = "Ручная отмена"
    ) -> str:
        """
        Создание HTML шаблона для уведомления об отмене бронирования

        Args:
            user_name: Имя пользователя
            workspace_name: Название рабочего места
            room_address: Адрес помещения
            booking_date: Дата бронирования
            reason: Причина отмены

        Returns:
            HTML строка
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; }}
                .info-box {{ background-color: white; border-left: 4px solid #f44336; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                h1 {{ margin: 0; font-size: 24px; }}
                .detail {{ margin: 12px 0; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Бронирование отменено!</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, <strong>{user_name}</strong>!</p>
                    
                    <p>Ваше бронирование было отменено.</p>

                    <div class="info-box">
                        <div class="detail">
                            <span class="label">🪑 Место:</span>
                            <span class="value">{workspace_name}</span>
                        </div>
                        <div class="detail">
                            <span class="label">🏢 Помещение:</span>
                            <span class="value">{room_address or 'Не указан'}</span>
                        </div>
                        <div class="detail">
                            <span class="label">📅 Дата:</span>
                            <span class="value">{booking_date}</span>
                        </div>
                        <div class="detail">
                            <span class="label">⚠️ Причина:</span>
                            <span class="value">{reason}</span>
                        </div>
                    </div>

                    <p>Если у вас возникли вопросы, пожалуйста, обратитесь к администратору системы.</p>

                    <p>С уважением,<br>Команда Seat Reservation System</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое уведомление, пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def create_workspace_disabled_html(
        user_name: str,
        workspace_name: str,
        room_name: str,
        room_address: str,
        booking_date: str
    ) -> str:
        """
        Создание HTML шаблона для уведомления об отключении рабочего места

        Args:
            user_name: Имя пользователя
            workspace_name: Название рабочего места
            room_name: Название помещения
            room_address: Адрес помещения
            booking_date: Дата бронирования

        Returns:
            HTML строка
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff9800; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; }}
                .info-box {{ background-color: white; border-left: 4px solid #ff9800; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                h1 {{ margin: 0; font-size: 24px; }}
                h2 {{ color: #ff9800; font-size: 18px; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Рабочее место недоступно</h1>
                </div>
                <div class="content">
                    <p>Уважаемый(ая), <strong>{user_name}</strong>!</p>
                    
                    <p>Информируем вас, что рабочее место, которое вы забронировали, стало недоступно по техническим причинам. Ваше бронирование было отменено. Приносим извинения за неудобства!</p>
                    
                    <div class="info-box">
                        <h2>Детали бронирования:</h2>
                        <div class="detail">
                            <span class="label">🪑 Рабочее место:</span> {workspace_name}
                        </div>
                        <div class="detail">
                            <span class="label">🏢 Помещение:</span> {room_name}
                        </div>
                        <div class="detail">
                            <span class="label">📍 Адрес:</span> {room_address or 'Не указан'}
                        </div>
                        <div class="detail">
                            <span class="label">📅 Дата:</span> {booking_date}
                        </div>
                    </div>
                    
                    <p>Пожалуйста, выберите другое рабочее место в системе бронирования.</p>
                    
                    <p>С уважением,<br>Команда Seat Reservation System</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое уведомление, пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def create_room_disabled_html(
        user_name: str,
        room_name: str,
        room_address: str,
        affected_bookings: List[Dict[str, str]]
    ) -> str:
        """
        Создание HTML шаблона для уведомления об отключении помещения

        Args:
            user_name: Имя пользователя
            room_name: Название помещения
            room_address: Адрес помещения
            affected_bookings: Список затронутых бронирований

        Returns:
            HTML строка
        """
        bookings_html = ""
        for booking in affected_bookings:
            bookings_html += f"""
            <div style="background-color: white; border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <div class="detail"><span class="label">🪑 Место:</span> {booking.get('workspace_name', 'Н/Д')}</div>
                <div class="detail"><span class="label">📅 Дата:</span> {booking.get('booking_date', 'Н/Д')}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #9c27b0; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; }}
                .info-box {{ background-color: white; border-left: 4px solid #9c27b0; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                h1 {{ margin: 0; font-size: 24px; }}
                h2 {{ color: #9c27b0; font-size: 18px; }}
                .detail {{ margin: 8px 0; }}
                .label {{ font-weight: bold; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 Помещение недоступно</h1>
                </div>
                <div class="content">
                    <p>Уважаемый(ая), <strong>{user_name}</strong>!</p>
                    
                    <p>Информируем вас, что помещение <strong>{room_name}</strong> стало недоступно по техническим причинам. Ваши бронирования в этом помещении были отменены. Приносим извинения за неудобства!</p>
                    
                    <div class="info-box">
                        <h2>Информация о помещении:</h2>
                        <div class="detail"><span class="label">🏢 Название:</span> {room_name}</div>
                        <div class="detail"><span class="label">📍 Адрес:</span> {room_address or 'Не указан'}</div>
                    </div>
                    
                    <h2>Затронутые бронирования:</h2>
                    {bookings_html}
                    
                    <p>Пожалуйста, выберите другое рабочее место в системе бронирования.</p>
                    
                    <p>С уважением,<br>Команда Seat Reservation System</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое уведомление, пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def create_booking_reminder_html(
        user_name: str,
        workspace_name: str,
        room_name: str,
        room_address: str,
        booking_date: str
    ) -> str:
        """
        Создание HTML шаблона для напоминания о бронировании

        Args:
            user_name: Имя пользователя
            workspace_name: Название рабочего места
            room_name: Название помещения
            room_address: Адрес помещения
            booking_date: Дата бронирования

        Returns:
            HTML строка
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196f3; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; }}
                .info-box {{ background-color: white; border-left: 4px solid #2196f3; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                h1 {{ margin: 0; font-size: 24px; }}
                h2 {{ color: #2196f3; font-size: 18px; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #555; }}
                .reminder-badge {{ 
                    background-color: #fff3cd; 
                    border: 2px solid #ffc107; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 15px 0;
                    text-align: center;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Напоминание о бронировании</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, <strong>{user_name}</strong>!</p>
                    
                    <div class="reminder-badge">
                        ⏰ Не забудьте посетить офис завтра!
                    </div>
                    
                    <p>Напоминаем вам о предстоящем бронировании рабочего места.</p>
                    
                    <div class="info-box">
                        <h2>Детали бронирования:</h2>
                        <div class="detail">
                            <span class="label">🪑 Рабочее место:</span> {workspace_name}
                        </div>
                        <div class="detail">
                            <span class="label">🏢 Помещение:</span> {room_name}
                        </div>
                        <div class="detail">
                            <span class="label">📍 Адрес:</span> {room_address or 'Не указан'}
                        </div>
                        <div class="detail">
                            <span class="label">📅 Дата:</span> {booking_date}
                        </div>
                    </div>
                    
                    <p>Желаем продуктивного дня!</p>
                    
                    <p>С уважением,<br>Команда Seat Reservation System</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое напоминание. Если вы больше не хотите получать уведомления, обратитесь к администратору.</p>
                </div>
            </div>
        </body>
        </html>
        """


# Singleton экземпляр сервиса
email_service = EmailService()


# Экспорт
__all__ = ["EmailService", "email_service"]
