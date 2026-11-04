import re
import string

# Try loading spaCy, otherwise provide clean fallback
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        # Download en_core_web_sm model on first run if needed
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except Exception:
    HAS_SPACY = False

# Common English stop words list as fallback
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 'cannot',
    'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll',
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while',
    'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll',
    'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

def preprocess_text(text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
    """
    Clean and preprocess raw text from resume or job descriptions.
    
    Steps:
    1. Lowercase conversion
    2. Remove URLs, emails, phone numbers, special bullet symbols
    3. Retain technical symbols (+, #, -, ., /) where relevant for skills like C++, C#, CI/CD, .NET
    4. Tokenize & remove stopwords
    5. Perform spaCy lemmatization if available
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text_clean = text.lower()

    # Remove URLs
    text_clean = re.sub(r'https?://\S+|www\.\S+', ' ', text_clean)

    # Remove emails
    text_clean = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text_clean)

    # Remove phone numbers
    text_clean = re.sub(r'[\+\(]?[0-9][0-9\-\(\)\.]{8,}[0-9]', ' ', text_clean)

    # Remove bullet points and special unicode symbols
    text_clean = re.sub(r'[•\t\r\n\f\v▪▫–—◦›»]', ' ', text_clean)

    # Sanitize punctuation while keeping C++, C#, .NET, CI/CD, Node.js intact
    # Replace general punctuation not in tech characters with space
    text_clean = re.sub(r'[^\w\s\+\#\./\-]', ' ', text_clean)

    # Multi-space normalization
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()

    if HAS_SPACY and lemmatize:
        try:
            doc = nlp(text_clean[:100000]) # Limit length for performance
            tokens = []
            for token in doc:
                word = token.lemma_.strip()
                if remove_stopwords and (token.is_stop or word in STOP_WORDS or len(word) < 2):
                    continue
                if token.is_punct or token.is_space:
                    continue
                tokens.append(word)
            return " ".join(tokens)
        except Exception:
            pass

    # Fallback tokenization & cleaning
    words = text_clean.split()
    filtered = []
    for w in words:
        w_clean = w.strip(string.punctuation.replace('+', '').replace('#', ''))
        if remove_stopwords and w_clean in STOP_WORDS:
            continue
        if len(w_clean) > 1:
            filtered.append(w_clean)
            
    return " ".join(filtered)

if __name__ == "__main__":
    sample = "Candidate holds B.Tech in CS. Experience with Python, C++, Docker, PyTorch & AWS! Email: test@example.com"
    print("Cleaned:", preprocess_text(sample))
