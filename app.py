from flask import Flask, render_template, request, redirect, url_for, session
import requests
from flask_sqlalchemy import SQLAlchemy
import os 
from dotenv import load_dotenv

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nasa.db'
app.config['TRACK_MODIFICATION'] = False
app.secret_key = 'hs'

load_dotenv()
api_key = os.getenv("NASA_API_KEY")
app.secret_key = os.getenv("FLASK_SECRET_KEY")

db = SQLAlchemy(app)

class Nasa(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable = False)
    date = db.Column(db.String(15), nullable = False)
    description = db.Column(db.Text)
    url = db.Column(db.String(200), nullable = False)


@app.route('/', methods = ['GET', 'POST'])
def index():
    wanted_date = '2024-12-31'
    if request.method == 'POST':
        new_date = request.form.get('date')

        if new_date:
            wanted_date = new_date


    url = "https://api.nasa.gov/planetary/apod?api_key={}&date={}"
    data = requests.get(url.format(api_key, wanted_date)).json()

    pic = {
        'title' : data.get('title', 'No Title'),
        'date' : data.get('date', wanted_date),
        'description' : data.get('explanation', 'No description available'),
        'image' : data.get('url'),
        'copyright' : data.get('copyright')
    }

    pic_data = [pic]

    return render_template('nasa.html', pic_data = pic_data, apod_data = True)

@app.route('/save', methods=['POST'])
def save_photo():
    title = request.form.get('title')
    date = request.form.get('date')
    url = request.form.get('url')
    description = request.form.get('description')

    exists = Nasa.query.filter_by(date=date).first()

    if not exists:
        new_pic = Nasa(title=title, date=date, url=url, description=description)
        db.session.add(new_pic)
        db.session.commit()
        print(f"Saved: {title}")
    
    return redirect(url_for('index'))

@app.route('/favorites')
def favorites():
    saved_pics = Nasa.query.all()

    return render_template('favorites.html', favs = saved_pics)

@app.route('/deletes/<int:id>', methods = ['POST'])
def delete_photos(id):
    photo_to_delete = Nasa.query.get_or_404(id)

    db.session.delete(photo_to_delete)
    db.session.commit()

    return redirect(url_for('favorites'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True, port=8000)



