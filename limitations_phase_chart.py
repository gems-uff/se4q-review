import os
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import Counter
import re

def main():
    # 1. Locate the CSV file in resources directory
    resources_dir = "resources"
    csv_files = glob.glob(os.path.join(resources_dir, "*.csv"))
    
    if not csv_files:
        print("Erro: Nenhum arquivo .csv encontrado na pasta 'resources'.")
        print("Por favor, exporte a 'tabela de artigos aceitos' do Google Forms/Sheets como CSV e coloque na pasta 'resources'.")
        print("O script usará a Coluna O (índice 14) e Coluna Q (índice 16) deste arquivo.")
        return
    
    csv_files.sort()
    csv_path = csv_files[-1]
    print(f"Lendo arquivo: {csv_path}")

    # 2. Define categories for phases and limitations
    phase_mapping = [
        ("Requirements\n(QSRA)", ["Análise de requisitos", "QSRA"]),
        ("Software\nDesign", ["Design de software quântico", "Design"]),
        ("Implementation", ["Implementação de software quântico", "Implementação"]),
        ("Testing\n& QA", ["Teste de software quântico", "Teste"]),
        ("Maintenance", ["Manutenção de software quântico", "Manutenção"]),
        ("Reuse\nAnalysis", ["Reutilização de software quântico", "Reutilização"])
    ]

    # These are the limitations categories provided by the user based on letter codes
    # Translated to English and broken into multiple lines to avoid overlapping
    limitation_mapping = [
        ("Hardware/\nNoise", ["H"]),
        ("Scalability/\nSimulation", ["E"]),
        ("Oracle/\nUnobservability", ["O"]),
        ("Data/\nVolatility", ["D"]),
        ("Abstraction/\nInteroperability", ["B"]),
        ("Lifecycle/\nEffort", ["L"])
    ]

    # 3. Read data from CSV
    # Coluna O = índice 14 (Fase do Ciclo de Vida)
    # Coluna Q = índice 16 (Limitações)
    col_phase = 14
    col_limitations = 16
    
    matrix = [[0] * len(phase_mapping) for _ in range(len(limitation_mapping))]
    other_limitations_counts = Counter()

    records_processed = 0

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None) # Skip header
        
        for row in reader:
            if len(row) <= max(col_phase, col_limitations):
                continue
                
            phase_text = row[col_phase].strip()
            limitations_text = row[col_limitations].strip()
            
            if not phase_text or not limitations_text:
                continue
                
            records_processed += 1

            # Identify matched phases
            matched_phase_indices = []
            for pi, (_, keywords) in enumerate(phase_mapping):
                if any(kw.lower() in phase_text.lower() for kw in keywords):
                    matched_phase_indices.append(pi)
            
            # Identify matched limitations
            # The limitations are stored as comma-separated letters, e.g., 'H,E,O'
            codes = [code.strip() for code in limitations_text.split(',')]
            matched_limitation_indices = []
            matched_any_limitation = False
            
            for code in codes:
                if not code:
                    continue
                found_match = False
                for li, (_, keywords) in enumerate(limitation_mapping):
                    if code in keywords:
                        matched_limitation_indices.append(li)
                        matched_any_limitation = True
                        found_match = True
                        break
                
                if not found_match:
                    other_limitations_counts[code] += 1
                        
            # Increment cross-tabulation matrix
            # Use a set to avoid double-counting if somehow a phase/limitation is matched twice
            for pi in set(matched_phase_indices):
                for li in set(matched_limitation_indices):
                    matrix[li][pi] += 1

    print(f"Total de registros processados com dados nas colunas O e Q: {records_processed}")
    
    if other_limitations_counts:
        print("\nCódigos não mapeados encontrados:", other_limitations_counts)
    
    data = np.array(matrix)
    
    # Filter out empty rows (limitations with 0 matches across all phases) to keep chart clean
    active_rows = [i for i in range(len(limitation_mapping)) if sum(matrix[i]) > 0]
    
    if not active_rows:
        print("Nenhuma correspondência encontrada. Verifique se as colunas O e Q contêm os dados esperados ou modifique as palavras-chave no script.")
        return
        
    filtered_data = data[active_rows, :]
    phase_names = [p[0] for p in phase_mapping]
    limitation_names = [limitation_mapping[i][0] for i in active_rows]

    # 4. Generate Heatmap
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    plt.rcParams['text.color'] = '#111111'
    plt.rcParams['axes.labelcolor'] = '#111111'
    plt.rcParams['xtick.color'] = '#333333'
    plt.rcParams['ytick.color'] = '#333333'

    fig, ax = plt.subplots(figsize=(9.0, 5.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Custom colormap: white -> light blue -> dark academic blue
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "academic_blue",
        ["#ffffff", "#d4e6f1", "#5b9bd5", "#2c3e50"],
        N=256
    )

    im = ax.imshow(filtered_data, cmap=cmap, aspect='auto', vmin=0)

    # Ticks
    ax.set_xticks(np.arange(len(phase_names)))
    ax.set_yticks(np.arange(len(limitation_names)))
    ax.set_xticklabels(phase_names, fontsize=11, ha='center')
    ax.set_yticklabels(limitation_names, fontsize=11)

    # Annotate cells with values
    max_val = filtered_data.max() if filtered_data.size > 0 else 1
    for i in range(len(limitation_names)):
        for j in range(len(phase_names)):
            val = filtered_data[i, j]
            # Use white text on dark cells, dark text on light cells
            text_color = 'white' if val > max_val * 0.55 else '#111111'
            ax.text(j, i, str(val), ha='center', va='center',
                    fontsize=12, fontweight='semibold', color=text_color)

    # Gridlines for separation
    ax.set_xticks(np.arange(len(phase_names) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(limitation_names) + 1) - 0.5, minor=True)
    ax.grid(which='minor', color='#cccccc', linewidth=0.5)
    ax.tick_params(which='minor', size=0)

    # Spines
    for spine in ax.spines.values():
        spine.set_color('#999999')
        spine.set_linewidth(0.5)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.03)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Number of Papers', fontsize=12, fontweight='bold')

    plt.tight_layout()

    # 5. Save outputs
    os.makedirs('images', exist_ok=True)
    plt.savefig(os.path.join('images', 'limitations_vs_phase_heatmap.pdf'), bbox_inches='tight')
    plt.savefig(os.path.join('images', 'limitations_vs_phase_heatmap.png'), dpi=300, bbox_inches='tight')
    print("Sucesso! Imagens geradas: images/limitations_vs_phase_heatmap.pdf e .png")

    # Only show if not running in headless mode, but we can just leave it as standard
    # plt.show()

if __name__ == "__main__":
    main()
