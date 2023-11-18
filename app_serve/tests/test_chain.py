from app_serve.chain import chain

def test_chain():
    print(
          chain.invoke({"test": "1+1=?"})
          )
    