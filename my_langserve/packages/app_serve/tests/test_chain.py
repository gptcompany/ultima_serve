from app_serve.chain import chain
import os

assert os.environ.get('GITHUB_ACCESS_TOKEN'), 'GITHUB_ACCESS_TOKEN_PERSONAL not found!'
assert os.environ.get('OPENAI_API_KEY'), 'OPENAI_API_KEY not found!'
def test_chain():
    print(
          chain.invoke({"test": "1+1=?"})
          )
    