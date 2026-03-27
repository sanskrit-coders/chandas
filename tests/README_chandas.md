# Sanskrit Poetry Chandas Verifier

[Generated - may be outdated]

This project provides an end-to-end pipeline for generating, verifying, and evaluating Sanskrit poetry with respect to traditional metrical constraints (Chandas). It leverages the [chandas](https://github.com/sanskrit-coders/chandas) library for meter analysis and OpenAI LLMs for both verse generation and semantic grading.

---

## Features

- **Prompt Generation:** Randomly generates Sanskrit poetry prompts with a specified topic and meter.
- **Verse Generation:** Uses OpenAI LLMs to generate Sanskrit verses according to the prompt.
- **Meter Verification:** Analyzes the generated verse using the chandas library to check if it matches the requested meter, with robust Devanagari-to-IAST normalization.
- **Semantic Grading:** Uses an LLM (optionally a different "thinking" model) to grade the verse for meaning, topic relevance, authenticity, and completeness.
- **Syllable Analysis:** Breaks down the verse into syllables for further analysis.
- **Result Storage and Analysis:** Saves results and provides meter-wise performance statistics.

---

## Usage

1. **Install dependencies:**
    ```bash
    pip install git+https://github.com/sanskrit-coders/chandas indic-transliteration openai
    ```

2. **Set your OpenAI API key:**
    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

3. **Run the script:**
    ```bash
    python sanskrit_poetry_chandas_verifier.py
    ```

4. **Review the output:**  
   Results, including meter match statistics and semantic grading, will be printed and saved to disk.

---

## File Structure

- `sanskrit_poetry_chandas_verifier.py` — Main pipeline for prompt generation, verse generation, meter verification, grading, and analysis.

---

## Next Steps

1. **Complete Function Implementations:**  
   Fill in the missing logic for all functions in the script, ensuring robust error handling and logging.

2. **Test the Pipeline:**  
   Run the full pipeline on a small dataset and verify that meter and semantic grading work as expected.

3. **Refine LLM Prompts:**  
   Improve prompts for both generation and grading. Consider using a different model for grading to reduce bias.

4. **Expand Dataset and Metrics:**  
   Add more topics, meters, and prompt styles. Include more detailed evaluation metrics.

5. **Add Human Evaluation (Optional):**  
   Manually review a sample of outputs to benchmark LLM grader reliability.

6. **Document and Share:**  
   Write clear documentation and consider adding a CLI or notebook interface. Share your results and code with the community.

---

## References

- [chandas library](https://github.com/sanskrit-coders/chandas)
- [OpenAI API documentation](https://platform.openai.com/docs/)
- [Indic Transliteration](https://github.com/indic-transliteration/indic_transliteration_py)
