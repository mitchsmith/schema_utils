import argparse
import json
import re
from typing import List, Dict, Any

def read_file(filepath: str) -> str:
    """Reads the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        raise IOError(f"Error reading file '{filepath}': {e}")

def write_file(filepath: str, content: str) -> None:
    """Writes content to a file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Error writing to file '{filepath}': {e}")

def convert_markdown_to_json(md_content: str) -> List[Dict[str, str]]:
    """
    Parses Markdown content into a structured list of dictionaries.

    It assumes a structure where level 2 headers (##) denote new sections.
    """
    # Split the content by lines
    lines = md_content.splitlines()
    
    sections: List[Dict[str, str]] = []
    current_section: Dict[str, Any] = {}
    
    # Regular expression to find a Level 2 header (##)
    # We use r'^##\s*(.+)$' to capture the title group 1
    header_pattern = re.compile(r'^##\s*(.+)$')
    
    for line in lines:
        match = header_pattern.match(line)
        
        if match:
            # Found a new section header
            
            # 1. If we have a previously processed section, clean its content
            # and append it to the sections list.
            if current_section:
                # Clean content: strip surrounding whitespace and replace 
                # multiple newlines (from empty lines) with two newlines 
                # (to preserve paragraph separation)
                cleaned_content = current_section['content'].strip()
                cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)
                current_section['content'] = cleaned_content
                sections.append(current_section)
                
            # 2. Start a new section
            title = match.group(1).strip()
            current_section = {
                'title': title,
                'content': ''
            }
        else:
            # This is content (paragraph, list, etc.) for the current section
            if current_section:
                current_section['content'] += line + '\n'
    
    # After the loop, append the last processed section if it exists
    if current_section:
        cleaned_content = current_section['content'].strip()
        cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)
        current_section['content'] = cleaned_content
        sections.append(current_section)
        
    return sections

def main():
    """Main function to handle file arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description="Convert a structured Markdown file to a JSON array of objects, using '##' headers as section titles."
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='The path to the input Markdown (.md) file.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output.json',
        help='The path for the output JSON (.json) file. Defaults to "output.json".'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Reading content from: {args.input_file}")
        md_content = read_file(args.input_file)
        
        if not md_content.strip():
            print("Input Markdown file is empty. Generating empty JSON.")
            json_data = []
        else:
            json_data = convert_markdown_to_json(md_content)
        
        # Serialize the Python list/dict to a pretty-printed JSON string
        json_output = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        write_file(args.output, json_output)
        
        print(f"Successfully converted '{args.input_file}' to JSON.")
        print(f"Output saved to: {args.output}")
        
    except (FileNotFoundError, IOError) as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
