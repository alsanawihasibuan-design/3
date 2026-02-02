import sys

def hitung_resiko():
    print("--- RECOVERY MODE: XAUUSD CALC ---")
    try:
        modal = float(input("Modal (USD): "))
        risiko_persen = float(input("Risiko (%): "))
        sl_pips = float(input("Jarak SL (Pips): "))
    except ValueError:
        print("Input angka saja.")
        return

    uang_resiko = modal * (risiko_persen / 100)
    lot_size = uang_resiko / sl_pips

    print(f"\nRisiko: ${uang_resiko:.2f}")
    print(f"Max Lot: {lot_size:.2f} Lot")

if __name__ == "__main__":
    hitung_resiko()
