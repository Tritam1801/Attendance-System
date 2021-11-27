from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd, numpy as np

INPUT_FOLDER = '/static'
OUTPUT_FOLDER = '/static'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Att_Db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Att_Db(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.String(50), nullable=False)

    def __repr__(self) -> str:
        return f"{self.date} - {self.total}"

@app.route("/")
def home(): 
    attendance= Att_Db.query.all()
    return render_template("index.html", attendance= attendance)

@app.route("/about")
def about(): 
    return render_template("about.html")

@app.route("/results", methods= ["POST","GET"])
def results():
    if request.method == "POST":
        course= request.form['semester']

        # getting the minimum percentage
        min_perc= int(request.form['percentage'])

        # Reaing required files
        inputFile = Path(request.form['inputFile']).absolute()
        outputFile= Path(request.form['outputFile']).absolute()
        csv_data = pd.read_csv(inputFile, skiprows=4)
        output_xls = pd.read_excel(outputFile, sheet_name= 'Sheet1')

        # Striping out the requied date
        att_date = datetime.strptime(csv_data['First Seen'][0], '%Y-%m-%d %H:%M:%S').date()
            
        # Time calculation
        time_minutes = []
        for time in csv_data['Time in Call']:
            delta = timedelta(hours= int(time.split(':')[0]), minutes= int(time.split(':')[1]), seconds= int(time.split(':')[2]))
            minutes = delta.total_seconds()/60
            time_minutes.append(minutes)
        csv_data['Minutes Present'] = time_minutes
            
        # marking the present(1) or asbent(0) in csv dataframe.
        csv_data['Present/Absent']= np.where(csv_data['Minutes Present'] >= (max(csv_data['Minutes Present'])*(min_perc/100)), 1, 0)

        # Insering a blank column with the required date in output file
        output_xls[str(att_date)] = [np.NaN]*len(output_xls)
            
        # storing the appropriate attendance in output file
        for i in range(len(output_xls)):
            for j in range(len(csv_data)):
                if output_xls.loc[i, 'Student Name'].casefold() == csv_data.loc[j, 'Full Name'].casefold():
                    output_xls.loc[i, str(att_date)] = csv_data.loc[j, 'Present/Absent'].astype(int)
            
        output_xls[str(att_date)] = output_xls[str(att_date)].fillna(0)
        output_xls[str(att_date)] = output_xls[str(att_date)].astype(int)
            
        old_count= csv_data['Present/Absent'].sum()
        new_count= output_xls[str(att_date)].sum()+1
            
        print("Input Count:",old_count)
        print("Output Count:",new_count)

        total_count = new_count-1

        att = Att_Db(course= course, date=att_date, total= str(total_count))
        db.session.add(att)
        db.session.commit()
                       
        writer = pd.ExcelWriter(outputFile, engine= 'xlsxwriter')
            
        # storing results in output file
        output_xls.to_excel(writer, sheet_name= 'Sheet1', index=False)
            
        writer.save()
        
    return redirect('/')
    

@app.route("/refresh")
def refresh():
    db.session.query(Att_Db).delete()
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug= True, port=8001)
