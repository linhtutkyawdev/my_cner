import os
import json
import time
import sys
import random
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress

# Add the parent directory to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, VALIDATION_PROMPT

load_dotenv()

# Configure API Key
API_KEY = os.environ.get("GEMINI_API_KEY")

console = Console()


def _strip_markdown(text: str) -> str:
    """Removes markdown code block formatting from a string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class CNERGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initialize the Gemini Generator.
        Args:
            model_name (str): The Gemini model to use. Defaults to "gemini-2.5-flash-lite".
        """
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def generate_batch(
        self, sentences: List[str], retry_count: int = 5, temperature: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Sends a batch of sentences to Gemini to get CNER tags.
        Args:
            sentences (List[str]): List of raw Burmese sentences.
            retry_count (int): Number of times to retry on API failure.
            temperature (float): The generation temperature.
        Returns:
            List[Dict[str, Any]]: List of processed sentence objects with entities.
        """
        # Dynamically create a few-shot prompt
        num_examples = min(len(FEW_SHOT_EXAMPLES), 2)  # Use up to 2 examples
        selected_examples = random.sample(FEW_SHOT_EXAMPLES, num_examples)

        few_shot_prompt = "Here are some examples of how to format the output:\n\n"
        for ex in selected_examples:
            few_shot_prompt += f"Input:\n{ex['input']}\n\nOutput:\n{json.dumps(ex['output'], ensure_ascii=False, indent=2)}\n\n"

        # Construct the user prompt with the batch of sentences
        user_prompt = "Please process the following sentences and return the JSON object with the 'sentences' key:\n\n"
        for i, sent in enumerate(sentences):
            user_prompt += f"{i+1}. {sent}\n"

        full_prompt = f"{SYSTEM_PROMPT}\n\n{few_shot_prompt}{user_prompt}"

        for attempt in range(retry_count):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[full_prompt],
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        response_mime_type="application/json",
                    )
                )

                clean_text = _strip_markdown(response.text)
                data = json.loads(clean_text)

                if "sentences" in data and isinstance(data["sentences"], list):
                    return data["sentences"]
                else:
                    console.log(f"[bold yellow]Warning: Unexpected JSON structure: {data.keys()}[/bold yellow]")
                    return []

            except Exception as e:
                console.log(f"[bold red]API Error (Attempt {attempt+1}/{retry_count}): {e}[/bold red]")
                if "429" in str(e) or "503" in str(e) or "SSL" in str(e):
                    sleep_time = 15 * (attempt + 1)  # Exponential backoff
                    console.log(f"Rate limit or server error. Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    time.sleep(2)

        console.log("[bold red]Failed to process batch after retries.[/bold red]")
        return []

    def validate_and_correct_batch(
        self,
        results: List[Dict[str, Any]],
        taxonomy: set,
        max_correction_loops: int = 5,
        retry_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Validates and corrects entities in a batch, looping until all are valid.
        """
        corrected_results = list(results)  # Create a mutable copy

        for loop_num in range(max_correction_loops):
            invalid_entities_found = False
            
            # Find entries that need correction
            entries_to_correct = []
            for i, result in enumerate(corrected_results):
                invalid_objects = []
                if "entities" in result and isinstance(result["entities"], list):
                    for entity in result["entities"]:
                        if "label" in entity and entity["label"] not in taxonomy:
                            invalid_objects.append(entity)
                
                if invalid_objects:
                    entries_to_correct.append((i, result, invalid_objects))
                    invalid_entities_found = True

            if not invalid_entities_found:
                console.log(f"[bold green]Validation loop {loop_num+1}: No invalid entities found. Batch is clean.[/bold green]")
                break  # Exit the loop if the batch is clean

            console.log(f"[bold yellow]Validation loop {loop_num+1}: Found {len(entries_to_correct)} sentences with invalid entities. Correcting...[/bold yellow]")

            for idx, result, invalid_objs in entries_to_correct:
                prompt = (
                    f"{VALIDATION_PROMPT}\n\n"
                    f"The following objects in 'entities' were found to be incorrect. Please correct them.\n\n"
                    f"Wrongful Objects:\n{json.dumps(invalid_objs, ensure_ascii=False, indent=2)}\n\n"
                    f"Original Sentence: {result['text']}\n\n"
                    f"Full Original JSON:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
                )

                for attempt in range(retry_count):
                    try:
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=[prompt],
                            config=types.GenerateContentConfig(
                                temperature=0.0,
                                response_mime_type="application/json",
                            )
                        )
                        clean_text = _strip_markdown(response.text)
                        data = json.loads(clean_text)
                        corrected_results[idx] = data  # Update the result in the list
                        break
                    except Exception as e:
                        console.log(f"[bold red]Correction Error (Attempt {attempt+1}/{retry_count}): {e}[/bold red]")
                        time.sleep(2)
                else:
                    console.log(f"[bold red]Failed to correct result after retries: {result['text']}[/bold red]")
                    # Keep the last known version if correction fails
        else:
             console.log(f"[bold red]Exceeded max validation loops ({max_correction_loops}). Some invalid entities may remain.[/bold red]")


        return corrected_results

    def process_file(self, input_file: str, output_file: str, batch_size: int = 50, progress: Optional[Progress] = None, skip_sentences: set = set()):
        """
        Reads a file of sentences, processes them in batches, and saves to JSONL.
        """
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                all_sentences = [line.strip() for line in f if line.strip()]
                
            if skip_sentences:
                sentences = [s for s in all_sentences if s not in skip_sentences]
                console.log(f"Skipping {len(all_sentences) - len(sentences)} already processed sentences.")
            else:
                sentences = all_sentences

        except FileNotFoundError:
            console.log(f"[bold red]Input file not found: {input_file}[/bold red]")
            return

        console.log(f"Loaded {len(sentences)} lines from {input_file}")

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        total_batches = (len(sentences) + batch_size - 1) // batch_size
        console.log(f"Starting processing. Output will be streamed to {output_file}")

        task = None
        if progress:
            task = progress.add_task("[cyan]Processing...", total=total_batches)
            # Use the progress console for logging to avoid breaking the layout
            log_console = progress.console
        else:
            log_console = console
        
        taxonomy = {
            "PER", "LOC", "ORG", "DATE", "NUM", "ROLE", "EVENT", "LAW", "THEORY",
            "GROUP", "FOOD", "FIELD", "LANGUAGE", "ART", "ARTIFACT", "SUBSTANCE",
            "DISEASE", "MONEY"
        }

        for i in range(0, len(sentences), batch_size):
            batch_num = i // batch_size + 1
            batch = sentences[i : i + batch_size]
            log_console.log(f"Processing batch {batch_num}/{total_batches}...")

            # First Pass: Extraction
            initial_results = self.generate_batch(batch)
            
            # Second Pass: Validation and Correction Loop
            log_console.log(f"Validating and correcting batch {batch_num}/{total_batches}...")
            final_results = self.validate_and_correct_batch(initial_results, taxonomy)

            
            skipped_count = 0

            if final_results:
                with open(output_file, "a", encoding="utf-8") as f:
                    for result in final_results:
                        if isinstance(result, dict) and result.get("entities"):
                            f.write(json.dumps(result, ensure_ascii=False) + "\n")
                        else:
                            skipped_count += 1
                if skipped_count > 0:
                    log_console.log(f"[yellow]Skipped {skipped_count} non-sentence or empty results in batch {batch_num}.[/yellow]")
            else:
                log_console.log(f"[yellow]Batch {batch_num} failed or returned no results.[/yellow]")
            
            if progress and task is not None:
                progress.update(task, advance=1)

        console.log(f"Processing complete. Data saved to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate CNER annotations using the Gemini API.")
    parser.add_argument("input_file", help="Path to the input text file (one sentence per line).")
    parser.add_argument("output_file", help="Path to the output JSONL file.")
    parser.add_argument("--batch_size", type=int, default=50, help="Number of sentences to process in each batch.")
    parser.add_argument("--model_name", type=str, default="gemini-2.5-flash", help="The Gemini model to use.")
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        console.log("[bold red]Please set the GEMINI_API_KEY environment variable.[/bold red]")
    else:
        # Ensure the output directory exists
        output_dir = os.path.dirname(args.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            console.log(f"Created output directory: {output_dir}")

        # --- Resume Logic ---
        processed_sentences = set()
        if os.path.exists(args.output_file):
            try:
                with open(args.output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if 'text' in data:
                                processed_sentences.add(data['text'])
                        except json.JSONDecodeError:
                            continue # Ignore corrupted lines
                if processed_sentences:
                    console.log(f"Found {len(processed_sentences)} sentences already processed. Resuming generation.")
            except Exception as e:
                console.log(f"[bold red]Could not read existing output file to resume: {e}[/bold red]")


        generator = CNERGenerator(model_name=args.model_name)
        
        with Progress() as progress:
            generator.process_file(
                args.input_file, 
                args.output_file, 
                batch_size=args.batch_size, 
                progress=progress,
                skip_sentences=processed_sentences
            )
