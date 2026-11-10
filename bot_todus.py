#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
from datetime import datetime
from todus import ToDusClientWithQueue

# --- CONFIGURACIÓN ---
MI_TELEFONO = "5351417372"
MI_TOKEN = os.environ.get("TODUS_TOKEN", "TU_TOKEN_DE_96_CARACTERES_AQUI")

API_URL = "https://webapi.labolitacubana.com/results"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.labolitacubana.com",
    "Referer": "https://www.labolitacubana.com/",
    "X-Requested-With": "XMLHttpRequest",
}

def obtener_tirada_texto():
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

        msg = "🎰 RESULTADOS LA BOLITA\n"
        msg += f"📅 Fecha: {fecha}\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        msg += "☀️ MEDIODÍA\n"
        msg += f"   🔢 Fijo: {fijo_m}\n"
        msg += f"   🔢 Corridos: {corr_m}\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        msg += "🌙 NOCHE\n"
        if fijo_n and corr_n:
            msg += f"   🔢 Fijo: {fijo_n}\n"
            msg += f"   🔢 Corridos: {corr_n}\n"
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
        print(f"[INFO] Solicitud válida de {remitente}")
        respuesta = obtener_tirada_texto()
        client.send_message_queued(remitente, respuesta)
        print("[INFO] Respuesta enviada")

if __name__ == "__main__":
    print("🤖 Iniciando cliente ToDus con cola...")
    client = ToDusClientWithQueue(MI_TELEFONO, MI_TOKEN)
    client.login()
    print(f"✅ Conectado como {MI_TELEFONO}")
    print("👂 Escuchando mensajes...")
    
    # Ejecutamos el listener en un hilo separado para poder controlar el tiempo
    import threading
    hilo = threading.Thread(target=client.listen_messages, args=(client.token, on_message), daemon=True)
    hilo.start()
    
    # Mantener vivo el proceso durante 5 horas (18,000 segundos)
    print("⏳ El bot estará activo por 5 horas...")
    time.sleep(18000)
    print("⏹️ Tiempo cumplido. Cerrando bot.")
