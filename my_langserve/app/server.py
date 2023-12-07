from typing import Any, Dict, List
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from langchain.pydantic_v1 import BaseModel
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Response
from langchain.chat_models import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from langserve import add_routes
#from app_serve.chain import chain as app_serve_chain
#from pirate_speak.chain import chain as pirate_speak_chain
import os
import asyncio
from multiprocessing import Process, Manager, freeze_support
import logging
import uvicorn
import xmlrpc.client
import subprocess
from starlette.responses import StreamingResponse
import redis
from datetime import datetime, timezone
import time
logging.basicConfig(filename='/var/log/server.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
title="LangChain Server",
version="1.0",
description="Spin up a simple api server using Langchain's Runnable interfaces",
)
# Set up your FastAPI app, including routes, etc.
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
username = "user"
password = "pass"
supervisor_url = "http://127.0.0.1:9001/RPC2"
#server = xmlrpc.client.ServerProxy(supervisor_url)
server = xmlrpc.client.ServerProxy(f'http://{username}:{password}@127.0.0.1:9001/RPC2')
# Initialize the CloudWatch logs client
cloudwatch_logs = boto3.client('logs', region_name=os.getenv('AWS_REGION'), aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/get-logs/{log_group}")
async def get_cloudwatch_logs(log_group: str = 'mycontainer', limit: int = 100):
    try:
        current_time = int(time.time() * 1000)  # Current time in milliseconds
        past_time = current_time - 3600000  # 1 hour ago in milliseconds

        response = cloudwatch_logs.filter_log_events(
            logGroupName=log_group,
            limit=limit,
            startTime=past_time,
            endTime=current_time,
            orderBy='LastEventTime',
            descending=True
        )
        return response['events']
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials are partial or incorrect")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/control/{action}/{process_name}")
async def control_process(action: str, process_name: str):
    try:
        if action == "start":
            result = server.supervisor.startProcess(process_name)
        elif action == "stop":
            result = server.supervisor.stopProcess(process_name)
        elif action == "status":
            result = server.supervisor.getProcessInfo(process_name)
        return {"action": action, "result": result}
    except Exception as e:
        return {"error": str(e)}

#add_routes(app, app_serve_chain, path="/app_serve") #app_serve_chain

#add_routes(app, pirate_speak_chain, path="/pirate-speak")
redis_host="redis-0001-001.redis.tetmd7.apne1.cache.amazonaws.com"
redis_port="6379"
key_pattern='BINANCE:BTC-USDT:book'
@app.get("/check_last_update/{key_pattern}/{threshold_seconds}")
async def check_last_update(redis_host=redis_host, redis_port=redis_port, key_pattern=key_pattern, threshold_seconds: float = 5.0):
    
    """
    Check if the last update in Redis for a given key pattern is older than the specified threshold in seconds.
    Logs a warning if the last update is more than threshold_seconds old.

    Parameters:
    - redis_host (str): Host address for the Redis server.
    - redis_port (int): Port number for the Redis server.
    - key_pattern (str): Pattern of the keys to check (e.g., 'exchange:symbol:book').
    - threshold_seconds (int): Threshold in seconds to determine if the update is recent.

    Returns:
    - bool: True if the last update is within the threshold, False otherwise.
    - str: The timestamp of the last update or an error message.
    """
    try:
        # Connect to Redis
        r = redis.Redis(host=redis_host, port=redis_port)

        # Assuming the most recent data is stored in a sorted set with timestamps as scores
        # Retrieve the latest entry's score (timestamp)
        last_update_score = r.zrange(key_pattern, -1, -1, withscores=True)

        if not last_update_score:
            return False, "No data found for the specified key pattern."

        # Extract the timestamp (score) of the last update
        _, last_timestamp = last_update_score[0]

        # Convert timestamp to a datetime object
        last_update_time = datetime.fromtimestamp(last_timestamp, tz=timezone.utc)

        # Current time
        current_time = datetime.now(timezone.utc)

        # Calculate time difference in seconds
        time_diff = (current_time - last_update_time).total_seconds()

        # Check if the time difference is greater than the threshold
        if time_diff > threshold_seconds:
            logger.warning(f"Last update is more than {threshold_seconds} seconds old. Last update was at {last_update_time.isoformat()}")
            return False, last_update_time.isoformat()

        return True, last_update_time.isoformat()

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return False, f"Error occurred: {e}"


@app.get("/stream-logs/{process_name}")
async def stream_logs(process_name: str):
    def generate():
        process = subprocess.Popen(["tail", "-f", f"/var/log/{process_name}_stdout.log"], stdout=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            yield f"data: {line.decode()}\n\n"

    return Response(generate(), media_type="text/event-stream")

def start_server():
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    start_server()
