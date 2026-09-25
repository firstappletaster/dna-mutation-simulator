```python
import os
import random

import requests
import streamlit as st

st.set_page_config(
    page_title="Genetik & DNA Mutasyon Simülatörü",
    page_icon="🧬",
    layout="centered",
)


def get_hf_token() -> str | None:
    token = os.environ.get("HF_TOKEN")
    if token:
        return token

    try:
        return st.secrets.get("HF_TOKEN")
    except FileNotFoundError:
        return None


HF_TOKEN = get_hf_token()

if not HF_TOKEN:
    st.error(
        "API Anahtarı Bulunamadı! Lütfen Replit Secrets alanına "
        "'HF_TOKEN' ekleyin."
    )
    st.stop()


def mutate_dna(sequence: str, mutation_rate: int) -> tuple[str, int]:
    bases = ["A", "T", "G", "C"]
    sequence_list = list(sequence.upper())
    mutated_count = 0

    for index in range(len(sequence_list)):
        if random.random() < (mutation_rate / 100):
            current_base = sequence_list[index]
            possible_bases = [base for base in bases if base != current_base]
            sequence_list[index] = random.choice(possible_bases)
            mutated_count += 1

    return "".join(sequence_list), mutated_count


def explain_with_huggingface(
    prompt: str,
    model: str = "mistralai/Mistral-7B-Instruct-v0.2",
) -> str:
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model}",
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 550,
                "temperature": 0.7,
            },
            "options": {"wait_for_model": True},
        },
        timeout=120,
    )

    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        return response.text

    if response.status_code >= 400:
        if isinstance(payload, dict) and payload.get("error"):
            raise RuntimeError(payload["error"])
        response.raise_for_status()

    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(payload["error"])

    if isinstance(payload, list) and payload:
        return payload[0].get("generated_text", "")

    if isinstance(payload, dict) and "generated_text" in payload:
        return payload["generated_text"]

    return str(payload)


def explain_genetics(
    original_dna: str,
    mutated_dna: str,
    mutation_count: int,
    simulation_type: str,
) -> str:
    prompt = f"""
Sen uzman bir moleküler biyolog ve genetikçisin.
Bir genetik simülasyonda şu veriler elde edildi:
- Simülasyon Odak Alanı: {simulation_type}
- Orijinal DNA Dizilimi: {original_dna}
- Mutasyona Uğramış DNA Dizilimi: {mutated_dna}
- Toplam Nokta Mutasyonu Sayısı: {mutation_count}

Lütfen bu genetik değişimi şu 3 ana başlık altında analiz et:

1. **Transkripsiyon ve Protein Etkisi:** Bu mutasyon mRNA ve sentezlenecek
   amino asit dizilimini (sessiz, yanlış anlamlı/missense veya anlamsız/nonsense
   mutasyon gibi) nasıl etkileyebilir?

2. **Hücresel ve Fenotipik Sonuçlar:** Bu değişimin hücre çalışması veya
   organizma fenotipi üzerindeki olası etkileri nelerdir?

3. **AP Biyoloji / Sınav Tipi Soru:** Bu mutasyon mekanizmasıyla ilgili bir
   AP Biyoloji düzeyinde örnek soru ve detaylı çözümü oluştur.
"""

    return explain_with_huggingface(prompt)


st.title("🧬 Genetik & DNA Mutasyon Simülatörü")

st.caption(
    "DNA dizilimi girin, mutasyon oranını ayarlayın ve biyolojik "
    "sonuçları yapay zeka ile inceleyin."
)

st.markdown("---")

user_dna = st.text_input(
    "DNA Dizilimi Girin (Sadece A, T, G, C):",
    value="ATGCGATCGATCGATCGATCGATCGATC",
)

mutation_rate = st.slider(
    "Mutasyon Oranı (%)",
    0,
    50,
    10,
)

simulation_type = st.selectbox(
    "Genetik İnceleme Odağı:",
    [
        "Nokta Mutasyonları ve Protein Sentezi",
        "Kanser Genetiği ve Onkogen İfadesi",
        "Popülasyon Genetiği ve Doğal Seçilim",
    ],
)


if st.button("Simülasyonu Çalıştır", use_container_width=True):
    clean_dna = user_dna.upper().strip()
    valid_bases = set("ATGC")

    if not clean_dna or not set(clean_dna).issubset(valid_bases):
        st.error(
            "Lütfen sadece A, T, G ve C harflerinden oluşan geçerli bir DNA yazın!"
        )
    else:
        mutated_dna, mutation_count = mutate_dna(
            clean_dna,
            mutation_rate,
        )

        st.markdown("---")
        st.subheader("1. Simülasyon Çıktıları")

        column_one, column_two = st.columns(2)

        with column_one:
            st.info(f"**Orijinal DNA:**\n`{clean_dna}`")

        with column_two:
            st.warning(f"**Mutasyonlu DNA:**\n`{mutated_dna}`")

        st.metric(
            label="Değişen Baz Sayısı",
            value=f"{mutation_count} adet",
        )

        with st.spinner("AI moleküler biyoloji analizini hazırlıyor..."):
            try:
                ai_analysis = explain_genetics(
                    clean_dna,
                    mutated_dna,
                    mutation_count,
                    simulation_type,
                )

                st.markdown("---")
                st.subheader("2. Biyolojik ve AI Analizi")
                st.markdown(ai_analysis)
                st.success("Simülasyon tamamlandı!")

            except Exception as error:
                st.error(f"Bir hata oluştu: {error}")
```
