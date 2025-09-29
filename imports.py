from flask import Flask, render_template,jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from urllib.parse import quote_plus
from pathlib import Path


def DB_Path():
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    ACCESS_DB = DATA_DIR / "exam_data.accdb"
    return(ACCESS_DB)