import os
from urllib.parse import quote_plus
import imports  # your convenience module
from useful_sql import rows, assessment_results

# --- Path to your .accdb ---
ACCESS_DB = imports.DB_Path()
# If the app might run as a service or different user, UNC paths are safer:
# ACCESS_DB = r"\\YourServer\YourShare\Jade.Garner\Personal_Projects\comment_generator\YourDb.accdb"

# Sanity check so you get a clear error if the path is wrong or V: isn't mapped
if not os.path.exists(ACCESS_DB):
    raise FileNotFoundError(f"Access DB not found: {ACCESS_DB}")

# --- Build a safe ODBC connection string ---
odbc_str = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    rf"DBQ={ACCESS_DB};"
)
DB_URI = f"access+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"

engine = imports.create_engine(DB_URI, future=True)

app = imports.Flask(__name__)

# Reflect existing tables (optional; can be skipped if you just use raw SQL)
Base = imports.automap_base()
Base.prepare(autoload_with=engine)

TABLE_NAME = "student_table"   # wrap in [ ] in SQL below, which you already do

@app.route("/")
def home():
    return "<p>Go to <a href='/rows'>/rows</a> to see data.</p>"

@app.route("/rows")

def rows_page():
    data = rows(engine, TABLE_NAME)              # all rows
    cols = list(data[0].keys()) if data else []  # simple columns
    return imports.render_template("rows.html", columns=cols, rows=data)

@app.route("/rows.json")
def rows_json():
    with engine.connect() as conn:
        result = conn.execute(imports.text(f"SELECT TOP 100 * FROM [{TABLE_NAME}]"))
        cols = result.keys()
        data = [dict(zip(cols, row)) for row in result.fetchall()]
    return imports.jsonify(data)

@app.route("/assessment/<int:assessment_id>")
def assessment_by_id(assessment_id):
    data = assessment_results(engine, assessment_id=assessment_id)
    if not data:
        return f"<p>No results for assessment_id {assessment_id}</p>", 404
    cols = ["StudentID", "StudentName", "TotalScore"]  # choose which columns to show
    return imports.render_template("assessment.html",
                                   title=f"Assessment #{data[0]['AssessmentID']} — {data[0]['AssessmentName']}",
                                   columns=cols,
                                   rows=data)

@app.route("/assessment/by-name/<path:name>")
def assessment_by_name(name):
    data = assessment_results(engine, assessment_name=name)
    if not data:
        return f"<p>No results for assessment name '{name}'</p>", 404
    cols = ["StudentID", "StudentName", "TotalScore"]
    return imports.render_template("assessment.html",
                                   title=f"{data[0]['AssessmentName']} (ID {data[0]['AssessmentID']})",
                                   columns=cols,
                                   rows=data)

if __name__ == "__main__":
    app.run(debug=True)