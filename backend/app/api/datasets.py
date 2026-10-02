import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.data.ingestion.validators import validate_file
from app.schemas.dataset import DatasetResponse

from app.data.ingestion.service import read_dataset
from app.data.profiling.service import profile_dataframe
from app.schemas.profile import DatasetProfileResponse

from app.db.session import get_db
from app.db.models import Dataset

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)

UPLOAD_DIRECTORY = Path("storage/uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


from app.api.deps import get_current_user
from app.db.models.user import User

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
) -> DatasetResponse:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    dataset_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix.lower()
    stored_filename = f"{dataset_id}{extension}"
    from app.services.storage import storage

    try:
        # We read the entire file into memory for upload. In a production setting with giant files, 
        # we would stream it directly to S3 without keeping it in memory.
        file_bytes = await file.read()
        file_size = len(file_bytes)
        validate_file(
            filename=file.filename,
            file_size=file_size,
            max_file_size=settings.max_upload_bytes,
        )
        
        storage_path = await storage.upload_file(file_bytes, stored_filename)
        
        # Temp download for immediate profiling to ensure it's valid
        temp_file = storage.download_to_temp_file(storage_path)
        read_dataset(Path(temp_file))
        if temp_file != storage_path:
            Path(temp_file).unlink(missing_ok=True)
            
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the uploaded dataset.",
        ) from exc
    finally:
        await file.close()

    db_dataset = Dataset(
        id=uuid.UUID(dataset_id),
        user_id=current_user.id if current_user else None,
        filename=file.filename,
        file_type=extension,
        file_size=file_size,
        storage_path=storage_path,
        status="uploaded",
    )
    db.add(db_dataset)
    await db.commit()
    await db.refresh(db_dataset)

    return DatasetResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        file_type=extension,
        file_size=file_size,
        created_at=db_dataset.created_at,
        status="uploaded",
    )

@router.get(
    "/{dataset_id}/profile",
    response_model=DatasetProfileResponse,
)
async def get_dataset_profile(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
) -> DatasetProfileResponse:

    dataset = await db.get(Dataset, uuid.UUID(dataset_id))
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    if dataset.user_id and (not current_user or dataset.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this dataset.")

    from app.services.storage import storage
    temp_file = storage.download_to_temp_file(dataset.storage_path)

    try:
        df = read_dataset(Path(temp_file))
        profile = profile_dataframe(df)

    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to profile dataset.",
        ) from exc
    finally:
        if temp_file != dataset.storage_path:
            Path(temp_file).unlink(missing_ok=True)

    return DatasetProfileResponse(
        dataset_id=dataset_id,
        **profile,
    )
