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
from datetime import datetime
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
ALLOWED_EXTENSIONS = {".json", ".smap", ".png", ".jpg", ".jpeg", ".csv"}
ALLOWED_MIME_TYPES = {
    "application/json",
    "application/octet-stream",
    "image/png",
    "image/jpeg",
    "text/csv",
}

app_route = APIRouter(tags=["App"])


@app_route.post("/uploads")
async def upload_file(file: UploadFile = File(...)):
    try:
        # ✅ Kiểm tra extension
        name, ext = os.path.splitext(file.filename)
        ext: str = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{ext}' không được phép. Chỉ cho phép: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # ✅ Kiểm tra MIME type (FastAPI tự đọc từ header)
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400, detail=f"File type '{file.content_type}' không hợp lệ."
            )

        # ✅ Lấy thông tin thời gian
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # ✅ Tách tên và phần mở rộng
        original_name, ext = os.path.splitext(file.filename)

        # ✅ Ghép tên mới
        safe_name = f"{original_name}_{timestamp}{ext}"

        # # ✅ Tạo đường dẫn đầy đủ
        # file_path = UPLOAD_DIR / safe_name
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"status": "success", "filename": safe_name, "path": str(file_path)}

    except Exception as E:
        print(E)
        return InternalServerError(msg=str(E)).send()


@app_route.post("/uploads/multi")
async def upload_files(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        name, ext = os.path.splitext(file.filename)
        safe_name = f"{name}_{timestamp}{ext}"
        # path = UPLOAD_DIR / safe_name
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        results.append({"filename": safe_name, "path": str(file_path)})
    return results


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
