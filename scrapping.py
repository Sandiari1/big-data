from youtube_transcript_api import YouTubeTranscriptApi
from pymongo import MongoClient
import re
from collections import Counter

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["present_db"]
col = db["segmen_transkrip"]

# Stopwords bahasa Indonesia
stopwords_id = {
    'yang', 'dan', 'di', 'ke', 'dari', 'pada', 'untuk', 'dengan', 'akan',
    'ini', 'itu', 'adalah', 'atau', 'juga', 'karena', 'sudah', 'sebagai',
    'oleh', 'tidak', 'dalam', 'lebih', 'bisa', 'agar', 'namun', 'bagi',
    'tersebut', 'saat', 'masih', 'telah', 'bahwa', 'hanya', 'saja', 'mereka',
    'kami', 'kita', 'anda', 'saya', 'dia', 'ia', 'apa', 'siapa', 'mengapa',
    'bagaimana', 'kapan', 'dimana', 'jadi', 'lagi', 'lah', 'pun', 'nah',
    'ya', 'oh', 'eh', 'hmm', 'huh', 'wow', 'wah', 'uh', 'ehh', 'ohh', 'yaa',
    'nahh', 'pun', 'pula', 'lagi', 'lah', 'kah', 'tuh', 'deh', 'dong', 'sih',
    'toh', 'kok', 'kan', 'nya', 'ku', 'mu', 'kau', 'gua', 'gue', 'elo', 'lu',
    'loe', 'loh', 'lho', 'nih'
}

# Kata filler umum
filler_words = {"eh", "hmm", "gitu", "apa", "ya", "kayak", "jadi", "nah", "anu", "gini"}

def bersihkan_teks(teks):
    teks = re.sub(r'[^a-zA-Z\s]', '', teks).lower()
    kata = teks.split()
    return [k for k in kata if k not in stopwords_id and len(k) > 2]

def hitung_filler(teks):
    teks = teks.lower()
    return {fw: teks.split().count(fw) for fw in filler_words if fw in teks}

def dummy_sentimen(teks):
    """ Fungsi dummy sederhana, bisa diganti dengan model nyata """
    if "senang" in teks or "bagus" in teks:
        return "positif"
    elif "buruk" in teks or "jelek" in teks:
        return "negatif"
    else:
        return "netral"

def scrap_dan_simpan(video_id, judul):
    if col.find_one({"video_id": video_id}):
        print("Data untuk video ini sudah ada.")
        return

    try:
        transkrip = YouTubeTranscriptApi.get_transcript(video_id, languages=['id'])
        for seg in transkrip:
            teks = seg["text"]
            kata_bersih = bersihkan_teks(teks)
            filler = hitung_filler(teks)
            sentimen = dummy_sentimen(teks)

            doc = {
                "video_id": video_id,
                "judul": judul,
                "start": seg["start"],
                "duration": seg["duration"],
                "teks": teks,
                "kata_bersih": kata_bersih,
                "filler_words": filler,
                "sentimen": sentimen
            }
            col.insert_one(doc)

        print("✅ Scraping dan penyimpanan selesai.")
    except Exception as e:
        print(f"Gagal scraping: {e}")