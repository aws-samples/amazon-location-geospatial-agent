import boto3
from botocore.client import BaseClient
from botocore.config import Config
from langchain.llms import Bedrock


def get_claude_v2(max_tokens_to_sample=8100, temperature=0.05, top_k=5, top_p=0.7):
    client = get_bedrock_client()
    llm = Bedrock(model_id="anthropic.claude-v2",
                  client=client,
                  model_kwargs={
                      "max_tokens_to_sample": max_tokens_to_sample,
                      "temperature": temperature,
                      "top_k": top_k,
                      "top_p": top_p})
    return llm

def get_bedrock_client() -> BaseClient:
    session = boto3.Session()

    # Otherwise, return a client with the default credential
    cfg = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
    client: BaseClient = session.client("bedrock-runtime", region_name="us-east-1", config=cfg)
    return client
