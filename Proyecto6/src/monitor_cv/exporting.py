"""Exportaciones reproducibles y CSV que neutraliza fórmulas de celdas de texto."""
import csv
from io import StringIO
import json

UNITS = {"G1":"ms","G2":"frames/s","G3":"MiB","G4":"proporción","G5":"proporción","G6":"s","G7":"alertas"}


def safe_cell(value):
    if value is None:
        return ""
    if isinstance(value,(dict,list,tuple)):
        value = json.dumps(value,ensure_ascii=False,allow_nan=False)
    if isinstance(value,str) and (value.lstrip().startswith(("=","+","-","@")) or value.startswith(("\t","\r","\n"))):
        return "'"+value
    return value


def flatten(kind, records):
    if kind == "metrics":
        return [{"id":r["id"],"run_id":r["run_id"],"timestamp":r["timestamp"],
                 "metric":group,"value":value,"unit":r.get("units",UNITS)[group],
                 "window_seconds":r["window_seconds"],"event_ids":r["event_ids"]}
                for r in records for group,value in r["values"].items()]
    return records


def csv_text(kind, records):
    rows = flatten(kind,records)
    # Cabecera también en estado vacío: mantiene un contrato descargable.
    columns = sorted(set(k for row in rows for k in row)) if rows else ["id","run_id","timestamp"]
    output = StringIO(newline="")
    writer = csv.writer(output,quoting=csv.QUOTE_ALL,lineterminator="\r\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([safe_cell(row.get(k)) for k in columns])
    return "\ufeff"+output.getvalue()
