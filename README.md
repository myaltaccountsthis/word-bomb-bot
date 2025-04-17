# 🧠💥 Word Bomb AI Bot

A Python bot that plays **Word Bomb** (on Roblox) entirely on its own:

* 📸 Captures the screen in real‑time  
* 🔍 Uses OpenCV + Tesseract OCR to read each bomb prompt (97% accuracy)  
* 🧮 Generates a valid English word that contains the given letter pair, choosing based on length or random
* ⚡ Types the answer in <2 s—fast enough to beat most humans

---

## Prerequisites
| Tool | Version tested | Notes |
|------|----------------|-------|
| Python | 3.9 – 3.12 | Any CPython build |
| Tesseract OCR | ≥ 5.0 | Install language data for `eng` |
| Windows | 10/11 | Uses `pywin32` for native keyboard input<sup>†</sup> |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/yourname/wordbomb-bot.git
cd wordbomb-bot

# 2. Create & activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/Scripts/activate        # Windows
# source .venv/bin/activate          # macOS / Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Tesseract
# Windows (choco)  : choco install tesseract
# macOS   (brew)   : brew install tesseract
# Linux   (apt)    : sudo apt-get install tesseract-ocr
