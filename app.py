import streamlit as st
import yaml
from yaml.loader import SafeLoader

# Sayfa ayarları
st.set_page_config(
    page_title="Banka ve Fatura Mutabakat Uygulaması", layout="wide"
)

# Basit kullanıcı kontrolü (Hash hatası vermez)
st.title("📊 Banka ve Fatura Mutabakat Paneli")

# Oturum durumunu başlat
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
  st.subheader("Lütfen Giriş Yapın")
  username = st.text_input("Kullanıcı Adı")
  password = st.text_input("Şifre", type="password")

  if st.button("Giriş Yap"):
    if username == "Bilal.turan21" and password == "ervayıçokseviyorum":
      st.session_state["logged_in"] = True
      st.rerun()
    else:
      st.error("Kullanıcı adı veya şifre yanlış!")
else:
  st.sidebar.success("Giriş Başarılı!")
  if st.sidebar.button("Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.rerun()

  # --- BURADAN İTİBAREN ASIL UYGULAMAN BAŞLIYOR ---
  st.write("Hoş geldin Bilal! Sistem başarıyla açıldı.")
