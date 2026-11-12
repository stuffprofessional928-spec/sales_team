import requests
import asyncio
import os
import smtplib
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, ModelSettings, set_tracing_disabled, OpenAIChatCompletionsModel
from agents.extensions.visualization import draw_graph
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
from email.message import EmailMessage
from openai import AsyncOpenAI 

load_dotenv(override=True)
set_tracing_disabled(True)

openrouter_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")
email_server = os.getenv("EMAIL_SMTP_SERVER")
email_pass = os.getenv("EMAIL_APP_PASSWORD")
email_add = os.getenv("EMAIL_ADDRESS")

client = AsyncOpenAI(base_url=openrouter_url, api_key=openrouter_key)
MODEL = "gpt-5.4-mini"
model = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)
agent = Agent(name="emailer", instructions="You are a snarky and witty agent who do mail on request", model=model)


async def main():
    result = await Runner.run(agent,"hey man")
    print(result.final_output)
    
    
asyncio.run(main())