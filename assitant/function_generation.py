from Lang2Logic.generator import Generator 
import json
gen = Generator("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")
def read_text_file(file_path):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
    file_path (str): The path to the text file.

    Returns:
    str: The contents of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

schema=gen.generate_schema(read_text_file("schema_prompt.txt"))
with open("schema.json", "w", encoding="utf-8") as file:
    json.dump(schema, file, indent=4)
