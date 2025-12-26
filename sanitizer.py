import re
import os
import shutil

def sanitize_text(input_path, output_path):
    """
    Reads raw text data, sanitizes it by extracting complete sentences
    containing Myanmar characters and being at least 15 characters long,
    and writes the sanitized data to a new file.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        sanitized_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Split the line by the Burmese sentence end character "။"
            sentences = stripped_line.split('။')
            for sentence in sentences:
                trimmed_sentence = sentence.strip()
                if len(trimmed_sentence) >= 30 and re.search(r'[က-၏]', trimmed_sentence):
                        # Also remove quotes and add the Burmese sentence end character
                        sanitized_lines.append(trimmed_sentence.replace("“","").replace("\"","") + "။")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the sanitized sentences to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for sentence in sanitized_lines:
                f.write(sentence + '\n')

        print(f"Sanitized data saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    raw_dir = 'data/raw'
    sanitized_dir = 'data/sanatized'

    # Clean the sanitized directory before processing
    if os.path.exists(sanitized_dir):
        for filename in os.listdir(sanitized_dir):
            file_path = os.path.join(sanitized_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(sanitized_dir)


    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(raw_dir, filename)
            output_path = os.path.join(sanitized_dir, filename)
            sanitize_text(input_path, output_path)
