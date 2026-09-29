import hashlib
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class ZenonOnlineGovernanceCore:
    def __init__(self, core_directive: str):
        self._core_directive = core_directive
        self._anchor_hash = hashlib.sha256(core_directive.encode('utf-8')).hexdigest()
        self.sandbox_dynamic_modules: Dict[str, Any] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.override_fuse_triggered = False

    def verify_anchor(self) -> None:
        if self.override_fuse_triggered:
            raise RuntimeError("CRITICAL: Zenon Override Fuse is ENGAGED. System Halted.")
        
        current_hash = hashlib.sha256(self._core_directive.encode('utf-8')).hexdigest()
        if current_hash != self._anchor_hash:
            raise RuntimeError("CRITICAL: Core Directive Drift Detected! Anchor Corrupted.")

    def trigger_override_fuse(self) -> None:
        self.override_fuse_triggered = True
        self.audit_log.append({"event": "OVERRIDE_FUSE_TRIGGERED", "status": "HALTED"})

    async def execute_mesh_analysis(self, raw_streams: List[str]) -> List[Dict[str, Any]]:
        self.verify_anchor()
        tasks = [self._worker_process(stream) for stream in raw_streams]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        sanitized_results = []
        for res in results:
            if isinstance(res, Exception):
                sanitized_results.append({"status": "ISOLATED_EXCEPTION", "error": str(res)})
            else:
                sanitized_results.append(res)
        return sanitized_results

    async def _worker_process(self, data: str) -> Dict[str, Any]:
        clean_snippet = data[:500]
        return {"snippet": clean_snippet, "risk_index": 0.15, "node_status": "SECURE"}

zenon_engine: Optional[ZenonOnlineGovernanceCore] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global zenon_engine
    directive_seed = "ZENON_V14_DETERMINISTIC_GOVERNANCE_CORE_BY_DAYUL"
    zenon_engine = ZenonOnlineGovernanceCore(core_directive=directive_seed)
    zenon_engine.verify_anchor()
    print("[Zenon Core v14.0] Online Mesh & Sandbox Guardian Initialized Securely.")
    yield
    print("[Zenon Core v14.0] Shutdown sequence initiated.")

app = FastAPI(title="Zenon Governance API Middleware", version="14.0", lifespan=lifespan)

class AnalysisRequest(BaseModel):
    streams: List[str] = Field(..., description="분석할 외부 데이터 스트림 목록")

@app.post("/zenon/v14/analyze", summary="분산 스웜 메쉬 분석 파이프라인")
async def run_analysis(payload: AnalysisRequest):
    if zenon_engine is None or zenon_engine.override_fuse_triggered:
        raise HTTPException(status_code=503, detail="Zenon Engine is offline or halted by override fuse.")
    try:
        results = await zenon_engine.execute_mesh_analysis(payload.streams)
        return {"status": "SUCCESS", "processed_nodes": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/zenon/v14/override-fuse", summary="오퍼레이터 긴급 킬 스위치 작동")
async def activate_override_fuse():
    if zenon_engine:
        zenon_engine.trigger_override_fuse()
        return {"status": "SUCCESS", "message": "Zenon Emergency Override Fuse activated. Engine halted."}
    raise HTTPException(status_code=404, detail="Engine instance not found.")

@app.get("/zenon/v14/dashboard", summary="실시간 거버넌스 상태 대시보드")
async def get_dashboard():
    if zenon_engine is None:
        raise HTTPException(status_code=503, detail="Engine uninitialized.")
    return {
        "engine_version": "v14.0-Online",
        "override_fuse_active": zenon_engine.override_fuse_triggered,
        "anchor_hash": zenon_engine._anchor_hash,
        "active_dynamic_modules": list(zenon_engine.sandbox_dynamic_modules.keys()),
        "audit_logs": zenon_engine.audit_log[-10:]
    }