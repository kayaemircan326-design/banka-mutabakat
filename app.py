import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Sayfa ayarları (En başta olmalı)
st.set_page_config(
    page_title="Banka ve Fatura Mutabakat Uygulaması", layout="wide"
)

# --- KİMLİK DOĞRULAMA (AUTHEBTICATION) AYARLARI ---
with open("config.yaml") as file:
  config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Giriş ekranını oluştur
name, authentication_status, username = authenticator.login("Giriş Yap", "main")

if authentication_status == False:
  st.error("Kullanıcı adı veya şifre yanlış")
elif authentication_status == None:
  st.warning("Lütfen kullanıcı adı ve şifrenizi girin")
elif authentication_status:
  # --- GİRİŞ BAŞARILIYSA ÇALIŞACAK UYGULAMA KODLARI ---
  authenticator.logout("Çıkış Yap", "sidebar")
  st.sidebar.write(肃, f"Hoş geldin, **{name}**!")

  # BURADan İTİBAREN SENİN MEVCUT MUTABAKAT KODLARIN BAŞLIYOR:
  st.title("📊 Banka ve Fatura Mutabakat Paneli")

  # Örnek olarak kendi mevcut kodlarını buraya ekleyebilirsin:
  st.info(
      "Sistem başarıyla açıldı! Sol menüden ayarları yapıp dosyalarınızı"
      " yükleyebilirsiniz."
  )

  # (Kendi yazdığın mutabakat arayüzü ve kod blokları buranın altına gelecek)
