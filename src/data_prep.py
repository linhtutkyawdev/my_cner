import os
import glob


def merge_sanitized_files(source_dir, output_file):
    """
    Merges all .txt files from the source directory into a single output file.
    """
    print(f"Merging files from {source_dir} into {output_file}...")

    txt_files = glob.glob(os.path.join(source_dir, "*.txt"))

    if not txt_files:
        print("No .txt files found in source directory.")
        return

    total_sentences = 0
    with open(output_file, "w", encoding="utf-8") as outfile:
        for txt_file in txt_files:
            with open(txt_file, "r", encoding="utf-8") as infile:
                for line in infile:
                    line = line.strip()
                    if line:
                        outfile.write(line + "\n")
                        total_sentences += 1

    print(f"Successfully merged {len(txt_files)} files.")
    print(f"Total sentences: {total_sentences}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    # Define paths relative to the project root
    source_directory = "data/sanitized"
    output_filename = "data/corpus_full.txt"

    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    merge_sanitized_files(source_directory, output_filename)
