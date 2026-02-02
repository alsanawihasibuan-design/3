import sys

def hitung_lot():
    print("=== XAUUSD RISK CALCULATOR ===")
    
    # Input data
    try:
        modal = float(input("Modal (USD): "))
        risiko_persen = float(input("Resiko per trade (%): "))
        jarak_sl = float(input("Jarak Stop Loss (Pips): "))
    except ValueError:
        print("Error: Masukkan angka saja!")
        return

    # Logika Matematika Utilitarian
    # Rumus: (Modal * %Resiko) / (Jarak SL * Contract Size)
    # Contract size Gold standar biasanya 100, tapi di mini account beda.
    # Kita anggap standar 1 pip = $1 per 0.1 lot (approx).
    
    uang_resiko = modal * (risiko_persen / 100)
    # Estimasi kasar: 1 Lot XAU bergerak 1 pip = $1
    # Rumus disederhanakan untuk latihan logika
    lot_size = uang_resiko / jarak_sl 

    print("\n--- HASIL ANALISIS ---")
    print(f"Uang yang siap hilang: ${uang_resiko:.2f}")
    print(f"Maksimal Lot Size: {lot_size:.2f} Lot")
    
    if lot_size < 0.01:
        print("Saran: JANGAN TRADE! Modal/SL tidak masuk akal.")
    else:
        print("Saran: Gas, tapi disiplin SL.")

# Menjalankan fungsi
if __name__ == "__main__":
    hitung_lot()
