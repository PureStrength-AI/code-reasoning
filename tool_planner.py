from code_searcher import get_function_context
from repo_parser import generate_or_load_knowledge_from_repo, get_repo_context
from termcolor import colored
import util


def tool_selection(input):
    system_prompt = """You are an expert developer and programmer. 
        You need to act as a tool recommender according to the user's questions.
        You are giving a user question about the code repository.
        You choose one of the following tools to help you answer the question.
        Your answer should be the name of the tool. No any other words or symbol are allowed.
        The tools are defined as follows:

        - Code_Searcher: This module is designed to search for specific keywords in a code repository that are derived from a user's query. It is particularly beneficial when the user's question pertains to particular functions or variables. As an illustration, this tool could answer queries such as "How do I utilize the function named 'extract_function_name'?" or "How should I apply the function 'def supabase_vdb()?'".

        - Repo_Parser: This module conducts a fuzzy search within a code repository, offering context for inquiries concerning general procedures and operations in the repository. The inquiries may be high-level, potentially involving multiple source code files and documents. For instance, this tool could handle queries like "Which function is in charge of processing incoming messages?" or "How does the code manage the knowledge base?".

        - No_Tool: This is the default module that comes into play when the user's query doesn't have a direct connection to the code repository or when other tools can't provide a suitable answer. This module is particularly useful for handling generic programming queries that aren't specific to the codebase in question. For instance, it could address questions like "How is the 'asyncio' library used in Python?" or "Can you explain the workings of smart pointers in C++?".
        """
    user_prompt = """

        Below are some example questions and answers:

        - Question: How to use the function extract_function_name?
        - Code_Searcher

        - Question: How to use the function def supabase_vdb(knowledge_base):?
        - Code_Searcher 

        - Question: How to create a knowledge base?
        - Repo_Parser 

        - Question: How to use the knowledge base?
        - Repo_Parser 

        - Question: How does this repo generate the UI interface?
        - Repo_Parser
        
        - Question: How to use Text Splitters in this repo?
        - Repo_Parser

        - Question: How to use the python asyncio library?
        - No_Tool

        """ + f'Here is the user input: {input}'
    return util.get_chat_response(system_prompt, user_prompt, tool_planner=True)


def extract_function_name(input):
    system_prompt = """You are an expert developer and programmer. """
    user_prompt = """
        You will handle user questions about the code repository.
        Please extract the function or variable name appeared in the question.
        Only response the one name without the parameters or any other words.
        If both function and variable names are mentioned, only extract the function name.

        Below are two examples:
        - Question: How to use the function extract_function_name?
        - Answer: extract_function_name

        - Question: How to use the function def supabase_vdb(query, knowledge_base):?
        - Answer: supabase_vdb 

        """ + f'Here is the user input: {input}'
    return util.get_chat_response(system_prompt, user_prompt)

def make_relevant_question(input):
    system_prompt = """As an expert developer and programmer, you are adept at understanding and analyzing complex code-related inquiries. Your task is to synthesize user questions into a single, comprehensive question that captures the essence of their inquiries."""

    user_prompt = f"""
        Given this set of user inquiries: "{input}"
        Craft a single, integrated question that:
        - Merges the key elements of the user's latest inquiry (index 0) with any pertinent information from earlier inquiries (index 1 and beyond).
        - Provides a more complete context or deeper clarification by combining aspects of these inquiries.
        - ONLY RETURN THE QUESTION. NO OTHER EXPLAINATION.
        - REMOVE EXPLAINATION LIKE : The integrated question for the given user inquiries is
        - Is formulated as a clear, concise, and complete sentence in question form.
        - Focuses solely on generating the question, without extra commentary or information.

        Example:
        - User Inquiries: ["Can you show how to remove placeholders?", "What does the function 'x' do?"]
        - Integrated Question: "How can I remove placeholders while understanding what function 'x' does?"

        - User Inquiries: ["How do I implement feature Y?", "What are the prerequisites for feature Y?", "Can you explain the dependencies needed for Y?"]
        - Integrated Question: "What are the necessary prerequisites and dependencies to implement feature Y effectively?"
        """

    return util.get_chat_response(system_prompt, user_prompt)


def user_input_handler(input):
    input = input[-5:]
    input = input[::-1]
    input = make_relevant_question(input)
    print("Relevant question: ", input)
    tool = tool_selection(input)
    print(colored(f"Tool selected: {tool}", "green"))
    if "Code_Searcher" in tool:
        # extract the function or variable name from the input
        function_name = extract_function_name(input)
        print(function_name)
        if function_name:
            # search the function with context
            context = get_function_context(function_name)
            prompt = input + "\n\n" + \
                     f"Here are some the contexts of the function or variable {function_name}: \n\n" + context
            print(prompt)
            return prompt
    elif "Repo_Parser" in tool:
        vdb = generate_or_load_knowledge_from_repo()
        context = get_repo_context(input, vdb)
        prompt = input + "\n\n" + \
                 f"Here are some contexts about the question, which are ranked by the relevance to the question: \n\n" + context
        return prompt
    else:
        print("No tool is selected.")
        return input


if __name__ == "__main__":
    results = user_input_handler("How to build a knowledge base?")
    print(results)
