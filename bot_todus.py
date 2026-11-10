#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from todus import ToDusClient2

# --- CONFIGURACIÓN HARDCODEADA ---
MI_TELEFONO = "5351417372"
MI_TOKEN = "TU_TOKEN_DE_96_CARACTERES_AQUI"  # Pega aquí tu token real

API_URL = "https://webapi.labolitacubana.com/results"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://www.labolitacubana.com",
    "Referer": "https://www.labolitacubana.com/",
    "X-Requested-With": "XMLHttpRequest",
}


def obtener_tirada_texto():
    """Consulta la API y devuelve el mensaje formateado en HTML."""
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        last = data.get("last", {})

        fecha_iso = last.get("date", "")
        fijo_m = last.get("pick3Midday") or "N/D"
        corr_m = last.get("pick4Midday") or "N/D"
        fijo_n = last.get("pick3Evening")
        corr_n = last.get("pick4Evening")

        try:
            fecha = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00")).strftime("%d/%m/%Y")
        except Exception:
            fecha = fecha_iso

        msg = "🎰 <b>RESULTADOS LA BOLITA</b>\n"
        msg += f"📅 Fecha: {fecha}\n"
        msg += "--------------------\n"
        msg += "☀️ <b>MEDIODÍA</b>\n"
        msg += f"   Fijo: <code>{fijo_m}</code>\n"
        msg += f"   Corridos: <code>{corr_m}</code>\n"
        msg += "--------------------\n"
        msg += "🌙 <b>NOCHE</b>\n"
        if fijo_n and corr_n:
            msg += f"   Fijo: <code>{fijo_n}</code>\n"
            msg += f"   Corridos: <code>{corr_n}</code>\n"
        else:
            msg += "   ⏳ Aún no disponible\n"
        return msg
    except Exception as e:
        return f"❌ Error: {e}"


def on_message(msg):
    remitente = msg.get("from", "").split("@")[0]
    cuerpo = msg.get("body", "").strip().lower()

    if not cuerpo or remitente == MI_TELEFONO:
        return

    if "tirada" in cuerpo:
        print(f"[{datetime.now().strftime('%H:%M')}] Solicitud de {remitente}")
        respuesta = obtener_tirada_texto()
        client.send_message_queued(remitente, respuesta, parse_mode="HTML")
        print("   -> Respuesta enviada (HTML).")


if __name__ == "__main__":
    print("🤖 Iniciando cliente ToDus...")

    try:
        # El token largo de 96 caracteres va como 'password'
        client = ToDusClient2(MI_TELEFONO, password=MI_TOKEN)
        client.login()
        print(f"✅ Conectado como {MI_TELEFONO}")
        print("👂 Escuchando mensajes...")
        client.listen_messages(client.token, on_message)
    except Exception as e:
        print(f"❌ Error: {e}")
