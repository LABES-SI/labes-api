from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/", summary="Health check")
def health_check():
    """Verifica se a API está no ar. Usada por load balancers e ferramentas de monitoramento para confirmar que o processo está respondendo."""
    return {"status": "ok"}
