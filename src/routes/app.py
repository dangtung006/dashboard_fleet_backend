from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
)
from fastapi.responses import JSONResponse, StreamingResponse
import gzip
import shutil
import os
from uuid import uuid4
import datetime
import json
import ijson

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app_route = APIRouter(tags=["App"])


@app_route.post("/uploads")
async def upload_file(file: UploadFile = File(...)):
    try:

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as E:
        print(E)
        return InternalServerError(msg=str(E)).send()


@app_route.get("/load_json_file/{filename}")
async def read_json_map(filename: str):

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")


@app_route.get("/load_json_file_stream/{filename}")
async def read_json_map(filename: str):

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:

        def file_iterator():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):  # đọc từng 1MB
                    yield chunk

        return StreamingResponse(file_iterator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")


@app_route.get("/download_zip_file/{filename}")
async def read_json_map(filename: str):

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:

        def file_iterator():
            with open(file_path, "rb") as f:
                compressor = gzip.compress(f.read())
                yield compressor

        return StreamingResponse(file_iterator(), media_type="application/gzip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")


@app_route.get("/load_map/{filename}/default")
async def read_json_map(filename: str):

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        fields_to_extract = [
            "header",
            "advancedPointList",
            "advancedCurveList",
            # "advancedAreaList",
            # "advancedLineList",
            # "normalPosList",
        ]
        results = {}

        with open(file_path, "rb") as f:
            for field in fields_to_extract:
                # lấy generator từng phần
                items = ijson.items(f, field)
                try:
                    results[field] = next(items)
                except StopIteration:
                    results[field] = None
                f.seek(0)  # reset về đầu file cho vòng lặp sau

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")


@app_route.get("/load_map/{filename}/{field}")
async def read_json_map(filename: str, field: str):

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(file_path, "rb") as f:
            parser = ijson.items(f, field)
            meta = next(parser)
            return meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")
