import os
from src.generator import CNERGenerator
from rich.console import Console
from rich.progress import Progress


def run_stress_test():
    console = Console()

    # Check for API Key
    if not os.environ.get("GEMINI_API_KEY"):
        console.log("[bold red]Please set GEMINI_API_KEY environment variable.[/bold red]")
        return

    input_file = "stress_test_sentences.txt"
    output_file = "stress_test_output.jsonl"

    if not os.path.exists(input_file):
        console.log(f"[bold red]Error: {input_file} not found. Please create it first.[/bold red]")
        return

    console.log(f"[bold green]Starting Stress Test on {input_file}...[/bold green]")
    # Using the new default model gemini-1.5-flash-latest
    generator = CNERGenerator()

    # Remove old output if exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Increased batch size to 50 for efficiency as per user request
    with Progress() as progress:
        generator.process_file(input_file, output_file, batch_size=50, progress=progress)

    console.log("[bold green]Stress Test Completed![/bold green]")


if __name__ == "__main__":
    run_stress_test()
