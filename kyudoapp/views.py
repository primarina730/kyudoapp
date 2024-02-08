from flask import render_template, request, redirect, url_for
from kyudoapp import app
from kyudoapp import db
from kyudoapp.models.result import Result
import sqlite3
import pandas as pd
import time
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import base64
from io import BytesIO
import sqlalchemy as sq


@app.route('/')
def index():
    DATABASE = "instance/kyudo_flask.db"
    con = sqlite3.connect(DATABASE)
    db = con.execute('SELECT * FROM result').fetchall()
    result_db = []
    for row in db:
        result_db.append(
            {'id': row[0], 'created_at': row[1], 'updated_at': row[2], 'position1': row[3], 'atari1': row[4], 'position2': row[5], 'atari2': row[6], 'memo': row[7]})

    if result_db:
        df = pd.DataFrame(result_db)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_at'] = df['created_at'].dt.date

        def check_atari(value):
            return 1 if value != 3 else 0

        df['atari1_check'] = df['atari1'].apply(check_atari)
        df['atari2_check'] = df['atari2'].apply(check_atari)
        df['yakazu'] = df['atari1_check'] + df['atari2_check']

        daily_count = pd.DataFrame()
        grouped_df = df.groupby("created_at")[
            'yakazu'].size().reset_index(name='count')
        daily_count['date'] = grouped_df['created_at']
        daily_count['yakazu_count'] = grouped_df['count']*2

        today = datetime.today().date()
        yday = today+timedelta(days=-1)
        wago = today+timedelta(weeks=-1)
        mago = today+relativedelta(months=-1)

        dft = df[df["created_at"] == today]
        dfy = df[df["created_at"] == yday]
        dfw = df[df["created_at"] > wago]
        dfm = df[df["created_at"] > mago]

        t_ave = ((dft["atari1"] == 1).sum()+(dft["atari2"] == 1).sum()
                 )/(dft["yakazu"].sum())
        y_ave = ((dfy["atari1"] == 1).sum()+(dfy["atari2"] == 1).sum()
                 )/(dfy["yakazu"].sum())
        w_ave = ((dfw["atari1"] == 1).sum()+(dfw["atari2"] == 1).sum()
                 )/(dfw["yakazu"].sum())
        m_ave = ((dfm["atari1"] == 1).sum()+(dfm["atari2"] == 1).sum()
                 )/(dfm["yakazu"].sum())

        x = daily_count["date"]
        y = daily_count["yakazu_count"]
        fig = Figure()
        ax = fig.subplots()
        ax.plot(x, y)
        ax.set_ylim(0, max(y)+1)
        ax.set_xlim(wago, today)
        ax.xaxis.set_tick_params(rotation=90)

        buf = BytesIO()
        fig.savefig(buf, format="png")

        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        today_f = today.strftime("%Y年%m月%d日")

        return render_template('kyudoapp/index.html', t_ave=t_ave, y_ave=y_ave, w_ave=w_ave, m_ave=m_ave, today=today_f, data=data)
    else:
        return render_template('kyudoapp/index.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        return render_template('kyudoapp/form.html')
    if request.method == 'POST':
        print('POSTデータ受け取ったので処理します')
        r = request.form['data1']
        return f'POST受け取ったよ:{r}'


@app.route('/add_result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'GET':
        return render_template('kyudoapp/add_result.html')
    if request.method == 'POST':
        position1 = request.form.get('position-1')
        position2 = request.form.get('position-2')
        atari1 = request.form.get('atari-1')
        atari2 = request.form.get('atari-2')
        memo = request.form.get('memo')

        result = Result(
            position1=position1,
            position2=position2,
            atari1=atari1,
            atari2=atari2,
            memo=memo
        )
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/results')
def result_list():
    results = Result.query.all()
    return render_template('kyudoapp/result_list.html', results=results)


@app.route('/results/<int:id>/edit', methods=['POST'])
def result_edit(id):
    result = Result.query.get(id)
    return render_template('kyudoapp/result_edit.html', rs=result)


@app.route('/results/<int:id>/update', methods=['POST'])
def result_update(id):
    result = Result.query.get(id)
    result.position1 = request.form.get('position-1')
    result.atari1 = request.form.get('atari-1')
    result.position2 = request.form.get('position-2')
    result.atari2 = request.form.get('atari-2')
    result.memo = request.form.get('memo')
    db.session.merge(result)
    db.session.commit()
    return redirect(url_for('result_list'))


@app.route('/results/<int:id>/delete', methods=['POST'])
def result_delete(id):
    result = Result.query.get(id)
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('result_list'))
