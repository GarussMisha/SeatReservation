"""
Notification Templates - шаблоны уведомлений для системы бронирования

Содержит:
- Функции для получения данных (JSON для frontend/БД)
- Функции для генерации HTML (для email)
"""
from typing import Dict, List, Any


# =============================================================================
# БАЗОВЫЕ ДАННЫЕ (единый источник истины)
# =============================================================================

def get_base_booking_data(
    workspace_name: str,
    room_address: str,
    booking_date: str
) -> Dict[str, Any]:
    """
    Базовые данные для всех уведомлений о бронировании
    
    Returns:
        Словарь с общими данными
    """
    return {
        "workspace_name": workspace_name,
        "room_address": room_address,
        "booking_date": booking_date
    }


# =============================================================================
# ДАННЫЕ ДЛЯ FRONTEND (JSON)
# =============================================================================

def get_booking_cancelled_data(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str,
    reason: str = "Ручная отмена"
) -> Dict[str, Any]:
    """
    Данные для уведомления об отмене бронирования
    
    Returns:
        Словарь с данными для отображения
    """
    base_data = get_base_booking_data(workspace_name, room_address, booking_date)
    
    return {
        "type": "booking_cancelled",
        "title": "Бронирование отменено!",
        "icon": "❌",
        "greeting": f"Здравствуйте, {user_name}!",
        "message": "Ваше бронирование было отменено.",
        "items": [
            {"icon": "🪑", "label": "Место", "value": base_data["workspace_name"]},
            {"icon": "🏢", "label": "Помещение", "value": base_data["room_address"]},
            {"icon": "📅", "label": "Дата", "value": base_data["booking_date"]},
            {"icon": "⚠️", "label": "Причина", "value": reason}
        ],
        "footer": "Если у вас возникли вопросы, пожалуйста, обратитесь к администратору системы."
    }


def get_workspace_disabled_data(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str
) -> Dict[str, Any]:
    """
    Данные для уведомления об отключении рабочего места
    
    Returns:
        Словарь с данными для отображения
    """
    base_data = get_base_booking_data(workspace_name, room_address, booking_date)
    
    return {
        "type": "workspace_disabled",
        "title": "Рабочее место недоступно!",
        "icon": "⚠️",
        "greeting": f"Здравствуйте, {user_name}!",
        "message": "Рабочее место, которое вы забронировали, стало недоступно. Ваше бронирование было отменено.",
        "items": [
            {"icon": "🪑", "label": "Место", "value": base_data["workspace_name"]},
            {"icon": "🏢", "label": "Помещение", "value": base_data["room_address"]},
            {"icon": "📅", "label": "Дата", "value": base_data["booking_date"]}
        ],
        "footer": "Пожалуйста, выберите другое рабочее место в системе бронирования."
    }


def get_room_disabled_data(
    user_name: str,
    room_name: str,
    room_address: str,
    affected_bookings: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Данные для уведомления об отключении помещения
    
    Args:
        user_name: Имя пользователя
        room_name: Название помещения
        room_address: Адрес помещения
        affected_bookings: Список затронутых бронирований
    
    Returns:
        Словарь с данными для отображения
    """
    bookings_text = "\n".join([
        f"  • {b.get('workspace_name', 'Н/Д')} на {b.get('booking_date', 'Н/Д')}"
        for b in affected_bookings
    ])
    
    return {
        "type": "room_disabled",
        "title": "Помещение недоступно!",
        "icon": "🏢",
        "greeting": f"Здравствуйте, {user_name}!",
        "message": f"Помещение \"{room_name}\" стало недоступно. Ваши бронирования были отменены.",
        "items": [
            {"icon": "🏢", "label": "Помещение", "value": room_name},
            {"icon": "📍", "label": "Адрес", "value": room_address},
            {"icon": "📋", "label": "Затронутые бронирования", "value": bookings_text}
        ],
        "footer": "Пожалуйста, выберите другое рабочее место в системе бронирования."
    }


def get_booking_reminder_data(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str
) -> Dict[str, Any]:
    """
    Данные для напоминания о бронировании
    
    Returns:
        Словарь с данными для отображения
    """
    base_data = get_base_booking_data(workspace_name, room_address, booking_date)
    
    return {
        "type": "booking_reminder",
        "title": "Напоминание о бронировании!",
        "icon": "📅",
        "greeting": f"Здравствуйте, {user_name}!",
        "message": "Напоминаем вам о предстоящем бронировании рабочего места.",
        "items": [
            {"icon": "🪑", "label": "Место", "value": base_data["workspace_name"]},
            {"icon": "🏢", "label": "Помещение", "value": base_data["room_address"]},
            {"icon": "📅", "label": "Дата", "value": base_data["booking_date"]}
        ],
        "footer": "Желаем продуктивного дня!"
    }


# =============================================================================
# HTML ДЛЯ EMAIL
# =============================================================================

def create_booking_cancelled_html(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str,
    reason: str = "Ручная отмена"
) -> str:
    """
    Создание HTML шаблона для уведомления об отмене бронирования
    
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
            .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 20px; }}
            .info-box {{ background-color: white; border-left: 4px solid #f44336; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .detail {{ margin: 12px 0; display: flex; align-items: center; gap: 8px; }}
            .label {{ font-weight: bold; color: #555; min-width: 120px; }}
            .value {{ color: #333; }}
            h1 {{ margin: 0; font-size: 24px; }}
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


def create_workspace_disabled_html(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str
) -> str:
    """
    Создание HTML шаблона для уведомления об отключении рабочего места
    
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
            .header {{ background-color: #ff9800; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 20px; }}
            .info-box {{ background-color: white; border-left: 4px solid #ff9800; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .detail {{ margin: 12px 0; display: flex; align-items: center; gap: 8px; }}
            .label {{ font-weight: bold; color: #555; min-width: 120px; }}
            .value {{ color: #333; }}
            h1 {{ margin: 0; font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Рабочее место недоступно</h1>
            </div>
            <div class="content">
                <p>Здравствуйте, <strong>{user_name}</strong>!</p>
                <p>Рабочее место, которое вы забронировали, стало недоступно. Ваше бронирование было отменено. Приносим извинения за неудобства!</p>
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


def create_room_disabled_html(
    user_name: str,
    room_name: str,
    room_address: str,
    affected_bookings: List[Dict[str, str]]
) -> str:
    """
    Создание HTML шаблона для уведомления об отключении помещения
    
    Returns:
        HTML строка
    """
    bookings_html = "".join([
        f"""
        <div style="background-color: white; border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 4px;">
            <div class="detail">
                <span class="label">🪑 Место:</span>
                <span class="value">{b.get('workspace_name', 'Н/Д')}</span>
            </div>
            <div class="detail">
                <span class="label">📅 Дата:</span>
                <span class="value">{b.get('booking_date', 'Н/Д')}</span>
            </div>
        </div>
        """
        for b in affected_bookings
    ])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #9c27b0; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 20px; }}
            .info-box {{ background-color: white; border-left: 4px solid #9c27b0; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .detail {{ margin: 8px 0; display: flex; align-items: center; gap: 8px; }}
            .label {{ font-weight: bold; color: #555; min-width: 120px; }}
            .value {{ color: #333; }}
            h1 {{ margin: 0; font-size: 24px; }}
            h2 {{ color: #9c27b0; font-size: 18px; margin: 15px 0 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏢 Помещение недоступно</h1>
            </div>
            <div class="content">
                <p>Здравствуйте, <strong>{user_name}</strong>!</p>
                <p>Помещение <strong>{room_name}</strong> стало недоступно по техническим причинам. Ваши бронирования были отменены. Приносим извинения за неудобства!</p>
                <div class="info-box">
                    <h2>Информация о помещении:</h2>
                    <div class="detail">
                        <span class="label">🏢 Название:</span>
                        <span class="value">{room_name}</span>
                    </div>
                    <div class="detail">
                        <span class="label">📍 Адрес:</span>
                        <span class="value">{room_address or 'Не указан'}</span>
                    </div>
                    <h2>Затронутые бронирования:</h2>
                    {bookings_html}
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


def create_booking_reminder_html(
    user_name: str,
    workspace_name: str,
    room_address: str,
    booking_date: str
) -> str:
    """
    Создание HTML шаблона для напоминания о бронировании
    
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
            .header {{ background-color: #2196f3; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 20px; }}
            .info-box {{ background-color: white; border-left: 4px solid #2196f3; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .reminder-badge {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .detail {{ margin: 12px 0; display: flex; align-items: center; gap: 8px; }}
            .label {{ font-weight: bold; color: #555; min-width: 120px; }}
            .value {{ color: #333; }}
            h1 {{ margin: 0; font-size: 24px; }}
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


# =============================================================================
# ЭКСПОРТ
# =============================================================================

__all__ = [
    # Данные для frontend
    "get_booking_cancelled_data",
    "get_workspace_disabled_data",
    "get_room_disabled_data",
    "get_booking_reminder_data",
    
    # HTML для email
    "create_booking_cancelled_html",
    "create_workspace_disabled_html",
    "create_room_disabled_html",
    "create_booking_reminder_html"
]
