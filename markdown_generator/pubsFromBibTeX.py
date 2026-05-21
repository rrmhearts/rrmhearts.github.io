#!/usr/bin/env python
# coding: utf-8

import os
import re
import html
from pybtex.database.input import bibtex

# Your BibTeX data file
bib_file = "pubs.bib"

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)

# Ensure output directory exists
os.makedirs("../_publications", exist_ok=True)

parser = bibtex.Parser()
bibdata = parser.parse_file(bib_file)

for bib_id in bibdata.entries:
    b = bibdata.entries[bib_id].fields
    
    # 1. Date Processing (Fallback to Jan 1st if missing)
    pub_year = b.get("year", "1900")
    pub_month = "01"
    pub_day = "01"
    
    if "month" in b:
        month_str = b["month"].lower()
        month_map = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
                     "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
        for m_key, m_val in month_map.items():
            if m_key in month_str:
                pub_month = m_val
                break

    pub_date = f"{pub_year}-{pub_month}-{pub_day}"
    
    # 2. Title & Slug Processing
    title = b.get("title", "Untitled").replace("{", "").replace("}", "").replace("\\", "")
    clean_title = title.replace(" ", "-")
    url_slug = re.sub(r"\[.*\]|[^a-zA-Z0-9_-]", "", clean_title)
    url_slug = re.sub(r"-+", "-", url_slug).lower()
    
    md_filename = f"{pub_date}-{url_slug}.md"
    
    # 3. Venue Extraction (Handles Journals, Books, Conferences, Miscs)
    venue = "Unknown Venue"
    if "journal" in b:
        venue = b["journal"]
    elif "booktitle" in b:
        venue = b["booktitle"]
    elif "organization" in b:
        venue = b["organization"]
        
    venue = venue.replace("{", "").replace("}", "").replace("\\", "")
    
    # 4. Author Processing
    authors = []
    for author in bibdata.entries[bib_id].persons.get("author", []):
        first = " ".join(author.first_names)
        last = " ".join(author.last_names)
        authors.append(f"{first} {last}".strip())
    author_str = ", ".join(authors) if authors else "Unknown Author"
    
    # 5. Citation Formatting
    citation = f"{author_str}. ({pub_year}). &quot;{html_escape(title)}.&quot; <i>{html_escape(venue)}</i>."
    
    # 6. Optional Notes/Excerpts
    excerpt = b.get("note", "")
    
    # 7. YAML Frontmatter Construction
    md = "---\n"
    md += f"title: \"{html_escape(title)}\"\n"
    md += "collection: publications\n"
    md += "category: manuscripts\n"
    md += f"permalink: /publication/{pub_date}-{url_slug}\n"
    
    if excerpt:
        md += f"excerpt: '{html_escape(excerpt)}'\n"
        
    md += f"date: {pub_date}\n"
    md += f"venue: '{html_escape(venue)}'\n"
    
    # Standardizing placeholders for URLs based on your template
    md += f"slidesurl: 'http://academicpages.github.io/files/slides_{bib_id}.pdf'\n"
    md += f"paperurl: 'http://academicpages.github.io/files/paper_{bib_id}.pdf'\n"
    md += f"bibtexurl: 'http://academicpages.github.io/files/bibtex_{bib_id}.bib'\n"
    
    md += f"citation: '{citation}'\n"
    md += "---\n\n"
    
    # 8. Markdown Content
    if excerpt:
        md += f"{html_escape(excerpt)}\n\n"
        
    md += f"Use [Google Scholar](https://scholar.google.com/scholar?q={html.escape(url_slug.replace('-', '+'))}){{:target=\"_blank\"}} for full citation\n"
    
    # 9. Write Output
    with open(f"../_publications/{md_filename}", 'w', encoding="utf-8") as f:
        f.write(md)
        
    print(f"SUCCESS: Generated {md_filename}")