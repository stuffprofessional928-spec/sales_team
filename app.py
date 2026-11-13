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

USE_EMAIL= 0

openrouter_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")
email_server = os.getenv("EMAIL_SMTP_SERVER")
email_pass = str(os.getenv("EMAIL_APP_PASSWORD"))
email_add = str(os.getenv("EMAIL_ADDRESS"))
pushover_user = os.getenv("PUSHOVER_USER")
pushover_key = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

client = AsyncOpenAI(base_url=openrouter_url, api_key=openrouter_key)
MODEL = "gpt-5.4-mini"
model = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)
agent = Agent(name="emailer", instructions="You are a snarky and witty agent who do anything on request", model=model)


def send_mail(subject, textbody, htmlbody):
    messg = EmailMessage()
    messg["From"] = email_add
    messg["To"] = email_add
    messg["SUbject"] = subject
    messg.set_content(textbody)
    messg.add_alternative(htmlbody,subtype="html")
    
    with smtplib.SMTP(str(email_server),587) as server:
        server.starttls()
        server.login(email_add,email_pass)
        server.send_message(messg)


def push(message):
    payload = {"user":pushover_user,"token":pushover_key,"message":message}
    result = requests.post(pushover_url, data=payload)
    print(result.content)
    


def sendmessage(subject, textbody,htmlbody):
    if USE_EMAIL:
        print("mail")
        send_mail(subject,textbody,htmlbody)
    else:
        print("notify")
        push(f"Subject: {subject} \n\n {textbody}")
        


    
    
intro = """
    You are a sales agent working for VJSalesAI.
    a company that provide a saas tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
    You write emails.
"""

instruction1 = intro + "Your email style professional , serious with gravitas and cradibility"
instruction2 = intro + "Your email style is witty engaging and humourus"
instruction3 = intro + "Your email style in concise, to the point, in the style of a busy senior executive"


decision = """
    You pick the best cold sales email from the given options.
    Imagine you are the customer who pick whatever the best email to reply.
    Do not give the explanation, reply with selected email only.
"""

picker_agent = Agent("Sales Email Picker Agent", instructions=decision, model=model)


sales_agent1 = Agent("Professional sales agent", instructions=instruction1, model=model)
sales_agent2 = Agent("Humourus sales agent", instructions=instruction2, model=model)    
sales_agent3 = Agent("Executive sales agent", instructions=instruction3, model=model)  

# async def main():
#     result = Runner.run_streamed(sales_agent1,input="write a cold sales email")
#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
#             print(event.data.delta, end="", flush=True)

@function_tool
def send_email_tool(subject:str, textbody:str, htmlbody: str) -> str:
    """
        Send out an email with the given subject and body to all sales prospects
        
        Args:
            subject: The subject of email
            textbody: The body of email as plain text
            htmlbody: The html body of the email
    """
    
    send_mail(subject=subject,textbody=textbody,htmlbody=htmlbody)
    return "Email sent successfully"
    
    
sender_decision = """
        You pick the best cold sales email from the given options.
        Imagine you are the customer who pick whatever the best email to reply.
        Then use your tool to send email
"""


require_tool = ModelSettings(tool_choice="required")

sender_agent = Agent("Email_sender_agent", instructions=sender_decision, model=model, tools=[send_email_tool], model_settings=require_tool)




async def main():
    message = "Write a cold sales email"
    results = await asyncio.gather(
         Runner.run(sales_agent1,message),
         Runner.run(sales_agent2,message),
         Runner.run(sales_agent3,message)
    )
    outputs = [result.final_output for result in results]
    emails = "Cold sales emails: \n\n" + "\n\nEmail:\n\n".join(outputs)
    result = await Runner.run(sender_agent,emails)
    print(f"{result.final_output}")
  
asyncio.run(main())