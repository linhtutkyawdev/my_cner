
import os
import time

def estimate_generation_cost_and_time():
    """
    Estimates the cost and time for mass data generation.
    """
    # Constants
    SENTENCE_COUNT = 5713
    # Using a conservative estimate of tokens per sentence
    AVG_TOKENS_PER_SENTENCE = 100  # This is a rough estimate
    # Gemini API rate limit (example, replace with actual)
    REQUESTS_PER_MINUTE = 60
    SENTENCES_PER_REQUEST = 1 # Assuming one sentence per API call for simplicity

    # Gemini 2.5 Flash pricing based on user-provided information
    COST_PER_MILLION_INPUT_TOKENS = 0.30
    COST_PER_MILLION_OUTPUT_TOKENS = 2.50
    # Assuming a 1:1 ratio of input to output tokens for estimation
    AVG_TOKENS_PER_SENTENCE_INPUT = 50
    AVG_TOKENS_PER_SENTENCE_OUTPUT = 50

    # Calculations
    total_input_tokens = SENTENCE_COUNT * AVG_TOKENS_PER_SENTENCE_INPUT
    total_output_tokens = SENTENCE_COUNT * AVG_TOKENS_PER_SENTENCE_OUTPUT
    total_tokens = total_input_tokens + total_output_tokens

    estimated_input_cost = (total_input_tokens / 1_000_000) * COST_PER_MILLION_INPUT_TOKENS
    estimated_output_cost = (total_output_tokens / 1_000_000) * COST_PER_MILLION_OUTPUT_TOKENS
    estimated_cost = estimated_input_cost + estimated_output_cost

    total_requests = SENTENCE_COUNT / SENTENCES_PER_REQUEST
    estimated_time_minutes = total_requests / REQUESTS_PER_MINUTE
    estimated_time_hours = estimated_time_minutes / 60

    print("--- Mass Generation Estimates (Updated Pricing) ---")
    print(f"Corpus Size: {SENTENCE_COUNT} sentences")
    print(f"Estimated Total Tokens: {total_tokens} (Input: {total_input_tokens}, Output: {total_output_tokens})")
    print(f"Estimated Cost: ${estimated_cost:.2f} (Input: ${estimated_input_cost:.2f}, Output: ${estimated_output_cost:.2f})")
    print(f"Estimated Time: {estimated_time_minutes:.2f} minutes (~{estimated_time_hours:.2f} hours)")
    print("---------------------------------------------------")

def main():
    """
    Main function to confirm and start the mass generation process.
    """
    estimate_generation_cost_and_time()
    
    confirm = input("Do you want to start the mass generation process? (yes/no): ")
    
    if confirm.lower() == 'yes':
        print("Starting mass generation... (This is a simulation)")
        # In a real scenario, you would call the generator.py script here.
        # For now, we'll just simulate the process.
        time.sleep(5) 
        print("Mass generation process completed. (Simulation)")
    else:
        print("Mass generation cancelled.")

if __name__ == "__main__":
    main()
