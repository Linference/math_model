import re

with open('HiMCM_A_final.tex', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

in_tab = False
ncols = 0
tab_start = 0
for i, line in enumerate(lines, 1):
    m = re.search(r'begin\{tabular\}\{([^}]*)\}', line)
    if m:
        spec = m.group(1)
        ncols = len(spec.replace('|', '').replace('@{}', '').replace('@{\hspace{1em}}', ''))
        in_tab = True
        tab_start = i
        continue
    if in_tab and 'end{tabular}' in line:
        in_tab = False
        continue
    if in_tab:
        stripped = line.strip()
        # skip pure structure lines
        if any(stripped.startswith(x) for x in ['\\toprule', '\\midrule', '\\bottomrule', '\\cmidrule', '%', '\\hline']):
            continue
        if not ('\\\\' in line or '&' in line):
            continue
        # count ampersands
        namp = line.count('&')
        # subtract multicolumn adjustments (multicolumn{n} uses n cells but only writes n-1 separators counted differently)
        mc_specs = re.findall(r'\\multicolumn\{(\d+)\}', line)
        # A multicolumn{n} spans n columns; the '&' inside is still a separator.
        # The separators actually present:
        #   For a row with colspec CCC... (ncols cols), the separators are the '&' chars.
        #   multicolumn{n}{...}{...} occupies n columns worth but written as one cell.
        # So effective separator count = namp.
        # A valid data row for ncols columns must have exactly ncols-1 separators.
        if namp == ncols - 1:
            continue
        # Allow multicolumn spanning full width (e.g. \multicolumn{6}{l}{...}) - that row has 0 '&'
        if namp == 0 and mc_specs and sum(int(x) for x in mc_specs) == ncols:
            continue
        print(f'TABLE {tab_start} | LINE {i}: ncols={ncols}, separators={namp} :: {stripped[:80]}')
