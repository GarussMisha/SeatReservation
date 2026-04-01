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
            if self.use_tls:
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


# Singleton экземпляр сервиса
email_service = EmailService()


# Экспорт
__all__ = ["EmailService", "email_service"]
