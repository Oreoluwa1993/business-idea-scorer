from fastapi import APIRouter

from app.api.endpoints import uploads, scores, ideas

router = APIRouter()

router.include_router(uploads.router, prefix="/uploads", tags=["File Uploads"])
router.include_router(scores.router, prefix="/scores", tags=["Scoring"])
router.include_router(ideas.router, prefix="/ideas", tags=["Business Ideas"])
