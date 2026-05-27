"""Validace vstupů (email, heslo, atd.)"""

import re

def validate_email_format(email: str) -> tuple:
    """Validace emailu - jednoduché regex"""
    email = email.strip().lower()
    
    # Jednoduchý regex na email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(pattern, email):
        return False, "Neplatný email"
    
    return True, ""


def validate_password(password: str) -> tuple:
    """Validace hesla - 8+ znaků, malé, velké, číslo, speciální znak"""
    errors = []

    if len(password) < 8:
        errors.append("Heslo musí mít alespoň 8 znaků")

    if not re.search(r'[a-z]', password):
        errors.append("Heslo musí obsahovat alespoň jedno malé písmeno")

    if not re.search(r'[A-Z]', password):
        errors.append("Heslo musí obsahovat alespoň jedno velké písmeno")

    if not re.search(r'[0-9]', password):
        errors.append("Heslo musí obsahovat alespoň jednu číslici")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\|`~]', password):
        errors.append("Heslo musí obsahovat alespoň jeden speciální znak")

    return len(errors) == 0, errors


def validate_nickname(nickname: str, min_length: int = 3, max_length: int = 50) -> tuple:
    """Validace přezdívky"""
    if not nickname or len(nickname.strip()) == 0:
        return False, "Přezdívka nesmí být prázdná"

    nickname = nickname.strip()

    if len(nickname) < min_length:
        return False, f"Přezdívka musí mít alespoň {min_length} znaků"

    if len(nickname) > max_length:
        return False, f"Přezdívka nesmí přesáhnout {max_length} znaků"

    return True, ""


def validate_bio(bio: str, max_length: int = 500) -> tuple:
    """Validace bio"""
    if len(bio) > max_length:
        return False, f"Bio nesmí přesáhnout {max_length} znaků"
    return True, ""


def validate_nerd_level(nerd_level, min_val: int = 0, max_val: int = 10) -> tuple:
    """Validace nerd levelu"""
    try:
        level = int(nerd_level)
        if level < min_val or level > max_val:
            return False, f"Nerd level musí být mezi {min_val} a {max_val}"
        return True, ""
    except (ValueError, TypeError):
        return False, "Nerd level musí být číslo"
