from flask import Flask
import sqlite3
from flask import render_template
from flask import request
from flask import g
import folium
from joblib import dump, load
import os
import pandas as pd
from IPython.core.display import HTML


with open('housepriceprediction.joblib', 'rb') as f:
    model = load(f)

app = Flask(__name__)
DATABASE = 'adpost.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.route("/")


def hello_name ():
    return render_template('login.html')       



@app.route('/second')
def main():
    cursor =get_db().cursor()
    query1 = "SELECT * FROM addressall ORDER BY RANDOM() LIMIT 1000"
    result = cursor.execute(query1)
    result = result.fetchall()
    username = request.args.get('value')
    print(username)

    return render_template('index.html',locate=result)



@app.route('/inside/<bhav>', methods=['GET'])
def inside(bhav):
    
    cursor1 =get_db().cursor()
    res1 = cursor1.execute('select * from addressall where address=?',(bhav,))
    print('Address: ', res1)
    
    res1 = res1.fetchall()
    l=[]
    for i in res1:
        l.append(i[0])
        l.append(i[1])
        l.append(i[2])
        l.append(i[3])
        l.append(i[13])
    print('List: ', l)
    start_coords = (-37.8136,144.9631)
    folium_map = folium.Map(location=start_coords, zoom_start=10)
    tooltip="Click ME"
    folium.Marker([l[0], l[1]], popup="<b>Lattitude:</b>"+str(l[0])+"\n"+"<b>Longtitude:</b>"+str(l[1])+"\n"+"<b>Address:</b>"+str(l[2])+"\n"+"<b>Price:</b>"+str(l[3])+"\n"+"<b>Predicted Price:</b>"+str(l[4]), tooltip=tooltip).add_to(folium_map)    
    

    if res1 is None:
        res1="No such entry"
    return render_template('ins.html',res1=res1, map = HTML(folium_map._repr_html_()), unsafe_allow_html=True)
   


@app.route('/predictpage',methods =['GET', 'POST'])
def predictionpage():

    if request.method == 'GET':
       
        return render_template('pred.html')


    if  request.method == 'POST':
        rooms = request.form['rooms']
        bathroom = request.form['bathroom']
        landsize = request.form['landsize']
        lattitude = request.form['lattitude']
        longtitude = request.form['longtitude']
        car = request.form['car']
        buildingarea = request.form['buildingarea']
        yearbuilt = request.form['yearbuilt']
        

        input_variables = pd.DataFrame([[rooms, bathroom, landsize, lattitude, longtitude, car, buildingarea, yearbuilt]],
                                       columns=['rooms', 'bathroom', 'landsize', 'lattitude', 'longtitude',
                                                 'car', 'buildingarea', 'yearbuilt'],
                                       dtype='float',
                                       index=['input'])

        predictions = model.predict(input_variables)[0]
        print(predictions)
        return render_template('pred.html',original_input={'Rooms': rooms, 'Bathroom': bathroom, 'Landsize': landsize, 'Lattitude': lattitude, 'Longtitude': longtitude, 'Car': car, 'BuildingArea': buildingarea, 'YearBuilt': yearbuilt},
                                     result=int(predictions))


     
if __name__ == '__main__':
    app.run()

