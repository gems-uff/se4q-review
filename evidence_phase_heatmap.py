import os
import re
import glob
from collections import Counter
import pypdf
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# 1. Dynamically locate the survey PDF in resources directory
resources_dir = "resources"
pdf_pattern = os.path.join(resources_dir, "Artigos aceitos (respostas) - Respostas ao formulário.pdf")
pdf_files = glob.glob(pdf_pattern)

if not pdf_files:
    raise FileNotFoundError("Could not find any matching survey PDF file in resources directory.")

pdf_files.sort()
pdf_path = pdf_files[-1]
print(f"Reading PDF: {pdf_path}")

reader = pypdf.PdfReader(pdf_path)

# Extract all text from all pages
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Remove the header block on each page
header_pat = r"Carimbo de data/hora.*Observações"
clean_text = re.sub(header_pat, "", full_text)

# Find timestamps to split records
record_starts = [m.start() for m in re.finditer(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', clean_text)]

records = []
for idx, start_pos in enumerate(record_starts):
    end_pos = record_starts[idx+1] if idx + 1 < len(record_starts) else len(clean_text)
    records.append(clean_text[start_pos:end_pos].strip())

print(f"Total records found: {len(records)}")

# 2. Define categories
phase_mapping = [
    ("Requirements\n(QSRA)", ["Análise de requisitos", "QSRA"]),
    ("Software\nDesign", ["Design de software quântico", "Design"]),
    ("Implementation", ["Implementação de software quântico", "Implementação"]),
    ("Testing\n& QA", ["Teste de software quântico", "Teste"]),
    ("Maintenance", ["Manutenção de software quântico", "Manutenção"]),
    ("Reuse\nAnalysis", ["Reutilização de software quântico", "Reutilização"])
]

evidence_mapping = [
    ("Controlled Experiment", ["Experimento", "Controlado"]),
    ("Example Application", ["Aplica", "Exemplo"]),
    ("Experimental Evaluation", ["Avalia", "Experimental"]),
    ("Case Study", ["Estudo de Caso", "Caso"]),
    ("Proof of Concept", ["Prova de Conceito", "Conceito"]),
    ("Empirical Study", ["Estudo Emp", "Emp rico", "Emprico"]),
    ("Discussion", ["Discuss"])
]

# 3. Build the cross-tabulation matrix
matrix = [[0] * len(phase_mapping) for _ in range(len(evidence_mapping))]

for r in records:
    r_clean = re.sub(r'\s+', ' ', r)

    # Identify matched phases (last 400 chars where checkbox answers sit)
    last_part = r_clean[-400:]
    matched_phase_indices = []
    for pi, (_, keywords) in enumerate(phase_mapping):
        if any(kw in last_part for kw in keywords):
            matched_phase_indices.append(pi)

    # Find the last phase position; evidence checkbox is after the phase labels
    phases_flat = [kw for _, kws in phase_mapping for kw in kws]
    last_phase_pos = -1
    for kw in phases_flat:
        pos = r_clean.rfind(kw)
        if pos > last_phase_pos:
            last_phase_pos = pos + len(kw)

    search_area = r_clean[last_phase_pos:] if last_phase_pos != -1 else r_clean[-400:]

    # Identify matched evidences
    matched_evidence_indices = []
    for ei, (_, keywords) in enumerate(evidence_mapping):
        if any(kw in search_area for kw in keywords):
            matched_evidence_indices.append(ei)

    # Increment cross-tabulation
    for pi in matched_phase_indices:
        for ei in matched_evidence_indices:
            matrix[ei][pi] += 1

data = np.array(matrix)

phase_names = [p[0] for p in phase_mapping]
evidence_names = [e[0] for e in evidence_mapping]

# 4. Heatmap chart
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#111111'
plt.rcParams['axes.labelcolor'] = '#111111'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'

fig, ax = plt.subplots(figsize=(9.0, 5.5), dpi=300)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Custom colormap: white → light blue → dark academic blue
cmap = mcolors.LinearSegmentedColormap.from_list(
    "academic_blue",
    ["#ffffff", "#d4e6f1", "#5b9bd5", "#2c3e50"],
    N=256
)

im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=0)

# Ticks
ax.set_xticks(np.arange(len(phase_names)))
ax.set_yticks(np.arange(len(evidence_names)))
ax.set_xticklabels(phase_names, fontsize=11, ha='center')
ax.set_yticklabels(evidence_names, fontsize=11)

# Annotate cells with values
for i in range(len(evidence_names)):
    for j in range(len(phase_names)):
        val = data[i, j]
        # Use white text on dark cells, dark text on light cells
        text_color = 'white' if val > data.max() * 0.55 else '#111111'
        ax.text(j, i, str(val), ha='center', va='center',
                fontsize=12, fontweight='semibold', color=text_color)

# Gridlines for separation
ax.set_xticks(np.arange(len(phase_names) + 1) - 0.5, minor=True)
ax.set_yticks(np.arange(len(evidence_names) + 1) - 0.5, minor=True)
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
plt.savefig(os.path.join('images', 'evidence_vs_phase_heatmap.pdf'), bbox_inches='tight')
plt.savefig(os.path.join('images', 'evidence_vs_phase_heatmap.png'), dpi=300, bbox_inches='tight')
print("Successfully generated images/evidence_vs_phase_heatmap.pdf and images/evidence_vs_phase_heatmap.png.")

plt.show()
