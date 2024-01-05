import re
import subprocess
import os

def extract_grep_output(line):
    # Regular expressions to match the grep output lines
    regex_colon = r'(.*):(\d+):(.*)'
    regex_dash = r'(.*?)-(\d+)-(.*)'
    match_colon = re.match(regex_colon, line)
    match_dash = re.match(regex_dash, line)

    if match_colon:
        filename, line_number, line_content = match_colon.groups()
        return [filename, line_number, line_content]
    elif match_dash:
        filename, line_number, line_content = match_dash.groups()
        return [filename, line_number, line_content]
    else:
        return ["", "", line]

def extract_function_context_typescript(search_dir, function_name):
    # Adjust the regex to match TypeScript function declarations and class methods
    function_regex = rf'\bfunction\s+{function_name}\s*\('
    extracted_functions = []

    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.ts'):  # Targeting TypeScript files
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    context = []
                    found = False
                    brace_count = 0
                    brace_found = False
                    for i, line in enumerate(lines):
                        
                        if found:
                            context.append(line)
                            brace_count += line.count("{")
                            brace_found = brace_count > 0
                            brace_count -= line.count("}")
                            if brace_found == True:
                                if brace_count == 0:
                                    extracted_functions.append((file_path, ''.join(context)))
                                    break
                        elif re.search(function_regex, line):
                            print("match")
                            found = True
                            line = line.strip()
                            context.append(line)
                            brace_count += line.count("{")
                            brace_found = brace_count > 0
    return extracted_functions


def search_function_with_context(function_name, before_lines=20, after_lines=50, search_dir="./code_repo"):
    extracted_functions = extract_function_context_typescript(search_dir=search_dir, function_name=function_name)
    command = [
        "grep",
        "-r",  # Recursive search
        "-n",  # Print line numbers
        f"-B{before_lines}",  # Show context before the match
        f"-A{after_lines}",  # Show context after the match
        f"{function_name}",  # The search pattern
        search_dir
    ]

    # Run the command and capture the output
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except:
        print("Error: grep command failed.")
        return []

    # Split the output by lines
    output_lines = result.stdout.splitlines()

    # Group the lines by occurrence
    occurrences = []
    current_filename = None
    current_lines = []
    for line in output_lines:
        if line.startswith("--"):  # This line separates occurrences
            if current_filename is not None:
                occurrences.append((current_filename, "\n".join(current_lines)))
            current_lines = []
        else:
            current_filename, line_number, line_text = extract_grep_output(line)
            if function_name in line_text:
                current_start_line = line_number + ":" + line_text
            current_lines.append(line_text)

    # Add the last occurrence if there is one
    if current_filename is not None:
        occurrences.append((current_filename, "\n".join(current_lines)))

    return extracted_functions, occurrences


def get_function_context(function_name):
    results, occ = search_function_with_context(function_name)
    output = ""
    for filename, context in results:
        output += f"Filename: {filename}\n"
        output += "Context:\n"
        output += context
        output += "\n\n"

    for filename, context in occ:
        output += f"Filename: {filename}\n"
        output += "Context:\n"
        output += context
        output += "\n\n"

    return output


# if __name__ == "__main__":
#     function_name = "set_visible_true"
#     results = search_function_with_context(function_name)

#     for filename, start_line, context in results:
#         print(f"Filename: {filename}")
#         print(f"Start line: {start_line}")
#         print("Context:")
#         print(context)
#         print()
