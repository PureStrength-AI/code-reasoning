1. Clone this repository and install the required packages:
```
pip install -r requirements.txt
```
2. Create a `.env` file to put your API key:
```
OPENAI_API_KEY=sk-xxxxxx
LLM_TYPE="OpenAI"
EMBEDDING_TYPE="OpenAI"
```
3. Put the repo url (e.g., Github link) in the `Repo Link` textbox and click `Analyze Code Repo` button in the GUI. Or manually clone the repo you want to learn into `code_repo` folder:
```
cd code_repo
git clone <repo_url>
```
4. Run the Assistant.
```
python run.py
```
5. Open your web browser at http://127.0.0.1:7860 to ask any questions about your repo