import folium
from flask import Flask, render_template
from bson import json_util
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

cluster = MongoClient(f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PASSWORD')}@cluster0.vvcgq.mongodb.net/?retryWrites=true&w=majority")
db = cluster[os.getenv('DATABASE_NAME')]
collection = db[os.getenv('COLLECTION_NAME')]


#                            ------------------index.html / index--------------------------
@app.route('/',  methods=['GET'])
@app.route('/index',  methods=['GET'])

def home():
    try:
        return render_template('index.html')
    except:
        return '404 Not Found'

#                              -----------------brand.html / Brands----------------------
@app.route('/Brands',  methods=['GET'])
def brands():
    try:
        return render_template('Brands.html')
    except:
        return '404 Not Found'

#                             -------------------------about.html--------------------------------
@app.route('/about',  methods=['GET'])
def about_us():
    try:
        return render_template('About.html')
    except:
        return '404 Not Found'

#                   --------------------------Product.html / all-products-------------------

@app.route('/all-products/<company_name>',  methods=['GET'])
def all_products(company_name):
    try:
        data = collection.find({"company":company_name})

        return render_template('Products.html',data=data[0:4], company=company_name)
    except:
        return '404 Not Found'


# #                    --------------------Car-details.html / details-------------------
@app.route('/detalis/<name>',  methods=['GET'])
def details(name):
    try:
        data = collection.find_one({"Name":name})

        star_avg = collection.aggregate([
        {
            '$unwind': {
                'path': '$star'
            }
        }, {
            '$match': {
                'Name': name
            }
        }, {
            '$group': {
                '_id': '$Name', 
                'Rating': {
                    '$avg': '$star'
                }, 
                'review': {
                    '$sum': 1
                }
            }
        }
        ])
        
        stars = list(star_avg)



        relcar = collection.aggregate([
        {
            '$match': {
                'company': data['company']
            }
        }, {
            '$match': {
                'Name': {
                    '$ne': data['Name']
                }
            }
        }
    ])
        rel_car = list(relcar)

        return render_template('car-detail.html', data=data, stars=stars, related_car=rel_car)
    
    except:
        return '404 Not Found'

# #          --------------------------------comparison----------------------------------

@app.route('/compare')
def compare():
    try:
        imgurl = "https://i.ibb.co/mzwD5H0/default.jpg"
        return render_template('compare.html',image=imgurl,image1=imgurl)
    except:
        return '404 Not Found'


complist1 =[]
@app.route('/compare/<car1>')
def comparison(car1):
    complist1.clear()
    carc1 = collection.aggregate([ {
        '$match': {
            'Name': car1
        }
    }])
    for record5 in carc1:
        complist1.append(record5['Name'])
        complist1.append(record5['engine'])
        complist1.append(record5['body_type'])
        complist1.append(record5['image1'])
        complist1.append(record5['price'])
    #print("c1",complist1)
    
    star_avg1 = collection.aggregate([
    {
        '$unwind': {
            'path': '$star'
        }
    }, {
        '$match': {
            'Name': car1
        }
    }, {
        '$group': {
            '_id': '$Name', 
            'Rating': {
                '$avg': '$star'
            }, 
            'review': {
                '$sum': 1
            }
        }
    }
    ])
    '''resp = json_util.dumps(test2)
    return Response(resp, mimetype='application/json')
    print(resp)'''

    for avgstars1 in star_avg1:
        complist1.append(round(avgstars1['Rating'],1))
    return("",204)


complist2=[]
@app.route('/compares/<car2>')
def comparisons(car2):
    complist2.clear()
    carc2 = collection.aggregate([ {
        '$match': {
            'Name': car2
        }
    }])
    for record6 in carc2:
        complist2.append(record6['Name'])
        complist2.append(record6['engine'])
        complist2.append(record6['body_type'])
        complist2.append(record6['image1'])
        complist2.append(record6['price'])
    #print("c2",complist2)

        star_avg2 = collection.aggregate([
    {
        '$unwind': {
            'path': '$star'
        }
    }, {
        '$match': {
            'Name': car2
        }
    }, {
        '$group': {
            '_id': '$Name', 
            'Rating': {
                '$avg': '$star'
            }, 
            'review': {
                '$sum': 1
            }
        }
    }
    ])
    '''resp = json_util.dumps(test2)
    return Response(resp, mimetype='application/json')
    print(resp)'''

    for avgstars2 in star_avg2:
        complist2.append(round(avgstars2['Rating'],1))
    return("",204)

@app.route('/comparebutton')
def result():
    try:
        return render_template('compare.html',Name=complist1[0],engine=complist1[1],
        bodytype=complist1[2],image=complist1[3],price=complist1[4],star=complist1[5], Name1=complist2[0],
        engine1=complist2[1],
        bodytype1=complist2[2],image1=complist2[3],price1=complist2[4],star1=complist2[5])
    except:
        return '404 Not Found'


# #      ------------------------------------ maps -----------------------------------------
@app.route('/map/<loc>', methods=['GET'])
def map(loc):
    try:
        if loc == 'BMW':
            lon=30.6880702
            lat=-96.8858575
        elif loc == 'Audi':
            lon=28.3382283
            lat=-96.8825097
        elif loc == 'Honda':
            lon=32.6880702
            lat=-96.8858575
        elif loc == 'Toyota':
            lon=33.8797612
            lat=-113.8126791
        elif loc == 'Nissan':
            lon=42.2316003
            lat=-96.8858575
        elif loc == 'Lamborghini':
            lon=40.6932866
            lat=-113.8775378
        elif loc == 'KIA':
            lon=39.1015302
            lat=-116.4560085
        elif loc == 'Hyundai':
            lon=37.6137496
            lat=-116.5134254
        elif loc == 'chevrolet':
            lon=35.8084869
            lat=-96.5979544

    
        maps = folium.Map(
            location=[lon,lat],
            zoom_start=9
            #tiles='Stamen Terrain'
        )
        
        folium.Marker(
        location=[lon,lat],
        popup=loc
        ).add_to(maps)

        return maps._repr_html_()
    except:
        return 'Something went Wrong'


if __name__ == "__main__":
    app.run(port=os.getenv('PORT', 5000), debug=False)