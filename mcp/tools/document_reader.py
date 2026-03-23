import requests
from bs4 import BeautifulSoup
import PyPDF2

def read_document(source: str):
    """Reads content from a URL or a local PDF file path with custom User-Agent."""
    # Wikipedia and others require a descriptive User-Agent
    headers = {
        'User-Agent': 'DeepResearchAgent/1.0 (contact: your-email@example.com) ResearchBot'
    }

    if source.startswith("http"):
        try:
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status() # Check for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=' ')
            return " ".join(text.split())[:5000]
        except Exception as e:
            return f"Error reading URL: {str(e)}"
    
    else:
        # Local PDF logic remains the same
        try:
            with open(source, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "".join([page.extract_text() for page in reader.pages])
                return text[:5000]
        except Exception as e:
            return f"Error reading file: {str(e)}"