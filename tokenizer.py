import sys


def tokenize(file_path: str) -> list:
    """
    Runtime: O(n) where n is the total characters in the file
    We iteratre through each character once, therefore linearly
    """
    tokens = []
    
    try:
        with open(file_path, 'r', encoding='utf_8', errors='ignore') as file:
            for line in file:
                current_token = []
                for char in line:    
                    if (char >= 'a' and char <= 'z') or \
                       (char >= 'A' and char <= 'Z') or \
                       (char >= '0' and char <= '9'):
                        current_token.append(char.lower())
                    else:
                        if current_token:
                            tokens.append(''.join(current_token))
                            current_token = []
                        
                if current_token:
                    tokens.append(''.join(current_token))
                
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    return tokens


def tokenize_text(text: str) -> list:
    """
    Tokenize text content directly (for web crawler).
    Runtime: O(n) where n is the total characters in the text
    """
    tokens = []
    current_token = []
    
    for char in text:
        if (char >= 'a' and char <= 'z') or \
           (char >= 'A' and char <= 'Z') or \
           (char >= '0' and char <= '9'):
            current_token.append(char.lower())
        else:
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
    
    if current_token:
        tokens.append(''.join(current_token))
    
    return tokens


def computeWordFrequencies(tokens_list: list) -> dict:
    """
    Runtime: O(n) where n is the number of tokens
    We do a single pass through the tokens, scaling linearly as n gets bigger
    """
    freq_dict = {}
    
    for tokens in tokens_list:
        freq_dict[tokens] = freq_dict.get(tokens, 0) + 1
        
    return freq_dict
            

def printFrequencies(freq_dict: dict) -> None:
    """
    Runtime: O(n log n) where n is unique tokens
    Printing itself is O(n) but O(n log n) dominates/grows faster
    """
    sorted_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    for token, freq in sorted_dict:
        print(f"{token}\t{freq}")


def main():
    """
    Runtime: O(m + n long n) where m is the total characters
    and n is the unique tokens
    Linear in the file size, and log-linear in the unique tokens
    """
    if len(sys.argv) != 2:
        print("Format: python3 PartA.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]

    tokens = tokenize(file_path)
    frequencies = computeWordFrequencies(tokens)
    
    printFrequencies(frequencies)


if __name__ == "__main__":
    main()