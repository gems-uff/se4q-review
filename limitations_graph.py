import os
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

def main():
    # 1. Locate the CSV file in resources directory
    resources_dir = "resources"
    csv_files = glob.glob(os.path.join(resources_dir, "*.csv"))
    
    if not csv_files:
        print("Erro: Nenhum arquivo .csv encontrado na pasta 'resources'.")
        return
    
    csv_files.sort()
    csv_path = csv_files[-1]
    print(f"Lendo arquivo: {csv_path}")

    # These are the limitations categories provided by the user based on letter codes
    # Translated to English as requested
    limitation_mapping = [
        ("Hardware/Noise", ["H"]),
        ("Scalability/Simulation", ["E"]),
        ("Oracle/Unobservability", ["O"]),
        ("Data/Volatility", ["D"]),
        ("Abstraction/Interoperability", ["B"]),
        ("Lifecycle/Effort", ["L"])
    ]

    # 3. Read data from CSV
    # Coluna Q = índice 16 (Limitações)
    col_limitations = 16
    
    counts = Counter()
    records_processed = 0

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None) # Skip header
        
        for row in reader:
            if len(row) <= col_limitations:
                continue
                
            limitations_text = row[col_limitations].strip()
            
            if not limitations_text:
                continue
                
            records_processed += 1

            # Identify matched limitations
            # The limitations are stored as comma-separated letters, e.g., 'H,E,O'
            codes = [code.strip() for code in limitations_text.split(',')]
            
            matched_limitation_indices = []
            
            for code in codes:
                if not code:
                    continue
                for li, (display_name, keywords) in enumerate(limitation_mapping):
                    if code in keywords:
                        matched_limitation_indices.append(display_name)
                        break
                        
            # Use a set to avoid double-counting if a limitation is matched twice for some reason
            for display_name in set(matched_limitation_indices):
                counts[display_name] += 1

    print(f"Total de registros processados com dados na coluna Q: {records_processed}")
    
    # Sort categories by descending quantity to present a clean visual order
    sorted_limitations = sorted(limitation_mapping, key=lambda x: counts[x[0]], reverse=True)
    limitation_names = [item[0] for item in sorted_limitations]
    quantities = [counts[name] for name in limitation_names]

    print("Limitations Counts:")
    for name, qty in zip(limitation_names, quantities):
        print(f"  {name}: {qty}")

    # 3. Compact chart configuration
    bar_color = "#2c3e50"  # Academic dark blue

    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    plt.rcParams['text.color'] = '#111111'
    plt.rcParams['axes.labelcolor'] = '#111111'
    plt.rcParams['xtick.color'] = '#333333'
    plt.rcParams['ytick.color'] = '#333333'

    fig, ax = plt.subplots(figsize=(7.0, 3.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 4. Horizontal bars
    bars = ax.barh(
        limitation_names,
        quantities,
        color=bar_color,
        height=0.55,
        edgecolor='#1a252f',
        linewidth=0.6,
        zorder=3
    )

    # 5. Subtle vertical gridlines
    ax.grid(axis='x', linestyle=':', alpha=0.5, color='#b0b0b0', zorder=0)

    # Clean spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#777777')
    ax.spines['bottom'].set_color('#777777')
    ax.spines['left'].set_linewidth(0.6)
    ax.spines['bottom'].set_linewidth(0.6)

    # 6. Axis styling
    ax.set_xlabel("Number of Papers", fontsize=13, fontweight='bold', labelpad=5)
    ax.tick_params(labelsize=11, width=0.6, length=3)
    ax.invert_yaxis()

    # 7. Value labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 1.0,  # Slightly offset from the bar
            bar.get_y() + bar.get_height() / 2,
            f'{int(width)}',
            va='center',
            ha='left',
            fontsize=11,
            fontweight='semibold',
            color='#111111'
        )

    # X-axis limit for spacing
    ax.set_xlim(0, max(quantities) + 6)

    plt.tight_layout()

    # 8. Save outputs
    os.makedirs('images', exist_ok=True)
    plt.savefig(os.path.join('images', 'limitations_graph.pdf'), bbox_inches='tight')
    plt.savefig(os.path.join('images', 'limitations_graph.png'), dpi=300, bbox_inches='tight')
    print("Successfully generated images/limitations_graph.pdf and images/limitations_graph.png.")

if __name__ == "__main__":
    main()
