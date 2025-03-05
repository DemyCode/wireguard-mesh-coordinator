from fastapi import FastAPI

from wireguard_mesh_coordinator.utils import NewPeer, add_peer

app = FastAPI()


@app.post("/add_peer")
def add_peer_post(new_peer: NewPeer):
    add_peer(new_peer)
    return {"status": "success"}


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
