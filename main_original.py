from fastapi import FastAPI, Query, Depends
from typing import Optional
import re
import time
import asyncio
from collections import OrderedDict

app = FastAPI(
    title="Localization Manager Backend",
    description="A backend service for managing localized React components with templates",
    version="0.1.0",
)

# Concurrency limit to shed load at high load
CONCURRENCY_LIMIT = 2
concurrency_semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


async def limit_concurrency():
    """Dependency to limit concurrent requests"""
    async with concurrency_semaphore:
        yield


# Simple LRU Cache with TTL
class TTLCache:
    def __init__(self, maxsize=100, ttl=300):  # Default 5 minutes TTL
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}

    def get(self, key):
        if key in self.cache:
            current_time = time.time()
            timestamp = self.timestamps.get(key, 0)

            if current_time - timestamp > self.ttl:
                # Remove expired item
                del self.cache[key]
                del self.timestamps[key]
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            # Update existing item
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.maxsize:
                # Remove least recently used item
                try:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]
                except (StopIteration, KeyError):
                    pass

        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self):
        self.cache.clear()
        self.timestamps.clear()

    def size(self):
        return len(self.cache)


# Initialize cache instance
component_cache = TTLCache(maxsize=50, ttl=600)  # 10 minutes TTL for components

# Pseudo database with localized strings
LOCALIZATION_DB = {
    "en": {
        "welcome_title": "Welcome to Our App",
        "welcome_subtitle": "Your journey starts here",
        "login_button": "Log In",
        "signup_button": "Sign Up",
        "navigation_home": "Home",
        "navigation_about": "About",
        "navigation_contact": "Contact",
        "footer_copyright": "© 2024 Our Company. All rights reserved.",
        "user_profile_title": "User Profile",
        "user_profile_edit": "Edit Profile",
        "settings_title": "Settings",
        "settings_language": "Language",
        "settings_theme": "Theme",
        "error_404": "Page not found",
        "error_500": "Internal server error",
    },
    "es": {
        "welcome_title": "Bienvenido a Nuestra App",
        "welcome_subtitle": "Tu viaje comienza aquí",
        "login_button": "Iniciar Sesión",
        "signup_button": "Registrarse",
        "navigation_home": "Inicio",
        "navigation_about": "Acerca de",
        "navigation_contact": "Contacto",
        "footer_copyright": "© 2024 Nuestra Empresa. Todos los derechos reservados.",
        "user_profile_title": "Perfil de Usuario",
        "user_profile_edit": "Editar Perfil",
        "settings_title": "Configuración",
        "settings_language": "Idioma",
        "settings_theme": "Tema",
        "error_404": "Página no encontrada",
        "error_500": "Error interno del servidor",
    },
    "fr": {
        "welcome_title": "Bienvenue dans Notre App",
        "welcome_subtitle": "Votre voyage commence ici",
        "login_button": "Se Connecter",
        "signup_button": "S'inscrire",
        "navigation_home": "Accueil",
        "navigation_about": "À Propos",
        "navigation_contact": "Contact",
        "footer_copyright": "© 2024 Notre Entreprise. Tous droits réservés.",
        "user_profile_title": "Profil Utilisateur",
        "user_profile_edit": "Modifier le Profil",
        "settings_title": "Paramètres",
        "settings_language": "Langue",
        "settings_theme": "Thème",
        "error_404": "Page non trouvée",
        "error_500": "Erreur interne du serveur",
    },
    "de": {
        "welcome_title": "Willkommen in Unserer App",
        "welcome_subtitle": "Ihre Reise beginnt hier",
        "login_button": "Anmelden",
        "signup_button": "Registrieren",
        "navigation_home": "Startseite",
        "navigation_about": "Über Uns",
        "navigation_contact": "Kontakt",
        "footer_copyright": "© 2024 Unser Unternehmen. Alle Rechte vorbehalten.",
        "user_profile_title": "Benutzerprofil",
        "user_profile_edit": "Profil Bearbeiten",
        "settings_title": "Einstellungen",
        "settings_language": "Sprache",
        "settings_theme": "Design",
        "error_404": "Seite nicht gefunden",
        "error_500": "Interner Serverfehler",
    },
}

# React Component Templates with data attributes
COMPONENT_TEMPLATES = {
    "welcome": {
        "component_name": "WelcomeComponent",
        "component_type": "functional",
        "template": """
import React from 'react';

const WelcomeComponent = ({ className = "welcome-container" }) => {
  return (
    <div className={className}>
      <div className="welcome-wrapper">
        <header className="welcome-header">
          <h1 className="welcome-title" data-l10n="welcome_title">
            {l10n.welcome_title}
          </h1>
          <p className="welcome-subtitle" data-l10n="welcome_subtitle">
            {l10n.welcome_subtitle}
          </p>
        </header>
        <div className="welcome-actions">
          <button 
            className="btn btn-primary" 
            onClick={handleLogin}
            data-l10n="login_button"
          >
            {l10n.login_button}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={handleSignup}
            data-l10n="signup_button"
          >
            {l10n.signup_button}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeComponent;
""",
        "required_keys": [
            "welcome_title",
            "welcome_subtitle",
            "login_button",
            "signup_button",
        ],
    },
    "navigation": {
        "component_name": "NavigationComponent",
        "component_type": "functional",
        "template": """
import React from 'react';

const NavigationComponent = ({ className = "navigation-container" }) => {
  return (
    <nav className={className}>
      <ul className="nav-list">
        <li className="nav-item">
          <a href="/" className="nav-link" data-l10n="navigation_home">
            {l10n.navigation_home}
          </a>
        </li>
        <li className="nav-item">
          <a href="/about" className="nav-link" data-l10n="navigation_about">
            {l10n.navigation_about}
          </a>
        </li>
        <li className="nav-item">
          <a href="/contact" className="nav-link" data-l10n="navigation_contact">
            {l10n.navigation_contact}
          </a>
        </li>
      </ul>
    </nav>
  );
};

export default NavigationComponent;
""",
        "required_keys": ["navigation_home", "navigation_about", "navigation_contact"],
    },
    "user_profile": {
        "component_name": "UserProfileComponent",
        "component_type": "functional",
        "template": """
import React from 'react';

const UserProfileComponent = ({ className = "user-profile-container" }) => {
  return (
    <div className={className}>
      <div className="profile-wrapper">
        <h2 className="profile-title" data-l10n="user_profile_title">
          {l10n.user_profile_title}
        </h2>
        <div className="profile-actions">
          <button 
            className="btn btn-outline" 
            onClick={handleEditProfile}
            data-l10n="user_profile_edit"
          >
            {l10n.user_profile_edit}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfileComponent;
""",
        "required_keys": ["user_profile_title", "user_profile_edit"],
    },
    "footer": {
        "component_name": "FooterComponent",
        "component_type": "functional",
        "template": """
import React from 'react';

const FooterComponent = ({ className = "footer-container" }) => {
  return (
    <footer className={className}>
      <div className="footer-content">
        <p className="footer-copyright" data-l10n="footer_copyright">
          {l10n.footer_copyright}
        </p>
      </div>
    </footer>
  );
};

export default FooterComponent;
""",
        "required_keys": ["footer_copyright"],
    },
}


def interpolate_template(template: str, localized_data: dict) -> str:
    """Interpolate template with localized data"""
    # Replace {l10n.key} patterns with actual localized values
    for key, value in localized_data.items():
        pattern = r"\{l10n\." + re.escape(key) + r"\}"
        template = re.sub(pattern, f'"{value}"', template)

    return template


def get_localized_component(component_type: str, lang: str) -> dict:
    """Get a localized React component based on template and language"""

    if component_type not in COMPONENT_TEMPLATES:
        raise ValueError(f"Component type '{component_type}' not found")

    template_data = COMPONENT_TEMPLATES[component_type]
    strings = LOCALIZATION_DB.get(lang, LOCALIZATION_DB["en"])

    # Get only the required keys for this component
    required_keys = template_data["required_keys"]
    component_strings = {key: strings.get(key, f"[{key}]") for key in required_keys}

    localized_template = interpolate_template(
        template_data["template"], component_strings
    )

    component_id = f"{component_type}_{lang}_{int(time.time() * 1000) % 10000}"

    return {
        "component_name": template_data["component_name"],
        "component_type": template_data["component_type"],
        "language": lang,
        "template": localized_template,
        "localized_data": component_strings,
        "metadata": {
            "component_id": component_id,
            "last_updated": "2024-01-15T10:30:00Z",
            "required_keys": required_keys,
        },
    }


@app.get("/health")
async def health_check(concurrency: None = Depends(limit_concurrency)):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "localization-manager-backend",
        "version": "0.1.0",
        "cache_size": component_cache.size(),
        "concurrency_limit": CONCURRENCY_LIMIT,
    }


@app.get("/api/component/{component_type}")
async def get_localized_component_endpoint(
    component_type: str,
    lang: str = Query(default="en", description="Language code (en, es, fr, de)"),
    concurrency: None = Depends(limit_concurrency),
):
    """Returns a localized React component based on template and language"""

    cache_key = f"component:{component_type}:{lang}"

    cached_result = component_cache.get(cache_key)
    if cached_result:
        return {**cached_result, "cached": True}

    try:
        component = get_localized_component(component_type, lang)

        component_cache.put(cache_key, component)

        return {**component, "cached": False}
    except ValueError as e:
        return {
            "error": str(e),
            "available_components": list(COMPONENT_TEMPLATES.keys()),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
