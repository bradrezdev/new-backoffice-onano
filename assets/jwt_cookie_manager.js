/**
 * Utilidades para manejo de cookies JWT
 * ====================================
 *
 * Este archivo contiene funciones JavaScript para manejar cookies
 * de autenticación JWT del lado del cliente.
 */

class JWTCookieManager {
    constructor() {
        this.cookieName = 'auth_token'; // Unificado con AuthState
        this.cookieOptions = {
            path: '/',
            secure: window.location.protocol === 'https:',
            sameSite: 'lax', // Lax es mas compatible con navegacion
            maxAge: 86400  // 24 horas
        };
    }

    /**
     * Establece la cookie de autenticación con el token JWT
     * @param {string} token - Token JWT de acceso
     */
    setAuthCookie(token) {
        const cookieValue = `${this.cookieName}=${token}`;
        const options = Object.entries(this.cookieOptions)
            .map(([key, value]) => {
                if (key === 'maxAge') return `max-age=${value}`;
                if (key === 'secure' && value) return 'secure';
                if (key === 'sameSite') return `samesite=${value}`;
                return `${key}=${value}`;
            })
            .join('; ');

        document.cookie = `${cookieValue}; ${options}`;
        console.log('Cookie de autenticación establecida');
    }

    /**
     * Obtiene el token JWT de la cookie de autenticación
     * @returns {string|null} Token JWT o null si no existe
     */
    getAuthToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === this.cookieName) {
                return value;
            }
        }
        return null;
    }

    /**
     * Elimina la cookie de autenticación
     */
    clearAuthCookie() {
        document.cookie = `${this.cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
        console.log('Cookie de autenticación eliminada');
    }

    /**
     * Verifica si hay un token válido en la cookie
     * @returns {boolean} True si hay un token válido
     */
    hasValidToken() {
        const token = this.getAuthToken();
        if (!token) return false;

        try {
            // Decodificar el payload del JWT (sin verificar firma)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);

            // Verificar si el token ha expirado
            return payload.exp > currentTime;
        } catch (error) {
            console.error('Error al verificar token:', error);
            return false;
        }
    }

    /**
     * Obtiene el tiempo restante del token en segundos
     * @returns {number} Segundos restantes o 0 si expirado/no existe
     */
    getTokenTimeRemaining() {
        const token = this.getAuthToken();
        if (!token) return 0;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            const remaining = payload.exp - currentTime;
            return remaining > 0 ? remaining : 0;
        } catch (error) {
            return 0;
        }
    }

    /**
     * Configura un temporizador para renovar el token antes de que expire
     * @param {Function} onExpire - Función a llamar cuando el token expire
     */
    setupTokenRefreshTimer(onExpire) {
        const checkToken = () => {
            const remaining = this.getTokenTimeRemaining();

            if (remaining <= 0) {
                // Token expirado
                this.clearAuthCookie();
                if (onExpire) onExpire();
                return;
            }

            // Verificar nuevamente en 30 segundos o cuando falten 30 segundos
            const nextCheck = Math.min(30, remaining - 30);
            if (nextCheck > 0) {
                setTimeout(checkToken, nextCheck * 1000);
            } else {
                // Token expira pronto, verificar más frecuentemente
                setTimeout(checkToken, 5000);
            }
        };

        // Iniciar verificación
        checkToken();
    }
}

// Instancia global del manejador de cookies
const jwtCookieManager = new JWTCookieManager();

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JWTCookieManager;
}