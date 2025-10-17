"""
Runs on my Office Desktop within WTS conda env PDF_101
python3 ocr_101.py
"""

import subprocess, os, multiprocessing as mp
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'


input_pdf = r"THESIS.pdf"
output_pdf = r"THESIS_OCR.pdf"

cmd = [
    "ocrmypdf",
    "-l", "eng",
    "--rotate-pages",
    "--deskew",
    "--force-ocr",
    "--optimize", "3",  # Add this - maximum compression
    "--jpeg-quality", "75",  # Add this - lower JPEG quality for images
    "--jobs", str(mp.cpu_count()),#str(mp.cpu_count() // 2 or 1),
    "--output-type", "pdf",
    input_pdf,
    output_pdf,
]

print("Running:", " ".join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr)
if proc.returncode != 0:
    raise SystemExit(f"OCR failed with code {proc.returncode}")
