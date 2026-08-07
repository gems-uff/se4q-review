import os
import re
import glob
from collections import Counter
import pypdf
import matplotlib.pyplot as plt

# 1. Dynamically locate the survey PDF in resources directory
resources_dir = "resources"
pdf_pattern = os.path.join(resources_dir, "Artigos aceitos (respostas) - Respostas ao formulário.pdf")
pdf_files = glob.glob(pdf_pattern)

if not pdf_files:
    raise FileNotFoundError("Could not find any matching survey PDF file in resources directory.")

# Sort to get the latest (e.g. (5) instead of (3))
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

# 2. Count empirical evidence categories
counts = Counter()

# Define the categories to search for and their display names (in English)
evidence_mapping = [
    ("Controlled Experiment", ["Experimento", "Controlado"]),
    ("Example Application", ["Aplica", "Exemplo"]),
    ("Performance Evaluation", ["Avalia", "Experimental"]),
    ("Case Study", ["Estudo de Caso", "Caso"]),
    ("Proof of Concept", ["Prova de Conceito", "Conceito"]),
    ("Discussion", ["Discuss"]),
    ("Survey", ["Survey"])
]

# We will search in the search area after the last phase label or fall back to the last 400 characters
phases = [
    "Análise de requisitos (QSRA)",
    "Design de software quântico",
    "Implementação de software quântico",
    "Teste de software quântico",
    "Manutenção de software quântico",
    "Reutilização de software quântico",
    "Análise de requisitos",
    "Design de software",
    "Implementação de software",
    "Teste de software",
    "Manutenção de software",
    "Reutilização de software"
]

for idx, r in enumerate(records):
    # Normalize whitespace to make matching easier
    r_clean = re.sub(r'\s+', ' ', r)
    
    # Find the end of the phase labels
    last_phase_pos = -1
    for phase in phases:
        pos = r_clean.rfind(phase)
        if pos > last_phase_pos:
            last_phase_pos = pos + len(phase)
            
    if last_phase_pos == -1:
        # Fallback to the last 400 characters
        search_area = r_clean[-400:]
    else:
        search_area = r_clean[last_phase_pos:]
        
    # Match empirical evidence options
    matched_any = False
    for display_name, keywords in evidence_mapping:
        if any(kw in search_area for kw in keywords):
            counts[display_name] += 1
            matched_any = True
            
    if not matched_any:
        print(f"Warning: Record {idx+1} did not match any empirical evidence categories. Search area: {repr(search_area)}")

# Sort categories by descending quantity to present a clean visual order
sorted_evidence = sorted(evidence_mapping, key=lambda x: counts[x[0]], reverse=True)
evidence_names = [item[0] for item in sorted_evidence]
quantities = [counts[name] for name in evidence_names]

print("Empirical Evidence Counts:")
for name, qty in zip(evidence_names, quantities):
    print(f"  {name}: {qty}")

# 3. Compact chart configuration
bar_color = "#2c3e50"  # Academic dark blue

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#111111'
plt.rcParams['axes.labelcolor'] = '#111111'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'

# 7 categories look best on slightly taller canvas to preserve vertical spacing
fig, ax = plt.subplots(figsize=(7.0, 3.5), dpi=300)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# 4. Horizontal bars
bars = ax.barh(
    evidence_names,
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
plt.savefig(os.path.join('images', 'compact_evidence_graph.pdf'), bbox_inches='tight')
plt.savefig(os.path.join('images', 'compact_evidence_graph.png'), dpi=300, bbox_inches='tight')
print("Successfully generated images/compact_evidence_graph.pdf and images/compact_evidence_graph.png.")

plt.show()
