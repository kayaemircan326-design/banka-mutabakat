import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

st.set_page_config(page_title="Banka & Fatura Mutabakat Toolu", layout="wide", page_icon="📊")

# --- GÖZ YORMAYAN ÖZEL TEMA VE SAĞ ALT İMZA (CUSTOM CSS) ---
st.markdown(
    """
    <style>
    /* Genel Arka Plan ve Yazı Rengi (Soft Dark Theme) */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Yan Menü (Sidebar) Arka Planı */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Metin Kutuları ve Kart Tasarımları */
    div[data-testid="stMetricValue"] {
        color: #58A6FF !important;
    }
    
    /* Buton Tasarımı */
    div.stButton > button:first-child {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #2EA043;
        border: none;
    }

    /* Sağ Alt Köşe BilalTuran İmzası */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #8B949E;
        text-align: right;
        padding-right: 25px;
        padding-bottom: 12px;
        font-size: 13px;
        font-weight: 600;
        pointer-events: none;
        z-index: 100;
        letter-spacing: 0.5px;
    }
    </style>
    <div class="footer">
        BilalTuran
    </div>
    """,
    unsafe_allow_html=True
)

# --- BAŞLIK BÖLÜMÜ ---
st.title("📊 Akıllı Banka Ekstresi & Fatura Mutabakat Raporu")
st.caption("Aralıklı damga vergisi süzgeci ile otomatik mutabakat sistemi")

st.markdown("---")

# --- SIDEBAR (PARAMETRELER) ---
st.sidebar.header("⚙️ Eşleştirme Parametreleri")

fuzzy_threshold = st.sidebar.slider("İsim Benzerlik Eşiği (%)", min_value=30, max_value=100, value=60, step=5)

st.sidebar.subheader("📐 Damga Vergisi Aralığı (%)")
min_damga_pct = st.sidebar.number_input("Min. Damga Vergisi (%)", min_value=0.0, max_value=5.0, value=0.70, step=0.05, format="%.2f")
max_damga_pct = st.sidebar.number_input("Maks. Damga Vergisi (%)", min_value=0.0, max_value=5.0, value=1.00, step=0.05, format="%.2f")

tolerance_amount = st.sidebar.number_input("Maksimum Tolerans Tutarı (TL)", min_value=0.0, value=500.0, step=50.0)

# --- DOSYA YÜKLEME ---
col1, col2 = st.columns(2)

with col1:
    bank_file = st.file_uploader("🏦 Banka Ekstresi Yükle", type=["xlsx", "xls", "csv"])

with col2:
    invoice_file = st.file_uploader("📄 Fatura Listesi Yükle", type=["xlsx", "xls", "csv"])

def load_data(file):
    if file is None:
        return None
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def find_column(cols, keywords, default_idx=0):
    for col in cols:
        col_str = str(col).lower()
        if any(kw in col_str for kw in keywords):
            return col
    return cols[default_idx] if cols else None

df_bank = load_data(bank_file)
df_inv = load_data(invoice_file)

if df_bank is not None and df_inv is not None:
    st.success("Her iki dosya da başarıyla yüklendi!")
    
    bank_cols = df_bank.columns.tolist()
    inv_cols = df_inv.columns.tolist()

    col_b_desc = find_column(bank_cols, ["açıklama", "aciklama", "dekont", "detay", "narration", "description"])
    col_b_amt = find_column(bank_cols, ["tutar", "miktar", "amount", "bakiye"])

    col_i_vendor = find_column(inv_cols, ["firma", "cari", "müşteri", "musteri", "unvan", "ünvan", "vendor", "party"])
    col_i_amt = find_column(inv_cols, ["tutar", "genel toplam", "toplam", "amount"])
    col_i_no = find_column(inv_cols, ["fatura no", "faturano", "fatura_no", "belge no", "no", "invoice"])

    if st.button("🚀 Mutabakatı Çalıştır ve Raporla"):
        results = []
        inv_df_work = df_inv.copy()
        inv_df_work['matched'] = False

        for b_idx, b_row in df_bank.iterrows():
            b_desc = str(b_row[col_b_desc]) if col_b_desc and pd.notnull(b_row[col_b_desc]) else ""
            try:
                b_amt = abs(float(b_row[col_b_amt]))
            except:
                b_amt = 0.0

            matched_row = None
            status = "Eşleşmedi ❌"
            reason = "Uyumlu fatura bulunamadı."
            match_type = "-"

            # 1. AŞAMA: Fatura No Birebir Geçiyor mu?
            if col_i_no:
                for i_idx, i_row in inv_df_work[~inv_df_work['matched']].iterrows():
                    i_no = str(i_row[col_i_no]).strip()
                    if i_no and len(i_no) > 3 and i_no.lower() in b_desc.lower():
                        matched_row = i_row
                        status = "Eşleşti ✅"
                        reason = "Fatura No birebir uyuşuyor."
                        match_type = "Fatura No"
                        inv_df_work.at[i_idx, 'matched'] = True
                        break

            # 2. AŞAMA: İsim + Tutar (Aralıklı Damga Vergisi Kontrolü)
            if matched_row is None and col_i_vendor and col_i_amt:
                for i_idx, i_row in inv_df_work[~inv_df_work['matched']].iterrows():
                    i_vendor = str(i_row[col_i_vendor]) if pd.notnull(i_row[col_i_vendor]) else ""
                    try:
                        i_amt = abs(float(i_row[col_i_amt]))
                    except:
                        i_amt = 0.0

                    amt_diff = abs(b_amt - i_amt)
                    amt_diff_pct = (amt_diff / i_amt * 100) if i_amt > 0 else 999
                    score = fuzz.partial_ratio(i_vendor.lower(), b_desc.lower())

                    if score >= fuzzy_threshold:
                        if amt_diff == 0:
                            matched_row = i_row
                            status = "Eşleşti ✅"
                            reason = "Firma adı ve tutar birebir uyuşuyor."
                            match_type = "İsim + Tam Tutar"
                            inv_df_work.at[i_idx, 'matched'] = True
                            break
                        elif min_damga_pct <= amt_diff_pct <= max_damga_pct and amt_diff <= tolerance_amount:
                            matched_row = i_row
                            status = "Eşleşti ✅"
                            reason = f"Firma adı uyumlu, kesinti (%{amt_diff_pct:.2f}) damga vergisi aralığında (%{min_damga_pct:.2f} - %{max_damga_pct:.2f})."
                            match_type = "İsim + Damga Vergisi Aralığı"
                            inv_df_work.at[i_idx, 'matched'] = True
                            break
                        elif (min_damga_pct - 0.3) <= amt_diff_pct <= (max_damga_pct + 0.3) and amt_diff <= tolerance_amount:
                            matched_row = i_row
                            status = "Şüpheli / Kontrol Edilecek ⚠️"
                            reason = f"Firma adı uyumlu fakat kesinti oranı (%{amt_diff_pct:.2f}) belirlenen aralığa (%{min_damga_pct:.2f} - %{max_damga_pct:.2f}) sadece yakın."
                            match_type = "İsim + Yakın Kesinti"
                            inv_df_work.at[i_idx, 'matched'] = True
                            break

            # 3. AŞAMA: Sadece Tutar (Açıklamada Firma İsmi Yoksa)
            if matched_row is None and col_i_amt:
                for i_idx, i_row in inv_df_work[~inv_df_work['matched']].iterrows():
                    try:
                        i_amt = abs(float(i_row[col_i_amt]))
                    except:
                        i_amt = 0.0

                    amt_diff = abs(b_amt - i_amt)
                    amt_diff_pct = (amt_diff / i_amt * 100) if i_amt > 0 else 999

                    if (amt_diff == 0 or (min_damga_pct <= amt_diff_pct <= max_damga_pct)) and amt_diff <= tolerance_amount:
                        matched_row = i_row
                        status = "Şüpheli / Kontrol Edilecek ⚠️"
                        reason = f"Tutar kesintisi (%{amt_diff_pct:.2f}) damga vergisi aralığıyla uyumlu fakat banka açıklamasında firma ismi yok!"
                        match_type = "Yalnızca Tutar"
                        inv_df_work.at[i_idx, 'matched'] = True
                        break

            # Sonuçları Kaydet
            if matched_row is not None:
                i_amt_val = abs(float(matched_row[col_i_amt]))
                diff_val = round(abs(b_amt - i_amt_val), 2)
                vendor_val = matched_row[col_i_vendor] if col_i_vendor else "-"
                no_val = matched_row[col_i_no] if col_i_no else "-"
                
                results.append({
                    "Durum": status,
                    "Şüphe / Açıklama Sebebi": reason,
                    "Banka Açıklama": b_desc,
                    "Banka Tutar (TL)": f"{b_amt:,.2f}",
                    "Eşleşen Firma": vendor_val,
                    "Eşleşen Fatura No": no_val,
                    "Fatura Tutar (TL)": f"{i_amt_val:,.2f}",
                    "Fark (TL)": f"{diff_val:,.2f}",
                    "Eşleşme Mantığı": match_type
                })
            else:
                results.append({
                    "Durum": status,
                    "Şüphe / Açıklama Sebebi": reason,
                    "Banka Açıklama": b_desc,
                    "Banka Tutar (TL)": f"{b_amt:,.2f}",
                    "Eşleşen Firma": "-",
                    "Eşleşen Fatura No": "-",
                    "Fatura Tutar (TL)": "-",
                    "Fark (TL)": "-",
                    "Eşleşme Mantığı": "-"
                })

        st.session_state['res_df'] = pd.DataFrame(results)

# --- SONUÇLARI GÖSTERME VE FİLTRELEME ALANI ---
if 'res_df' in st.session_state:
    res_df = st.session_state['res_df']
    
    st.markdown("---")
    st.subheader("🎯 Mutabakat Özet Raporu")
    
    cnt_success = len(res_df[res_df["Durum"] == "Eşleşti ✅"])
    cnt_warning = len(res_df[res_df["Durum"] == "Şüpheli / Kontrol Edilecek ⚠️"])
    cnt_fail = len(res_df[res_df["Durum"] == "Eşleşmedi ❌"])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Kesin Eşleşen", cnt_success)
    m2.metric("Şüpheli / Kontrol Edilecek", cnt_warning)
    m3.metric("Eşleşmeyen", cnt_fail)
    
    st.markdown("---")
    st.subheader("📋 Detaylı Mutabakat Listesi")

    # Güvenli Filtreleme Formu (Sayfa Çökmesini Engeller)
    with st.form("filter_form"):
        f_col1, f_col2 = st.columns([3, 1])
        
        with f_col1:
            selected_statuses = st.multiselect(
                "Listelenecek Durumları Seçin:", 
                ["Eşleşti ✅", "Şüpheli / Kontrol Edilecek ⚠️", "Eşleşmedi ❌"],
                default=["Eşleşti ✅", "Şüpheli / Kontrol Edilecek ⚠️", "Eşleşmedi ❌"]
            )
            
        with f_col2:
            st.write(" ")
            st.write(" ")
            apply_filter = st.form_submit_button("🔍 Filtreyi Uygula")

    # Filtre Kontrolü (Hata Önleyici)
    if not selected_statuses:
        st.warning("⚠️ Lütfen tablonun görünebilmesi için en az bir durum seçin ve 'Filtreyi Uygula' butonuna basın.")
    else:
        filtered_df = res_df[res_df["Durum"].isin(selected_statuses)]
        st.dataframe(filtered_df, use_container_width=True)