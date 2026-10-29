from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.backup_service import (
    create_backup,
    list_backups,
    get_backup_path,
    restore_backup,
    delete_backup,
)

router = APIRouter(tags=["backup"])


@router.post("/backup/create")
def create():
    """创建备份"""
    try:
        result = create_backup()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


@router.get("/backup/list")
def list_all():
    """列出所有备份"""
    return list_backups()


@router.get("/backup/download/{backup_id}")
def download(backup_id: str):
    """下载备份"""
    backup_path = get_backup_path(backup_id)
    if not backup_path:
        raise HTTPException(status_code=404, detail="备份不存在")

    return FileResponse(
        backup_path,
        filename=f"{backup_id}.zip",
        media_type="application/zip",
    )


@router.post("/backup/restore")
async def restore(file: UploadFile = File(...)):
    """从备份恢复"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="请上传 zip 格式的备份文件")

    # 保存上传的文件
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        result = restore_backup(temp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@router.delete("/backup/{backup_id}")
def delete(backup_id: str):
    """删除备份"""
    if delete_backup(backup_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="备份不存在")
