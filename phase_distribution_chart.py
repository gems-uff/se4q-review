import os
import re
from collections import Counter
# pyrefly: ignore [missing-import]
import pypdf
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt

# 1. Read and parse PDF dynamically to get phase labels
pdf_path = os.path.join("resources", "Artigos aceitos (respostas) - Respostas ao formulário 1 (3).pdf")

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

reader = pypdf.PdfReader(pdf_path)

# Extract all text from all pages
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Remove the header block on each page to avoid matching search strings in the column headers
header_pat = r"Carimbo de data/hora.*Observações"
clean_text = re.sub(header_pat, "", full_text)

# Find timestamps to split records
record_starts = [m.start() for m in re.finditer(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', clean_text)]

records = []
for idx, start_pos in enumerate(record_starts):
    end_pos = record_starts[idx+1] if idx + 1 < len(record_starts) else len(clean_text)
    records.append(clean_text[start_pos:end_pos].strip())

# Count phase labels in each record using the last 400 characters (where checkbox answers are situated)
counts = Counter()
for record in records:
    last_part = record[-400:]
    
    if "Análise de requisitos" in last_part or "QSRA" in last_part:
        counts["Requirements (QSRA)"] += 1
    if "Design de software quântico" in last_part or "Design" in last_part:
        counts["Software Design"] += 1
    if "Implementação de software quântico" in last_part or "Implementação" in last_part:
        counts["Implementation"] += 1
    if "Teste de software quântico" in last_part or "Teste" in last_part:
        counts["Testing & QA"] += 1
    if "Manutenção de software quântico" in last_part or "Manutenção" in last_part:
        counts["Maintenance"] += 1
    if "Reutilização de software quântico" in last_part or "Reutilização" in last_part:
        counts["Reuse Analysis"] += 1

# Define categories in English, in the desired order
phases = [
    "Requirements (QSRA)",
    "Software Design",
    "Implementation",
    "Testing & QA",
    "Maintenance",
    "Reuse Analysis"
]

quantities = [counts[phase] for phase in phases]


bar_color = "#2c3e50"  # Academic dark blue

# 2. Compact chart configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#111111'
plt.rcParams['axes.labelcolor'] = '#111111'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'

fig, ax = plt.subplots(figsize=(7.0, 3.0), dpi=300)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# 3. Horizontal bars
bars = ax.barh(
    phases,
    quantities,
    color=bar_color,
    height=0.55,
    edgecolor='#1a252f',
    linewidth=0.6,
    zorder=3
)

# 4. Subtle vertical gridlines
ax.grid(axis='x', linestyle=':', alpha=0.5, color='#b0b0b0', zorder=0)

# Clean spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#777777')
ax.spines['bottom'].set_color('#777777')
ax.spines['left'].set_linewidth(0.6)
ax.spines['bottom'].set_linewidth(0.6)

# 5. Axis styling
ax.set_xlabel("Number of Papers", fontsize=13, fontweight='bold', labelpad=5)
ax.tick_params(labelsize=11, width=0.6, length=3)
ax.invert_yaxis()

# 6. Value labels on bars
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.6,
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

# 7. Save outputs
os.makedirs('images', exist_ok=True)
plt.savefig(os.path.join('images', 'compact_graph.pdf'), bbox_inches='tight')
plt.savefig(os.path.join('images', 'compact_graph.png'), dpi=300, bbox_inches='tight')

plt.show()