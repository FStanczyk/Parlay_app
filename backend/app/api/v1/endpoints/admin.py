from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
import csv
import io
import re
from pathlib import Path
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.models.philip_snat_sport import PhilipSnatSport
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame
from app.models.philip_snat_khl_game import PhilipSnatKhlGame
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
        for file_path in PREDICTIONS_DIR.iterdir():
            if file_path.is_file() and file_path.suffix == ".csv":
                match = pattern.match(file_path.name)
                sport = match.group(1) if match else file_path.stem
                date = match.group(2) if match else None
                result.append(
                    {
                        "id": file_path.stem,
                        "name": file_path.name,
                        "sport": sport,
                        "date": date,
                    }
                )

    result.sort(key=lambda x: (x["date"] or "", x["sport"]), reverse=True)

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file id"
        )

    file_path = PREDICTIONS_DIR / f"{file_id}.csv"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return FileResponse(
        path=str(file_path),
        filename=f"{file_id}.csv",
        media_type="text/csv",
    )


@router.get("/philip-snat/prediction-files/{file_id}/data")
async def get_prediction_file_data(file_id: str):
    if ".." in file_id or "/" in file_id or "\\" in file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file id"
        )

    file_path = PREDICTIONS_DIR / f"{file_id}.csv"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

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


@router.get("/philip-snat/nhl/stats")
async def get_nhl_stats(db: Session = Depends(get_db)):
    nhl_games = (
        db.query(PhilipSnatNhlGame)
        .filter(
            PhilipSnatNhlGame.prediction_winner.isnot(None),
            PhilipSnatNhlGame.winner.isnot(None),
        )
        .all()
    )

    khl_games = (
        db.query(PhilipSnatKhlGame)
        .filter(
            PhilipSnatKhlGame.prediction_winner.isnot(None),
            PhilipSnatKhlGame.winner.isnot(None),
        )
        .all()
    )

    nhl_total = len(nhl_games)
    nhl_correct = 0
    for game in nhl_games:
        predicted_home = game.prediction_winner < 0.5
        actual_home_win = game.winner == 0
        if predicted_home == actual_home_win:
            nhl_correct += 1

    khl_total = len(khl_games)
    khl_correct = 0
    for game in khl_games:
        predicted_home = game.prediction_winner < 0.5
        actual_home_win = game.winner and game.winner.lower() == "home"
        if predicted_home == actual_home_win:
            khl_correct += 1

    nhl_accuracy = (nhl_correct / nhl_total * 100) if nhl_total > 0 else 0.0
    khl_accuracy = (khl_correct / khl_total * 100) if khl_total > 0 else 0.0

    return {
        "nhl": {
            "total_games": nhl_total,
            "correct_picks": nhl_correct,
            "accuracy_percentage": round(nhl_accuracy, 2),
        },
        "khl": {
            "total_games": khl_total,
            "correct_picks": khl_correct,
            "accuracy_percentage": round(khl_accuracy, 2),
        },
    }


class GameWithPredictionResponse(BaseModel):
    id: int
    date: str
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    predicted_winner: str
    actual_winner: str
    is_correct: bool
    prediction_goals: Optional[dict] = None

    class Config:
        from_attributes = True


class PaginatedGamesResponse(BaseModel):
    games: List[GameWithPredictionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/philip-snat/nhl/games", response_model=PaginatedGamesResponse)
async def get_nhl_games_with_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    games_query = db.query(PhilipSnatNhlGame).filter(
        PhilipSnatNhlGame.prediction_winner.isnot(None),
        PhilipSnatNhlGame.winner.isnot(None),
        PhilipSnatNhlGame.home_goals_no_ot.isnot(None),
        PhilipSnatNhlGame.away_goals_no_ot.isnot(None),
    )

    total = games_query.count()
    total_pages = (total + page_size - 1) // page_size

    games = (
        games_query.order_by(PhilipSnatNhlGame.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    game_responses = []
    for game in games:
        predicted_home = game.prediction_winner < 0.5
        predicted_winner = "Home" if predicted_home else "Away"
        actual_winner = "Home" if game.winner == 0 else "Away"
        is_correct = predicted_winner == actual_winner

        game_responses.append(
            GameWithPredictionResponse(
                id=game.id,
                date=str(game.date),
                home_team=game.home_team,
                away_team=game.away_team,
                home_score=game.home_goals_no_ot,
                away_score=game.away_goals_no_ot,
                predicted_winner=predicted_winner,
                actual_winner=actual_winner,
                is_correct=is_correct,
                prediction_goals=game.prediction_goals,
            )
        )

    return PaginatedGamesResponse(
        games=game_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/philip-snat/khl/games", response_model=PaginatedGamesResponse)
async def get_khl_games_with_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    games_query = db.query(PhilipSnatKhlGame).filter(
        PhilipSnatKhlGame.prediction_winner.isnot(None),
        PhilipSnatKhlGame.winner.isnot(None),
        PhilipSnatKhlGame.home_score_no_ot.isnot(None),
        PhilipSnatKhlGame.away_score_no_ot.isnot(None),
    )

    total = games_query.count()
    total_pages = (total + page_size - 1) // page_size

    games = (
        games_query.order_by(PhilipSnatKhlGame.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    game_responses = []
    for game in games:
        predicted_home = game.prediction_winner < 0.5
        predicted_winner = "Home" if predicted_home else "Away"
        actual_winner = game.winner.capitalize() if game.winner else None
        is_correct = (
            predicted_winner.lower() == actual_winner.lower()
            if actual_winner
            else False
        )

        game_responses.append(
            GameWithPredictionResponse(
                id=game.id,
                date=str(game.date),
                home_team=game.home_team,
                away_team=game.away_team,
                home_score=(
                    int(game.home_score_no_ot) if game.home_score_no_ot else None
                ),
                away_score=(
                    int(game.away_score_no_ot) if game.away_score_no_ot else None
                ),
                predicted_winner=predicted_winner,
                actual_winner=actual_winner or "Unknown",
                is_correct=is_correct,
                prediction_goals=game.prediction_goals,
            )
        )

    return PaginatedGamesResponse(
        games=game_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


class PaginatedUsersResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/admin/users", response_model=PaginatedUsersResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users_query = db.query(User)

    total = users_query.count()
    total_pages = (total + page_size - 1) // page_size

    users = (
        users_query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedUsersResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
