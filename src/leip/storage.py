from pymongo import MongoClient


def persist(run: dict, uri: str, database: str, client=None) -> str:
    owned = client is None
    client = client if client is not None else MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        collection = client[database].extraction_runs
        collection.create_index([("artifact.sha256", 1), ("created_at", -1)])
        # Cada intento conserva su propia salida; no sobrescribe publicaciones anteriores.
        collection.insert_one(dict(run))
        return run["_id"]
    finally:
        if owned:
            client.close()
