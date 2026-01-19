import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    is_production = (
        os.environ.get("SUPABASE_URL") == "prod" or 
        not os.path.exists(".env") or
        "reflex.dev" in os.environ.get("HOSTNAME", "")
    )

    if is_production:
        """Crea y retorna cliente de Supabase para producción."""
        SUPABASE_URL = "https://wxjknxpyqgxxjtrkuyev.supabase.co"
        SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4amtueHB5cWd4eGp0cmt1eWV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNTIxNDAsImV4cCI6MjA3MzcyODE0MH0.DG7NmFC7LyMC5iGpfyvIIYliNlFMQtcJofzo2gWTwm8"
    else:
        """Crea y retorna cliente de Supabase para desarrollo."""
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY requeridas en .env")

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase = get_supabase_client()
