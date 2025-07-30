import re

def clean_markdown_response(text: str) -> str:
    """Clean AI response to ensure proper markdown formatting without HTML artifacts"""
    
    # Remove any HTML attributes that might have leaked through
    # Remove target="_blank", rel="noopener", class="..." etc
    text = re.sub(r'\s+target="_blank"', '', text)
    text = re.sub(r'\s+rel="[^"]*"', '', text)
    text = re.sub(r'\s+class="[^"]*"', '', text)
    text = re.sub(r'\s+style="[^"]*"', '', text)
    text = re.sub(r'\s+id="[^"]*"', '', text)
    
    # Clean up any broken HTML tags
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    
    # Fix broken markdown links that might have HTML mixed in
    # Convert [text](url extra_attrs) to just [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)[^)]*\)', r'[\1](\2)', text)
    
    # Ensure proper spacing around links
    text = re.sub(r'([.!?])\[', r'\1 [', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove trailing spaces at end of lines
    text = re.sub(r' +$', '', text, flags=re.MULTILINE)
    
    # Ensure bullet points are properly formatted
    text = re.sub(r'^[-*]\s*', '- ', text, flags=re.MULTILINE)
    
    # Ensure numbered lists are properly formatted
    text = re.sub(r'^(\d+)\.\s*', r'\1. ', text, flags=re.MULTILINE)
    
    return text.strip()

def extract_clean_links(text: str) -> list:
    """Extract clean links from text, removing any HTML attributes"""
    links = []
    
    # Find markdown links
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
    for link_text, url in markdown_links:
        # Clean the URL of any attributes
        clean_url = url.split()[0] if ' ' in url else url
        links.append({'text': link_text, 'url': clean_url})
    
    # Find plain URLs
    plain_urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    for url in plain_urls:
        # Make sure it's not already part of a markdown link
        if not any(url in link['url'] for link in links):
            links.append({'text': url, 'url': url})
    
    return links