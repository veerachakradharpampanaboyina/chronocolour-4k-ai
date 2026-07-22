"""
ChronoColor 4K AI — WebSocket Endpoint

Real-time progress updates for processing jobs via WebSocket.
Bridges Redis Pub/Sub to WebSocket connections.
"""

from __future__ import annotations

import asyncio

import orjson
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import get_pubsub_redis

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.websocket("/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str) -> None:
    """
    WebSocket endpoint for real-time job progress updates.

    Subscribes to the Redis Pub/Sub channel for the given job
    and forwards all progress messages to the WebSocket client.

    Messages are JSON objects with:
    - stage: Current pipeline stage name
    - status: Stage status (running, completed, failed)
    - progress: Overall progress percentage (0-100)
    - message: Human-readable status message
    - timestamp: ISO 8601 timestamp
    """
    await websocket.accept()
    logger.info("websocket_connected", job_id=job_id)

    redis = get_pubsub_redis()
    pubsub = redis.pubsub()
    channel = f"job:{job_id}:progress"

    try:
        await pubsub.subscribe(channel)

        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "job_id": job_id,
            "message": "Connected to progress stream",
        })

        # Listen for updates
        while True:
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=30.0,  # Send heartbeat every 30s
                )

                if message and message["type"] == "message":
                    data = orjson.loads(message["data"])
                    await websocket.send_json(data)

                    # Close connection if job is done
                    if data.get("status") in ("completed", "failed", "cancelled"):
                        await websocket.send_json({
                            "type": "completed",
                            "job_id": job_id,
                            "final_status": data.get("status"),
                        })
                        break
                else:
                    # Send heartbeat to keep connection alive
                    await websocket.send_json({
                        "type": "heartbeat",
                        "job_id": job_id,
                    })

            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "job_id": job_id,
                    })
                except WebSocketDisconnect:
                    break

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", job_id=job_id)
    except Exception as e:
        logger.error("websocket_error", job_id=job_id, error=str(e))
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception:
            pass
