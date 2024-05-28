import json
import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from flask_mysqldb import MySQL
import requests
import boto3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)


# SageMaker endpoint configuration
SAGEMAKER_ENDPOINT_NAME = "nlp-blaztext-model-endpoint"  # Replace with your endpoint name
REGION = "us-east-2"  # Replace with your AWS region
 
# Initialize SageMaker runtime client
sagemaker_client = boto3.client('sagemaker-runtime', region_name=REGION)

# Function to process the review text
def process_review(text):
    punctuation = string.punctuation
    review = text.lower()
    review = review.replace("\r\n", " ").replace("\n\n", " ")
    translator = str.maketrans("", "", punctuation)
    review = review.translate(translator)
    return review


# Function to invoke SageMaker endpoint
def get_prediction(review):
    payload = {"instances": [review]}
    response = sagemaker_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        Body=json.dumps(payload),
        ContentType="application/json"
    )
    predictions = json.loads(response['Body'].read().decode('utf-8'))
    return predictions[0]  # Assuming single instance inference

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        product_review = request.form['product_review']
        product_class = request.form['product_class']
        product_department = request.form['product_department']
        user_age = request.form['user_age']
        
        # Call the API
        # api_url = 'http://yourapi.com/get_tag'
        # response = requests.post(api_url, json={'review': product_review})

        tag = get_prediction(process_review(product_review))
        print("taseen response:"+tag)
        tag =tag['label'][0]
        print(tag)
        tag=tag[len('__label__'):]
        print(tag)
        #tag= random.choice(["Positive", "Negative"])
        
        #Insert into MySQL
        cursor =  mysql.connection.cursor()
        cursor.execute("INSERT INTO reviews (product_review, product_class, product_department, user_age, tag) VALUES (%s, %s, %s, %s, %s)",
                       (product_review, product_class, product_department, user_age, tag))
        mysql.connection.commit()
        cursor.close()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file:
        data = pd.read_csv(file)
        
        for index, row in data.iterrows():
            product_review = row['product_review']
            product_class = row['product_class']
            product_department = row['product_department']
            user_age = row['user_age']
            
            
            # Call the API
            # api_url = 'http://yourapi.com/get_tag'
            # response = requests.post(api_url, json={'review': product_review})
            tag = get_prediction(process_review(product_review))
            #tag= random.choice(["Positive", "Negative"])
            
            # Insert into MySQL
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO reviews (product_review, product_class, product_department, user_age, tag) VALUES (%s, %s, %s, %s, %s)",
                           (product_review, product_class, product_department, user_age, tag))
            mysql.connection.commit()
        
        cursor.close()
        flash('File uploaded and data inserted successfully!', 'success')
        return redirect(url_for('index'))
    
@app.route('/charts')
def charts():
    cursor = mysql.connection.cursor()
    # cursor.execute("SELECT tag, COUNT(*) AS count FROM reviews GROUP BY tag")
    # data = cursor.fetchall()
    # cursor.close()
    
    # labels = [row[0] for row in data]
    # values = [row[1] for row in data]
    
    # return render_template('charts.html', labels=labels, values=values)    
    #cursor.execute(SELECT product_class, AVG(CASE WHEN tag='positive' THEN 1 WHEN tag='negative' THEN -1 ELSE 0 END) AS avg_tag FROM reviews GROUP BY product_class ORDER BY avg_tag DESC LIMIT 10")
    cursor.execute('''
        SELECT 
            product_class,
            (SUM(CASE WHEN tag = 'positive' THEN 1 ELSE 0 END) / 
            SUM(CASE WHEN tag IN ('positive', 'negative') THEN 1 ELSE 0 END)) * 100 AS posi_percentage
        FROM 
            reviews
        GROUP BY 
            product_class
        ORDER BY posi_percentage DESC                   

        ''')
    product_class_data = cursor.fetchall()

    cursor.execute('''
        SELECT 
            product_department,
            (SUM(CASE WHEN tag = 'positive' THEN 1 ELSE 0 END) / 
            SUM(CASE WHEN tag IN ('positive', 'negative') THEN 1 ELSE 0 END)) * 100 AS posi_percentage
        FROM 
            reviews
        GROUP BY 
            product_department
        ORDER BY posi_percentage DESC                   

        ''')
  #  cursor.execute("SELECT product_department, AVG(CASE WHEN tag='positive' THEN 1 WHEN tag='negative' THEN -1 ELSE 0 END) AS avg_tag FROM reviews GROUP BY product_department ORDER BY avg_tag DESC LIMIT 10")
    product_department_data = cursor.fetchall()

    cursor.execute("SELECT tag, COUNT(*) AS count FROM reviews GROUP BY tag")
    postive_negative_data = cursor.fetchall()


    query = '''
   WITH ranked_classes AS (    
      SELECT          
        age_range,        
        product_class,         
        tag,         
        ROW_NUMBER() OVER(PARTITION BY age_range, tag ORDER BY COUNT(*) DESC) AS class_rank  
            FROM (        
                  SELECT              
                   CASE
                     WHEN user_age BETWEEN 1 AND 10 THEN '1-10'         
                     WHEN user_age BETWEEN 11 AND 20 THEN '11-20'
                     WHEN user_age BETWEEN 21 AND 30 THEN '21-30'  
                     WHEN user_age BETWEEN 31 AND 40 THEN '31-40'
                     WHEN user_age BETWEEN 41 AND 50 THEN '41-50'       
                     WHEN user_age BETWEEN 51 AND 60 THEN '51-60'
                    WHEN user_age BETWEEN 61 AND 70 THEN '61-70'            
                    WHEN user_age BETWEEN 71 AND 80 THEN '71-80'       
                    WHEN user_age BETWEEN 81 AND 90 THEN '81-90'               
                    WHEN user_age BETWEEN 91 AND 100 THEN '91-100'       
                    ELSE 'Unknown' 
                   END AS age_range,product_class,tag        
                  FROM reviews) AS age_grouped_reviews     
                  GROUP BY age_range, product_class, tag )
                SELECT  
                   age_range,  
                   MAX(CASE WHEN tag = 'positive' AND class_rank = 1 THEN product_class ELSE NULL END) AS most_positive_class_1,   
                   MAX(CASE WHEN tag = 'positive' AND class_rank = 2 THEN product_class ELSE NULL END) AS most_positive_class_2,    
                   MAX(CASE WHEN tag = 'positive' AND class_rank = 3 THEN product_class ELSE NULL END) AS most_positive_class_3,    
                   MAX(CASE WHEN tag = 'negative' AND class_rank = 1 THEN product_class ELSE NULL END) AS most_negative_class_1, 
                   MAX(CASE WHEN tag = 'negative' AND class_rank = 2 THEN product_class ELSE NULL END) AS most_negative_class_2,    
                   MAX(CASE WHEN tag = 'negative' AND class_rank = 3 THEN product_class ELSE NULL END) AS most_negative_class_3 
                   FROM  ranked_classes 
                GROUP BY
                        age_range;
    '''

    cursor.execute(query)
    age_range_data = cursor.fetchall()
    # cursor.execute("SELECT FLOOR(user_age/10)*10 AS age_range, COUNT(id) AS count FROM reviews GROUP BY FLOOR(user_age/10)")
    # age_range_data = cursor.fetchall()


    cursor.close()
    return render_template('charts.html', 
                           product_class_data=product_class_data, 
                           product_department_data=product_department_data,
                           postive_negative_data=postive_negative_data,
                           age_range_data=age_range_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
