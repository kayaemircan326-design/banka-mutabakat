import io
import pandas as pd
from rapidfuzz import fuzz
import streamlit as st

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Banka & Fatura Mutabakat Sistemi",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- KULLANICI GİRİŞ (AUTH) KONTROLÜ ---
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False


def check_credentials():
  username = st.session_state.get("username_input", "")
  password = st.session_state.get("password_input", "")
  if username == "Bilal.turan21" and password == "ervayıçokseviyorum":
    st.session_state["authenticated"] = True
  else:
    st.session_state["login_error"] = True


if not st.session_state["authenticated"]:
  col1, col2, col3 = st.columns([1, 1.5, 1])
  with col2:
    st.markdown("### 🔐 Özel Giriş Paneli")
    st.text_input("Kullanıcı Adı", key="username_input")
    st.text_input("Şifre", type="password", key="password_input")
    st.button(
        "Giriş Yap", on_click=check_credentials, use_container_width=True
    )

    if st.session_state.get("login_error", False):
      st.error("Hatalı kullanıcı adı veya şifre!")
  st.stop()

# --- SIDEBAR PARAMETRELERİ ---
st.sidebar.header("⚙️ Mutabakat Ayarları")

fuzzy_threshold = st.sidebar.slider(
    "Fuzzy Eşleşme Eşiği (%)", min_value=50, max_value=100, value=85, step=1
)

st.sidebar.subheader("Damga Vergisi Filtresi (%)")
damga_vergisi_araligi = st.sidebar.slider(
    "Oran Aralığı Seçin",
    min_value=0.70,
    max_value=1.00,
    value=(0.70, 1.00),
    step=0.01,
    format="%.2f",
)
min_damga, max_damga = damga_vergisi_araligi

tolerans_tutar = st.sidebar.number_input(
    "Tutar Tolerans Payı (TL)",
    min_value=0.0,
    max_value=2000.0,
    value=1.0,
    step=10.0,
)

st.sidebar.divider()
st.sidebar.info("Lütfen Banka ve Fatura dosyalarınızı yükleyin.")

# --- SAĞ ALT İMZA ---
st.sidebar.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 10px;
            right: 20px;
            font-size: 12px;
            color: #888888;
            background-color: rgba(0,0,0,0.05);
            padding: 5px 10px;
            border-radius: 5px;
            z-index: 99999;
        }
    </style>
    <div class="footer">Geliştiren: Bilal Turan</div>
    """,
    unsafe_allow_html=True,
)

# --- ANA EKRAN & DOSYA YÜKLEME ---
st.title("⚖️ Banka - Fatura Mutabakat Sistemi")
st.write(
    "Banka hareketleri ile faturalarınızı otomatik eşleştirin, karşılıksız"
    " ödemeleri ve eksik kayıtları yönetin."
)

col_b, col_f = st.columns(2)

with col_b:
  st.subheader("1. Banka Ekstresi Yükle")
  banka_file = st.file_uploader(
      "Banka Dosyası (Excel / CSV)", type=["xlsx", "csv"], key="banka"
  )

with col_f:
  st.subheader("2. Fatura Listesi Yükle")
  fatura_file = st.file_uploader(
      "Fatura Dosyası (Excel / CSV)", type=["xlsx", "csv"], key="fatura"
  )

# --- MUTABAKAT MOTORU ---
if banka_file and fatura_file:
  try:
    if banka_file.name.endswith(".csv"):
      df_banka = pd.read_csv(banka_file)
    else:
      df_banka = pd.read_excel(banka_file)

    if fatura_file.name.endswith(".csv"):
      df_fatura = pd.read_csv(fatura_file)
    else:
      df_fatura = pd.read_excel(fatura_file)

    # Sütun isimlerindeki boşlukları temizle
    df_banka.columns = [str(c).strip() for c in df_banka.columns]
    df_fatura.columns = [str(c).strip() for c in df_fatura.columns]

    st.success("Dosyalar başarıyla yüklendi! Lütfen sütunları seçin:")

    col_s1, col_s2 = st.columns(2)

    fatura_kolonlar = list(df_fatura.columns)
    banka_kolonlar = list(df_banka.columns)

    with col_s1:
      st.markdown("#### 📄 Fatura Sütunları")
      f_tarih_col = st.selectbox(
          "Tarih Sütunu (Fatura)", fatura_kolonlar, key="f_tarih"
      )
      f_cari_col = st.selectbox(
          "Cari Sütunu (Fatura)", fatura_kolonlar, key="f_cari"
      )
      f_kurum_col = st.selectbox(
          "Kurum Adı Sütunu (Fatura)", fatura_kolonlar, key="f_kurum"
      )
      f_tutar_col = st.selectbox(
          "Tutar Sütunu (Fatura)", fatura_kolonlar, key="f_tutar"
      )
      f_aciklama_col = st.selectbox(
          "Açıklama Sütunu (Fatura)", fatura_kolonlar, key="f_aciklama"
      )

    with col_s2:
      st.markdown("#### 🏦 Banka Sütunları (Manuel Eşleşme İçin)")
      b_tarih_col = st.selectbox(
          "Tarih Sütunu (Banka)", banka_kolonlar, key="b_tarih"
      )
      b_cari_col = st.selectbox(
          "Cari Sütunu (Banka)", banka_kolonlar, key="b_cari"
      )
      b_kurum_col = st.selectbox(
          "Kurum / Gönderen Adı Sütunu (Banka)", banka_kolonlar, key="b_kurum"
      )
      b_tutar_col = st.selectbox(
          "Tutar Sütunu (Banka)", banka_kolonlar, key="b_tutar"
      )
      b_aciklama_col = st.selectbox(
          "Açıklama Sütunu (Banka)", banka_kolonlar, key="b_aciklama"
      )

    if st.button("🚀 Mutabakatı Başlat", use_container_width=True):
      with st.spinner("Eşleştirmeler yapılıyor..."):

        sonuc_listesi = []
        karsiliksiz_listesi = []
        eslesen_banka_indeksleri = set()

        for idx, fatura in df_fatura.iterrows():
          f_kurum_raw = fatura[f_kurum_col]
          if pd.isna(f_kurum_raw):
            continue
          f_kurum = str(f_kurum_raw).strip()
          if not f_kurum or f_kurum.lower() == "nan":
            continue

          f_tarih = fatura.get(f_tarih_col, "-")
          f_cari = fatura.get(f_cari_col, "-")
          f_ack = fatura.get(f_aciklama_col, "-")

          try:
            f_tutar = float(
                str(fatura[f_tutar_col]).replace(",", "").strip()
            )
          except:
            f_tutar = 0.0

          eslesti_mi = False
          en_iyi_eslesen_banka = None
          durum = ""
          aciklama = ""

          for b_idx, banka in df_banka.iterrows():
            if b_idx in eslesen_banka_indeksleri:
              continue

            b_kurum_raw = banka[b_kurum_col]
            if pd.isna(b_kurum_raw):
              continue
            b_kurum = str(b_kurum_raw).strip()
            if not b_kurum or b_kurum.lower() == "nan":
              continue

            b_tarih = banka.get(b_tarih_col, "-")
            b_cari = banka.get(b_cari_col, "-")
            b_ack = banka.get(b_aciklama_col, "-")

            try:
              b_tutar = float(str(banka[b_tutar_col]).replace(",", "").strip())
            except:
              b_tutar = 0.0

            benzerlik = fuzz.ratio(f_kurum.lower(), b_kurum.lower())

            beklenen_min_tutar = f_tutar * (1.00 - max_damga) - tolerans_tutar
            beklenen_max_tutar = f_tutar * (1.00 - min_damga) + tolerans_tutar

            tutar_uyuyor_mu = (b_tutar >= f_tutar - tolerans_tutar) or (
                beklenen_min_tutar <= b_tutar <= beklenen_max_tutar
            )

            if benzerlik >= fuzzy_threshold and tutar_uyuyor_mu:
              eslesti_mi = True
              eslesen_banka_indeksleri.add(b_idx)
              durum = "Eşleşti (Mutabık)"
              aciklama = "İsim ve damga vergili tutar tam uyumlu."
              en_iyi_eslesen_banka = (b_tarih, b_cari, b_kurum, b_tutar, b_ack)
              break
            elif benzerlik >= fuzzy_threshold and not tutar_uyuyor_mu:
              eslesti_mi = True
              eslesen_banka_indeksleri.add(b_idx)
              durum = "Şüpheli Eşleşme"
              aciklama = (
                  f"İsim uyumlu (%{benzerlik}), ancak tutar uyuşmuyor. Fatura:"
                  f" {f_tutar} TL, Banka: {b_tutar} TL."
              )
              en_iyi_eslesen_banka = (b_tarih, b_cari, b_kurum, b_tutar, b_ack)
              break
            elif benzerlik < fuzzy_threshold and tutar_uyuyor_mu:
              eslesti_mi = True
              eslesen_banka_indeksleri.add(b_idx)
              durum = "Şüpheli Eşleşme"
              aciklama = (
                  f"Tutar uyumlu, ancak kurum adı benzerliği düşük (%{benzerlik})."
              )
              en_iyi_eslesen_banka = (b_tarih, b_cari, b_kurum, b_tutar, b_ack)
              break

          if eslesti_mi:
            sonuc_listesi.append({
                "Durum": durum,
                "Fatura Tarihi": f_tarih,
                "Fatura Cari": f_cari,
                "Fatura Kurum": f_kurum,
                "Fatura Tutarı": f_tutar,
                "Fatura Açıklama": f_ack,
                "Banka Tarihi": (
                    en_iyi_eslesen_banka[0] if en_iyi_eslesen_banka else "-"
                ),
                "Banka Cari": (
                    en_iyi_eslesen_banka[1] if en_iyi_eslesen_banka else "-"
                ),
                "Banka Kurum": (
                    en_iyi_eslesen_banka[2] if en_iyi_eslesen_banka else "-"
                ),
                "Banka Tutarı": (
                    en_iyi_eslesen_banka[3] if en_iyi_eslesen_banka else 0.0
                ),
                "Banka Açıklama": (
                    en_iyi_eslesen_banka[4] if en_iyi_eslesen_banka else "-"
                ),
                "Eşleşme Durumu / Sebep": aciklama,
            })
          else:
            karsiliksiz_listesi.append({
                "Durum": "Eşleşmeyen (Bankada Karşılığı Yok)",
                "Fatura Tarihi": f_tarih,
                "Fatura Cari": f_cari,
                "Fatura Kurum": f_kurum,
                "Fatura Tutarı": f_tutar,
                "Fatura Açıklama": f_ack,
                "Açıklama": "Bankada karşılığı / eşleşen ödemesi bulunamadı.",
            })

        sonuc_df = pd.DataFrame(sonuc_listesi)
        karsiliksiz_df = pd.DataFrame(karsiliksiz_listesi)

        # --- FİLTRELEME VE GÖSTERİM ---
        st.divider()
        st.subheader("📊 Mutabakat Raporu & Filtreleme")

        tum_kayitlar_listesi = []
        if not sonuc_df.empty:
          tum_kayitlar_listesi.append(sonuc_df)
        if not karsiliksiz_df.empty:
          k_temp = karsiliksiz_df.copy()
          k_temp["Banka Tarihi"] = "-"
          k_temp["Banka Cari"] = "-"
          k_temp["Banka Kurum"] = "-"
          k_temp["Banka Tutarı"] = 0.0
          k_temp["Banka Açıklama"] = "-"
          k_temp["Eşleşme Durumu / Sebep"] = k_temp["Açıklama"]
          tum_kayitlar_listesi.append(k_temp)

        if tum_kayitlar_listesi:
          master_df = pd.concat(tum_kayitlar_listesi, ignore_index=True)

          secilen_durumlar = st.multiselect(
              "🔍 Duruma Göre Filtrele (İstediğiniz kategoriyi seçin veya"
              " tümünü bırakın):",
              options=master_df["Durum"].unique().tolist(),
              default=master_df["Durum"].unique().tolist(),
          )

          filtered_df = master_df[master_df["Durum"].isin(secilen_durumlar)]

          st.dataframe(filtered_df, use_container_width=True)
        else:
          st.info("Gösterilecek kayıt bulunamadı.")

        # --- AYRI AYRI ÖZET KISIMLAR ---
        st.divider()
        col_ozet1, col_ozet2 = st.columns(2)
        with col_ozet1:
          st.markdown("### ✅ Tam Eşleşenler")
          if not sonuc_df.empty:
            mutabik_df = sonuc_df[sonuc_df["Durum"] == "Eşleşti (Mutabık)"]
            st.metric("Mutabık Kayıt Sayısı", len(mutabik_df))
          else:
            st.metric("Mutabık Kayıt Sayısı", 0)

        with col_ozet2:
          st.markdown("### ⚠️ Şüpheli Eşleşmeler")
          if not sonuc_df.empty:
            supheli_df = sonuc_df[sonuc_df["Durum"] == "Şüpheli Eşleşme"]
            st.metric("Şüpheli Kayıt Sayısı", len(supheli_df))
          else:
            st.metric("Şüpheli Kayıt Sayısı", 0)

        st.divider()
        st.markdown(
            "### ❌ Bankada Karşılığı Olmayanlar (Ödemesi Gelmeyenler)"
        )
        if not karsiliksiz_df.empty:
          st.dataframe(karsiliksiz_df, use_container_width=True)
        else:
          st.success("Harika! Bankada karşılığı olmayan eksik kayıt bulunmuyor.")

        # --- EXCEL İNDİRME ---
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
          if not sonuc_df.empty:
            sonuc_df.to_excel(
                writer, sheet_name="Ana_Mutabakat_Raporu", index=False
            )
          if not karsiliksiz_df.empty:
            karsiliksiz_df.to_excel(
                writer, sheet_name="Karsiligi_Olmayanlar", index=False
            )
        buffer.seek(0)

        st.download_button(
            label="📥 Tüm Raporları Excel Olarak İndir",
            data=buffer,
            file_name="detayli_mutabakat_raporu.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )

  except Exception as e:
    st.error(f"Dosya işlenirken bir hata oluştu. Detay: {e}")
else:
  st.warning("Lütfen her iki dosyayı da yükleyin.")