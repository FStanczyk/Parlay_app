from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import csv
import io
import re
from pathlib import Path
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.philip_snat_sport import PhilipSnatSport
from app.schemas.philip_snat import PhilipSnatSportResponse

PREDICTIONS_DIR = Path("philip_snat_models/predictions")

router = APIRouter()

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


@router.get("/philip-snat/sports", response_model=list[PhilipSnatSportResponse])
async def get_philip_snat_sports(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    sports = db.query(PhilipSnatSport).all()
    return sports


@router.post("/admin/parse-csv")
async def parse_csv(
    file: UploadFile = File(...),
    sport_id: int = Form(...),
    date: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV"
        )

    try:
        contents = await file.read()
        text = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(text))

        rows = []
        for row in csv_reader:
            rows.append(dict(row))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(
            c for c in file.filename if c.isalnum() or c in (" ", "-", "_", ".")
        ).rstrip()
        stored_filename = f"{timestamp}_{safe_filename}"
        file_path = UPLOADS_DIR / stored_filename

        with open(file_path, "wb") as f:
            f.write(contents)

        prediction_file = PhilipSnatPredictionFile(
            path=str(file_path),
            name=file.filename,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            sport_id=sport_id,
        )
        db.add(prediction_file)
        db.commit()
        db.refresh(prediction_file)

        return {
            "success": True,
            "data": rows,
            "sport_id": sport_id,
            "date": date,
            "row_count": len(rows),
            "id": prediction_file.id,
            "stored_filename": stored_filename,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV: {str(e)}",
        )


@router.get("/admin/uploads")
async def list_uploads_admin(current_user: User = Depends(require_admin)):
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append(
                    {
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )

        files.sort(key=lambda x: x["created"], reverse=True)
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}",
        )


@router.get("/philip-snat/prediction-files")
async def get_prediction_files():
    result = []
    pattern = re.compile(r"^(.+)-(\d{4}-\d{2}-\d{2})\.csv$")

    if PREDICTIONS_DIR.exists():
        for file_path in sorted(PREDICTIONS_DIR.iterdir(), reverse=True):
            if file_path.is_file() and file_path.suffix == ".csv":
                match = pattern.match(file_path.name)
                sport = match.group(1) if match else file_path.stem
                date = match.group(2) if match else None
                result.append({
                    "id": file_path.stem,
                    "name": file_path.name,
                    "sport": sport,
                    "date": date,
                })

    return result


@router.get("/uploads")
async def list_uploads(current_user: User = Depends(get_current_user)):
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append(
                    {
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )

        files.sort(key=lambda x: x["created"], reverse=True)
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}",
        )


@router.get("/admin/uploads/{filename}")
async def download_file_admin(
    filename: str, current_user: User = Depends(require_admin)
):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )

    file_path = UPLOADS_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    resolved_uploads = UPLOADS_DIR.resolve()
    resolved_file = file_path.resolve()

    if not str(resolved_file).startswith(str(resolved_uploads)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return FileResponse(path=str(file_path), filename=filename, media_type="text/csv")


@router.get("/uploads/{filename}")
async def download_file(filename: str, current_user: User = Depends(get_current_user)):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )

    file_path = UPLOADS_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    resolved_uploads = UPLOADS_DIR.resolve()
    resolved_file = file_path.resolve()

    if not str(resolved_file).startswith(str(resolved_uploads)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return FileResponse(path=str(file_path), filename=filename, media_type="text/csv")


@router.get("/philip-snat/prediction-files/{file_id}/download")
async def download_prediction_file(file_id: str):
    if ".." in file_id or "/" in file_id or "\\" in file_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file id")

    file_path = PREDICTIONS_DIR / f"{file_id}.csv"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=f"{file_id}.csv",
        media_type="text/csv",
    )


@router.get("/philip-snat/prediction-files/{file_id}/data")
async def get_prediction_file_data(file_id: str):
    if ".." in file_id or "/" in file_id or "\\" in file_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file id")

    file_path = PREDICTIONS_DIR / f"{file_id}.csv"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    pattern = re.compile(r"^(.+)-(\d{4}-\d{2}-\d{2})$")
    match = pattern.match(file_id)
    sport = match.group(1) if match else None
    date = match.group(2) if match else None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(io.StringIO(f.read()))
            rows = [dict(row) for row in csv_reader]
            headers = list(csv_reader.fieldnames or [])

        return {
            "success": True,
            "data": rows,
            "headers": headers,
            "file_id": file_id,
            "file_name": file_path.name,
            "sport": sport,
            "date": date,
            "row_count": len(rows),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading CSV file: {str(e)}",
        )


@router.delete("/admin/philip-snat/prediction-files/{file_id}")
async def delete_prediction_file(
    file_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    prediction_file = (
        db.query(PhilipSnatPredictionFile)
        .filter(PhilipSnatPredictionFile.id == file_id)
        .first()
    )

    if not prediction_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    file_path = Path(prediction_file.path)

    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file: {str(e)}",
            )

    db.delete(prediction_file)
    db.commit()

    return {"success": True, "message": "File deleted successfully"}


@router.delete("/admin/uploads/{filename}")
async def delete_file(filename: str, current_user: User = Depends(require_admin)):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )

    file_path = UPLOADS_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    resolved_uploads = UPLOADS_DIR.resolve()
    resolved_file = file_path.resolve()

    if not str(resolved_file).startswith(str(resolved_uploads)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        file_path.unlink()
        return {"success": True, "message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}",
        )
