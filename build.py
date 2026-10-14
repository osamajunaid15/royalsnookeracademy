#!/usr/bin/env python3
"""Extract JS from HTML, obfuscate, reassemble."""
import subprocess, sys, os

def process(src, out, raw_js, obf_js):
    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find the LAST <script> ... </script> (inline script, not CDN tags)
    s_start = html.rindex('<script>') + len('<script>')
    s_end = html.rindex('</script>')
    js = html[s_start:s_end].strip()

    with open(raw_js, 'w', encoding='utf-8') as f:
        f.write(js)

    # Obfuscate
    result = subprocess.run([
        'npx', 'javascript-obfuscator', raw_js,
        '--output', obf_js,
        '--compact', 'true',
        '--control-flow-flattening', 'false',
        '--dead-code-injection', 'false',
        '--string-array', 'true',
        '--string-array-encoding', 'base64',
        '--string-array-threshold', '0.75',
        '--identifier-names-generator', 'hexadecimal',
        '--self-defending', 'false'
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Obfuscation failed for {src}:")
        print(result.stderr)
        sys.exit(1)

    with open(obf_js, 'r', encoding='utf-8') as f:
        obf = f.read()

    # Reassemble: replace inline script content with obfuscated version
    final = html[:s_start] + '\n' + obf + '\n' + html[s_end:]

    with open(out, 'w', encoding='utf-8') as f:
        f.write(final)

    print(f"Built {out} ({len(final)} bytes)")

process('source-pos.html', 'index.html', 'pos-raw.js', 'pos-obf.js')
process('source-booking.html', 'booking.html', 'booking-raw.js', 'booking-obf.js')
