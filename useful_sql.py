import imports

def rows(engine, table_name, top=None):
    """
    Return a list[dict] of rows from an Access table.
    - engine: SQLAlchemy engine
    - table_name: name of the table in Access
    - top: optional int to cap rows (Access uses TOP)
    """
    sql = f"SELECT {'TOP ' + str(int(top)) if top else ''} * FROM [{table_name}]"
    with engine.connect() as conn:
        result = conn.execute(imports.text(sql))
        cols = list(result.keys())
        data = [dict(zip(cols, row)) for row in result.fetchall()]
    return data

def assessment_results(engine, assessment_id, limit=None):
    """
    Returns aggregated assessment results from Access.
    """
    top = f"TOP {int(limit)} " if limit else ""
    sql_txt = f"""
    SELECT {top}
        s.[Student_ID],
        (s.[First_name] & ' ' & s.[Surname]) AS [StudentName],
        SUM(SUM(COALESCE(r.[MarksAwarded],0)) AS [TotalScore]
        ##################################################
        #FIX THIS LATER
        ####################################################
    FROM
        [student_table] AS s
        INNER JOIN [responses_table] AS r
            ON s.[Student_ID] = r.[Student_ID]
    WHERE
        r.[Assessment_ID] = :aid
    GROUP BY
        s.[Student_ID], s.[First_name], s.[Surname]
    ORDER BY
        [TotalScore] DESC, s.[Surname], s.[First_name];
    """
    with engine.connect() as conn:
        # Don't force int() here — pass the value as-is.
        rs = conn.execute(imports.text(sql_txt), {"aid": assessment_id})
        cols = rs.keys()
        return [dict(zip(cols, row)) for row in rs.fetchall()]
