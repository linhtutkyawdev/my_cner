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
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # remove various quotation marks
        content = re.sub(r'[“”«»„‟‟‟‘’‚‛"\']', "", content)
        # normalize multiple spaces and punctuation
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"\.{2,}", ".", content)
        content = re.sub(r"\?{2,}", "?", content)
        content = re.sub(r"!{2,}", "!", content)
        # split into lines at sentence-ending punctuation
        content = (
            content.replace("။", "။\n")
            .replace(". ", ".\n")
            .replace("?", "?\n")
            .replace("!", "!\n")
        )
        # split into lines array
        lines = content.splitlines()

        sanitized_lines = []
        for line in lines:
            stripped_line = line.strip()  # remove leading/trailing whitespace
            is_burmese = (
                re.search(r"[က-၏]", stripped_line) is not None
            )  # check for Myanmar characters
            is_sentence = len(stripped_line) >= 30 and (
                stripped_line.endswith("။")
                or stripped_line.endswith(".")
                or stripped_line.endswith("?")
                or stripped_line.endswith("!")
            )  # check length and ending punctuation
            is_banned = any(
                banned in stripped_line
                for banned in [
                    "အချိန်နှင့်တပြေးညီ သိရှိလိုပါသလား?",
                    "subscribe လုပ်ထားလိုက်ပါ။",
                    "အသေးစိတ် ပိုမိုသိရှိနိုင်ရန်",
                ]
            )  # check for banned phrases
            # Process only non-empty lines with Myanmar characters and of a certain length
            if is_burmese and is_sentence and not is_banned:
                sanitized_lines.append(stripped_line)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the sanitized sentences to the output file
        with open(output_path, "w", encoding="utf-8") as f:
            for sentence in sanitized_lines:
                f.write(sentence + "\n")

        print(f"Sanitized data saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    raw_dir = "data/raw"
    sanitized_dir = "data/sanitized"

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
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(sanitized_dir)

    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(raw_dir, filename)
            output_path = os.path.join(sanitized_dir, filename)
            sanitize_text(input_path, output_path)
