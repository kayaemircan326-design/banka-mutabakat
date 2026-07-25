import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Sayfa ayarları
st.set_page_config(
    page_title="Banka and Fatura Mutabakat Uygulaması", layout="wide"
)

# --- KİMLİK DOĞRULAMA AYARLARI ---
with open("config.yaml") as file:
  config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Giriş ekranını oluştur
try:
  authenticator.login()
except Exception as e:
  # Alternatif sürüm çağrısı için güvenli blok
  pass

# Giriş durumlarını kontrol et
if st.session_state.get("authentication_status") == False:
  st.error("Kullanıcı adı veya şifre yanlış")
elif st.session_state.get("authentication_status") == None:
  st.warning("Lütfen kullanıcı adı ve şifrenizi girin")
elif st.session_state.get("authentication_status") == True:
  # --- GİRİŞ BAŞARILIYSA ---
  authenticator.logout("Çıkış Yap", "sidebar")
  st.sidebar.write(f"Hoş geldin, **{st.session_state.get('name')}**!")

  # BURADAN İTİBAREN SENİN MEVCUT MUTABAKAT KODLARIN BAŞLIYOR:
  st.title("📊 Banka ve Fatura Mutabakat Paneli")
  st.info("Sistem başarıyla açıldı!")
