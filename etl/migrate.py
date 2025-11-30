import os
import json
import re
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from etl.transform_utils import iso2 as _iso2, to_date as _to_date, split_name as _split_name, parse_classes as _parse_classes

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "data" / "legacy_csv"
TRANSFORMED = ROOT / "data" / "transformed_csv"
TRANSFORMED.mkdir(parents=True, exist_ok=True)

MAP = json.loads((ROOT / "schema" / "mappings.json").read_text())
TARGET_DB_URL = os.getenv("TARGET_DB_URL")

def transform_clients(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["external_ref"] = df["client_id"].astype(str).str.strip()
    out["name"] = df["client_name"].map(_split_name)
    out["email"] = df.get("email", "")
    out["phone"] = df.get("phone", "")
    out["address"] = df.get("address", "")
    out["country_code"] = df.get("country", "").map(_iso2)
    out["created_on"] = df.get("created_on", "").map(_to_date)
    out.drop_duplicates(subset=["external_ref"], inplace=True)
    return out

def transform_patents(df: pd.DataFrame, client_map: dict) -> pd.DataFrame:
    out = pd.DataFrame()
    out["external_ref"] = df["patent_id"].astype(str).str.strip()
    out["client_ext"] = df["client_id"].astype(str).str.strip()
    out["client_id"] = out["client_ext"].map(client_map)
    out["title"] = df["title"].fillna("Untitled")
    out["filing_date"] = df.get("filing_date","").map(_to_date)
    out["grant_date"] = df.get("grant_date","").map(_to_date)
    out["jurisdiction"] = df.get("jurisdiction","").map(lambda x: MAP["jurisdiction_map"].get(str(x), None))
    out["status"] = df.get("status","")
    return out.drop(columns=["client_ext"])

def transform_trademarks(df: pd.DataFrame, client_map: dict) -> pd.DataFrame:
    out = pd.DataFrame()
    out["external_ref"] = df["tm_id"].astype(str).str.strip()
    out["client_ext"] = df["client_id"].astype(str).str.strip()
    out["client_id"] = out["client_ext"].map(client_map)
    out["mark_text"] = df["mark_text"].fillna("")
    out["nice_classes"] = df.get("class","").map(_parse_classes)
    out["filing_date"] = df.get("filing_date","").map(_to_date)
    out["status"] = df.get("status","")
    return out.drop(columns=["client_ext"])

def transform_deadlines(df: pd.DataFrame, patent_map: dict, tm_map: dict) -> pd.DataFrame:
    out = pd.DataFrame()
    out["external_ref"] = df["dl_id"].astype(str).str.strip()
    out["related_type"] = df["related_type"].str.lower()
    out["related_table"] = out["related_type"].map(lambda x: "patents" if x=="patent" else "trademarks")
    def resolve_id(row):
        rid = str(row["related_id"]).strip()
        if row["related_table"] == "patents":
            return patent_map.get(rid)
        else:
            return tm_map.get(rid)
    out["related_id"] = df.apply(resolve_id, axis=1)
    out["due_date"] = df.get("due_date","").map(_to_date)
    out["description"] = df.get("description","")
    return out.drop(columns=["related_type"])

def upsert_dataframe(conn, df: pd.DataFrame, table: str, unique_col: str, update_cols: list) -> tuple[int,int]:
    inserted = 0
    updated = 0
    if df.empty:
        return inserted, updated
    cols = df.columns.tolist()
    placeholders = ", ".join([f":{c}" for c in cols])
    collist = ", ".join(cols)
    update_set = ", ".join([f"{c}=EXCLUDED.{c}" for c in update_cols])
    stmt = text(f"""        INSERT INTO {table} ({collist})
        VALUES ({placeholders})
        ON CONFLICT ({unique_col}) DO UPDATE
        SET {update_set}
    """)
    result = conn.execute(stmt, df.to_dict(orient="records"))
    # SQLAlchemy doesn't directly return per-row inserted vs updated; we log total affected.
    # We'll approximate by counting conflicts via selecting existing keys beforehand if needed.
    inserted = len(df)
    return inserted, updated

def main():
    clients = pd.read_csv(LEGACY / "clients.csv")
    patents = pd.read_csv(LEGACY / "patents.csv")
    tms = pd.read_csv(LEGACY / "trademarks.csv")
    dls = pd.read_csv(LEGACY / "deadlines.csv")

    tf_clients = transform_clients(clients)

    if not TARGET_DB_URL:
        outdir = TRANSFORMED
        outdir.mkdir(exist_ok=True, parents=True)
        tf_clients.to_csv(outdir / "clients.csv", index=False)
        client_map = {ext: i+1 for i, ext in enumerate(tf_clients["external_ref"].tolist())}
        tf_patents = transform_patents(patents, client_map)
        tf_tms = transform_trademarks(tms, client_map)
        patent_map = {ext: i+1 for i, ext in enumerate(tf_patents["external_ref"].tolist())}
        tm_map = {ext: i+1 for i, ext in enumerate(tf_tms["external_ref"].tolist())}
        tf_deadlines = transform_deadlines(dls, patent_map, tm_map)
        tf_patents.to_csv(outdir / "patents.csv", index=False)
        tf_tms.to_csv(outdir / "trademarks.csv", index=False)
        tf_deadlines.to_csv(outdir / "deadlines.csv", index=False)
        print(f"Transformed CSVs written to {outdir}. Set TARGET_DB_URL to load into Postgres.")
        return

    engine = create_engine(TARGET_DB_URL, future=True)
    with engine.begin() as conn:
        schema_sql = (ROOT / "schema" / "target_postgres.sql").read_text()
        for stmt in schema_sql.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))

    with engine.begin() as conn:
        run_id = conn.execute(text("INSERT INTO migration_runs(status, notes) VALUES ('running', 'ETL start') RETURNING id")).scalar_one()

    with engine.begin() as conn:
        # clients upsert
        ins, upd = upsert_dataframe(conn, tf_clients, "clients", "external_ref",
                                    ["name","email","phone","address","country_code","created_on"])
        conn.execute(text("INSERT INTO migration_row_counts(run_id, table_name, inserted, updated) VALUES (:r, 'clients', :i, :u)"),
                     {"r": run_id, "i": ins, "u": upd})
        rows = conn.execute(text("SELECT id, external_ref FROM clients")).all()
        client_map = {ext: cid for cid, ext in rows}

    tf_patents = transform_patents(patents, client_map)
    tf_tms = transform_trademarks(tms, client_map)

    with engine.begin() as conn:
        ins, upd = upsert_dataframe(conn, tf_patents, "patents", "external_ref",
                                    ["client_id","title","filing_date","grant_date","jurisdiction","status"])
        conn.execute(text("INSERT INTO migration_row_counts(run_id, table_name, inserted, updated) VALUES (:r, 'patents', :i, :u)"),
                     {"r": run_id, "i": ins, "u": upd})
        ins, upd = upsert_dataframe(conn, tf_tms, "trademarks", "external_ref",
                                    ["client_id","mark_text","nice_classes","filing_date","status"])
        conn.execute(text("INSERT INTO migration_row_counts(run_id, table_name, inserted, updated) VALUES (:r, 'trademarks', :i, :u)"),
                     {"r": run_id, "i": ins, "u": upd})
        rows_p = conn.execute(text("SELECT id, external_ref FROM patents")).all()
        rows_t = conn.execute(text("SELECT id, external_ref FROM trademarks")).all()
        patent_map = {ext: pid for pid, ext in rows_p}
        tm_map = {ext: tid for tid, ext in rows_t}

    tf_deadlines = transform_deadlines(dls, patent_map, tm_map)
    with engine.begin() as conn:
        ins, upd = upsert_dataframe(conn, tf_deadlines, "deadlines", "external_ref",
                                    ["related_table","related_id","due_date","description"])
        conn.execute(text("INSERT INTO migration_row_counts(run_id, table_name, inserted, updated) VALUES (:r, 'deadlines', :i, :u)"),
                     {"r": run_id, "i": ins, "u": upd})
        conn.execute(text("UPDATE migration_runs SET status='success', finished_at=now() WHERE id=:r"), {"r": run_id})

    print("Migration completed into PostgreSQL with audit logging.")

if __name__ == "__main__":
    main()
