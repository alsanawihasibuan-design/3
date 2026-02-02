import os
import time
import argparse
import sys
import requests
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- KONFIGURASI KONSTANTA ---
API_URL_TEMPLATE = "https://www.goldapi.io/api/{symbol}/{currency}"
DEFAULT_SYMBOL = "XAU"
DEFAULT_CURRENCY = "USD"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
PIP_VALUE_XAUUSD = 10.0  # 1 Standard Lot = $10 per pip movement
PIP_PRICE_DISTANCE = 0.1  # 1 pip = $0.10 pergerakan harga di XAUUSD

def get_timestamp() -> str:
    """Mengembalikan timestamp saat ini dengan presisi detik."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def parse_arguments() -> argparse.Namespace:
    """
    Menangani input argumen dari terminal (CLI).
    Memberikan nilai default jika user tidak memasukkan argumen.
    """
    parser = argparse.ArgumentParser(
        description="Gold Trading Assistant - Risk Management & Monitoring Tool"
    )
    parser.add_argument(
        "--balance", 
        type=float, 
        default=10000.0, 
        help="Saldo akun trading dalam USD (Default: 10000)"
    )
    parser.add_argument(
        "--risk", 
        type=float, 
        default=1.0, 
        help="Persentase risiko per trade (Default: 1.0)"
    )
    parser.add_argument(
        "--symbol", 
        type=str, 
        default=DEFAULT_SYMBOL, 
        help="Simbol aset (Default: XAU)"
    )
    return parser.parse_args()

def clear_screen() -> None:
    """Membersihkan layar terminal secara cross-platform."""
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_market_price(api_key: str, symbol: str, currency: str) -> Optional[float]:
    """
    Mengambil data harga pasar dengan mekanisme Retry sederhana.
    
    Args:
        api_key (str): Kunci autentikasi API.
        symbol (str): Simbol aset (cth: XAU).
        currency (str): Mata uang (cth: USD).
        
    Returns:
        Optional[float]: Harga aset jika sukses, None jika gagal setelah retries.
    """
    url = API_URL_TEMPLATE.format(symbol=symbol, currency=currency)
    headers = {"x-access-token": api_key}
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Timeout diperpendek agar fail-fast
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data: Dict[str, Any] = response.json()
                return data.get('price')
            
            # Jika status code 4xx/5xx selain 200
            print(f"[{get_timestamp()}] ⚠️ Gagal (Status: {response.status_code}). Percobaan {attempt}/{MAX_RETRIES}...")
            
        except requests.RequestException as e:
            print(f"[{get_timestamp()}] 🔌 Koneksi Error: {e}. Percobaan {attempt}/{MAX_RETRIES}...")
        
        # Tunggu sebelum mencoba lagi (kecuali ini percobaan terakhir)
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)
            
    return None

def calculate_position_size(balance: float, risk_pct: float, sl_pips: int) -> Tuple[float, float]:
    """
    Menghitung ukuran lot dan nilai risiko dalam USD.
    
    Args:
        balance (float): Saldo akun.
        risk_pct (float): Persentase risiko (0-100).
        sl_pips (int): Jarak Stop Loss dalam pips.
        
    Returns:
        Tuple[float, float]: (Ukuran Lot, Risiko dalam USD)
    """
    risk_usd = balance * (risk_pct / 100)
    
    # Mencegah pembagian dengan nol
    if sl_pips == 0:
        return 0.0, risk_usd
        
    # Rumus: Risk USD / (SL Pips * Nilai per Pip per Lot)
    lot_size = risk_usd / (sl_pips * PIP_VALUE_XAUUSD)
    return lot_size, risk_usd

def render_dashboard(price: float, balance: float, risk_pct: float) -> None:
    """
    Menampilkan antarmuka pengguna (UI) ke terminal.
    """
    clear_screen()
    risk_usd = balance * (risk_pct / 100)
    
    print("=" * 60)
    print(f"{'🤖 ALGORITHMIC TRADING ASSISTANT (PRO)':^60}")
    print("=" * 60)
    print(f" 🔥 XAU/USD LIVE : ${price:,.2f}")
    print(f" 💰 Balance      : ${balance:,.2f}")
    print(f" 🛡️  Risk Profile : {risk_pct}% (${risk_usd:.2f} per trade)")
    print("-" * 60)
    print(f"{'SCENARIO ANALYSIS':^60}")
    print("-" * 60)
    
    # Header Tabel dengan alignment rapi
    print(f"| {'Tipe Trade':<12} | {'SL (Pips)':<10} | {'Max Lot':<10} | {'Jarak ($)':<12} |")
    print("-" * 60)
    
    # Skenario Trading
    scenarios = [
        ("Scalping", 30),
        ("Intraday", 50),
        ("Swing", 100)
    ]
    
    for name, pips in scenarios:
        lot, _ = calculate_position_size(balance, risk_pct, pips)
        price_distance = pips * PIP_PRICE_DISTANCE
        
        # Print baris tabel
        print(f"| {name:<12} | {pips:<10} | {lot:<10.2f} | ${price_distance:<11.2f} |")
        
    print("-" * 60)
    print(f" 🕒 Last Update: {get_timestamp()}")
    print(" 🛑 Tekan CTRL+C untuk keluar.")
    print("=" * 60)

def main() -> None:
    # 1. Validasi Lingkungan
    api_key = os.getenv("GOLD_API_KEY")
    if not api_key:
        print(f"[{get_timestamp()}] ❌ FATAL ERROR: Environment Variable 'GOLD_API_KEY' tidak ditemukan.")
        sys.exit(1)

    # 2. Setup Argument
    args = parse_arguments()
    
    print(f"[{get_timestamp()}] 📡 Memulai sistem pemantauan untuk {args.symbol}...")
    
    # 3. Main Loop
    try:
        while True:
            # Fetch Data
            current_price = fetch_market_price(api_key, args.symbol, DEFAULT_CURRENCY)
            
            if current_price:
                # Render UI jika data berhasil didapat
                render_dashboard(current_price, args.balance, args.risk)
            else:
                # Jika gagal setelah 3x retry, tampilkan pesan tanpa clear screen agar log terbaca
                print(f"[{get_timestamp()}] ❌ Gagal mengambil data pasar. Mencoba lagi nanti...")
            
            # Jeda update (30 detik)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan oleh pengguna. Selamat trading!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
