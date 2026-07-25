import pandas as pd
import streamlit as st

# Sayfa ayarları
st.set_page_config(
    page_title="Banka ve Fatura Mutabakat Uygulaması", layout="wide"
)

# Oturum durumunu başlat
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False

# Giriş Ekranı
if not st.session_state["logged_in"]:
  st.title("📊 Banka ve Fatura Mutabakat Paneli")
  st.subheader("Lütfen Giriş Yapın")

  username = st.text_input("Kullanıcı Adı")
  password = st.text_input("Şifre", type="password")

  if st.button("Giriş Yap"):
    if username == "Bilal.turan21" and password == "ervayıçokseviyorum":
      st.session_state["logged_in"] = True
      st.rerun()
    else:
      st.error("Kullanıcı adı veya şifre yanlış!")

# Giriş Başarılı Olduktan Sonra Açılacak Asıl Uygulama
else:
  st.sidebar.success("Giriş Başarılı!")
  if st.sidebar.button("Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.rerun()

  st.title("📊 Banka ve Fatura Mutabakat Paneli")
  st.write("Hoş geldin Bilal! Mutabakat işlemlerini buradan yönetebilirsin.")

  st.divider()

  # Dosya Yükleme Alanları
  col1, col2 = st.columns(2)

  with col1:
    st.subheader("1. Banka Ekstresi Yükle")
    bank_file = st.file_uploader(
        "Banka dosyasını seç (Excel/CSV)", type=["xlsx", "csv"], key="bank"
    )

  with col2:
    st.subheader("2. Fatura Listesi Yükle")
    invoice_file = st.file_uploader(
        "Fatura dosyasını seç (Excel/CSV)", type=["xlsx", "csv"], key="invoice"
    )

  # Dosyalar yüklendiyse önizleme ve işlem alanı
  if bank_file and invoice_file:
    st.success("Dosyalar başarıyla yüklendi!")

    try:
      # Dosyaları oku (Uzantıya göre otomatik ayar)
      if bank_file.name.endswith(".csv"):
        df_bank = pd.read_csv(bank_file)
      else:
        df_bank = pd.read_excel(bank_file)

      if invoice_file.name.endswith(".csv"):
        df_invoice = pd.read_csv(invoice_file)
      else:
        df_invoice = pd.read_excel(invoice_file)

      st.subheader("Banka Ekstresi Önizlemesi")
      st.dataframe(df_bank.head())

      st.subheader("Fatura Listesi Önizlemesi")
      st.dataframe(df_invoice.head())

      if st.button("Mutabakatı Başlat"):
        st.info(
            "Mutabakat algoritması çalıştırılıyor... (Buraya kendi eşleştirme"
            " kodlarını ekleyebilirsin)"
        )
        # Örnek eşleştirme çıktısı veya mantığı buraya gelebilir

    except Exception as e:
      st.error(f"Dosyalar okunurken bir hata oluştu: {e}")
  else:
    st.info(
        "Devam etmek için lütfen her iki dosyayı da (Banka ve Fatura) yukarıdan"
        " yükleyin."
    )
      
