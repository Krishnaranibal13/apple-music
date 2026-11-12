from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import Album, Track
from app.settings import MUSIC_DIR
from app.scanner import scan_music

app = FastAPI(title="Apple Music Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        scan_music(db)
        print(f"Music library scanned: {MUSIC_DIR}")
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Apple Music API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/albums")
def albums_only(db: Session = Depends(get_db)):
    albums = db.query(Album).order_by(Album.id).all()
    return [{"id": album.id, "name": album.title} for album in albums]


@app.get("/albums-with-tracks")
def albums_with_tracks(db: Session = Depends(get_db)):
    albums = db.query(Album).order_by(Album.id).all()

    response = []

    for album in albums:
        tracks = (
            db.query(Track)
            .filter(Track.album_id == album.id)
            .order_by(Track.id)
            .all()
        )

        if not tracks:
            continue

        response.append({
            "id": album.id,
            "name": album.title,
            "cover": f"/artwork/{tracks[0].id}",
            "tracks": [
                {
                    "track_id": track.id,
                    "name": track.title
                }
                for track in tracks
            ]
        })

    return response


@app.get("/artwork/{track_id}")
def get_artwork(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track or not track.album or not track.album.cover:
        raise HTTPException(status_code=404, detail="Artwork not found")

    cover_path = Path(track.album.cover)

    if not cover_path.is_file():
        raise HTTPException(status_code=404, detail="Artwork file not found")

    extension = cover_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    return FileResponse(
        path=cover_path,
        media_type=media_types.get(extension, "application/octet-stream")
    )


@app.get("/stream/{track_id}")
def stream(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    audio_path = Path(track.filename)

    if not audio_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
