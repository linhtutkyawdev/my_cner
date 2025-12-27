import pyidaungsu as pds
import os
from pathlib import Path
import re
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def tokenize_line(line):
    # Regex to find sequences of Burmese characters
    burmese_pattern = r'[\u1000-\u109F]+'
    
    def tokenize_burmese_match(match):
        # Remove spaces and then tokenize
        burmese_text = "".join(match.group(0).split())
        tokens = pds.tokenize(burmese_text, form="word")
        return " ".join(tokens)

    # Substitute only Burmese parts
    processed_line = re.sub(burmese_pattern, tokenize_burmese_match, line)
    
    # Remove space before '။'
    result = re.sub(r'\s+။', '။', processed_line)
    return result.strip()

def process_file(input_path, output_dir):
    output_path = output_dir / input_path.name
    print(f"Processing {input_path} -> {output_path}")
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            tokenized_line = tokenize_line(line)
            outfile.write(tokenized_line + '\n')
    return f"Finished processing {input_path}"


def main():
    sanitized_dir = Path('data/sanitized')
    tokenized_dir = Path('data/tokenized')

    if not sanitized_dir.is_dir():
        print(f"Directory not found: {sanitized_dir}")
        return

    if not tokenized_dir.exists():
        tokenized_dir.mkdir(parents=True)

    files_to_process = [sanitized_dir / filename for filename in os.listdir(sanitized_dir) if filename.endswith(".txt")]

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(process_file, file_path, tokenized_dir) for file_path in files_to_process]
        for future in futures:
            try:
                print(future.result())
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
