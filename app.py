from flask import Flask, render_template, request, redirect, url_for, session
from SPARQLWrapper import SPARQLWrapper, JSON
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

authenticated = 0


def get_user(user, password):
    sparql = SPARQLWrapper("http://localhost:3030/user_info/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery("""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ui: <http://www.w3.org/ns/ui#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
        SELECT ?user_id ?password
        {
          ?user usi:user_id ?user_id 
          FILTER(?user_id = "%s"^^xsd:string).
          ?user usi:password ?password 
          FILTER(?password = "%s"^^xsd:string). 
        }
            """ % (user, password)
                    )

    try:
        ret = sparql.queryAndConvert()
        return ret["results"]["bindings"]

    except Exception as e:
        print(e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        user = get_user(email, password)

        if user:
            session['loggedin'] = True
            session['userid'] = user[0]['user_id']['value']
            session['email'] = user[0]['user_id']['value']
            mesage = 'Logged in successfully !'
            print(mesage)
            global authenticated
            authenticated = 1
            return redirect(url_for('user'))
            # return render_template('Home.html', mesage=mesage)

        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage=mesage)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


def check_user(user_id):
    sparql = SPARQLWrapper("http://localhost:3030/user_info/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ui: <http://www.w3.org/ns/ui#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
    SELECT ?user_id 
    {
      ?user usi:user_id ?user_id 
      FILTER(?user_id = "%s"^^xsd:string). 
    }
        """ % (user_id)
                    )

    try:
        ret = sparql.queryAndConvert()
        return ret["results"]["bindings"]

    except Exception as e:
        print(e)


def insert_to_sparql(user, password, username, city, state, keyword):
    sparql = SPARQLWrapper("http://localhost:3030/user_info/update")
    sparql.setReturnFormat(JSON)
    email_replaced = user.replace('@', '')
    sparql.setQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ui: <http://www.w3.org/ns/ui#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
    INSERT DATA {
    usi:user%s usi:user_id "%s";
        usi:password "%s";
        usi:has_city_preference "%s";
        usi:has_state_preference "%s";
        usi:job_keyword "%s";
        usi:user_name "%s".
    }
    """ % (email_replaced, user, password, city, state, keyword, username))
    try:
        ret = sparql.queryAndConvert()
        return ret["statusCode"]

    except Exception as e:
        print(e)


@app.route('/')
@app.route('/register', methods=['POST', 'GET'])
def register():
    if session and 'loggedin' in session and session['loggedin']:
        return redirect(url_for('user'))

    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        city = request.form['city']
        state = request.form['state']
        keyword = request.form['keyword']
        res = check_user(email)
        account = res
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not password or not email:
            mesage = 'Please fill out the form !'
        else:
            # TODO Insert to sparql
            statusCode = insert_to_sparql(email, password, username, city, state, keyword)

            mesage = 'You have successfully registered !'
            session['loggedin'] = True
            session['userid'] = email
            session['email'] = email
            mesage = 'Logged in successfully !'
            return redirect(url_for('user'))
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'

    return render_template('register.html', mesage=mesage)


def map_job_data(data):
    job_data_list = []
    urls = []
    for job in data:
        if job['url'] not in urls:
            job_data_list.append(
                {
                    'job': job['job']['value'],
                    'company': job['company']['value'],
                    'city': job['city']['value'],
                    'state': job['state']['value'],
                    'min_sal': job['min_sal']['value'],
                    'max_sal': job['max_sal']['value'],
                    'salary': job['salary']['value'],
                    'desc': job['desc']['value'],
                    'sal_type': 'Yearly' if job['sal_type']['value'].lower() == 'y' else 'Hourly',
                    'url': job['url']['value'],
                    'date': job['date']['value']
                }
            )
            urls.append(job['url'])
    return job_data_list


def search_by_keywords(u_data, combo=False):
    sparql = SPARQLWrapper("http://localhost:3030/jobs/sparql")
    sparql.setReturnFormat(JSON)

    if combo:
        sparql.setQuery("""
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    PREFIX ui: <http://www.w3.org/ns/ui#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
                    PREFIX job: <http://www.semanticweb.org/SER531/ontologies/Team-7/Jobs#>
    
                    SELECT ?job ?company ?city ?state ?desc ?sal_type ?salary ?min_sal ?max_sal ?date ?url
                    {
                      ?job_uri job:has_title ?job .
                      
                      ?job_uri job:has_description ?desc.
                      ?job_uri job:salary_type ?sal_type.
                     
                      ?job_uri job:expected_salary ?salary.
                      ?job_uri job:has_company ?company_uri .
                      ?company_uri job:company_name ?company .
               
                      ?job_uri job:has_location ?location_uri .
                      ?location_uri job:has_city ?city_uri .
                      ?city_uri job:city_name ?city .
                      
                      ?location_uri job:has_state ?state_uri .
                      ?state_uri job:state_name ?state .
                  
                      ?job_uri job:date_posted ?date.
                      ?job_uri job:job_url ?url.
                      ?job_uri job:max_salary ?max_sal.
                      ?job_uri job:min_salary ?min_sal .
                      FILTER (regex(?job, "%s", "i") && (?sal_type = "%s"^^xsd:string) && regex(?company, "%s", "i") && regex(?city, "%s", "i") && regex(?state, "%s", "i"))
                    } limit 100
                        """ % (
            u_data['keyword'], u_data['salary_type'], u_data['cname'], u_data['city'], u_data['state'])
                        )
    else:
        sparql.setQuery("""
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX ui: <http://www.w3.org/ns/ui#>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
                            PREFIX job: <http://www.semanticweb.org/SER531/ontologies/Team-7/Jobs#>

                            SELECT ?job ?company ?city ?state ?desc ?sal_type ?salary ?min_sal ?max_sal ?date ?url
                            {
                              ?job_uri job:has_title ?job .
                              
                              ?job_uri job:has_description ?desc.
                              ?job_uri job:salary_type ?sal_type.
                              
                              ?job_uri job:expected_salary ?salary.
                              ?job_uri job:has_company ?company_uri .
                              ?company_uri job:company_name ?company .
                              
                              ?job_uri job:has_location ?location_uri .
                              ?location_uri job:has_city ?city_uri .
                              ?city_uri job:city_name ?city .
                              ?location_uri job:has_state ?state_uri .
                              ?state_uri job:state_name ?state .
                              
                              ?job_uri job:date_posted ?date.
                              ?job_uri job:job_url ?url.
                              ?job_uri job:max_salary ?max_sal.
                              ?job_uri job:min_salary ?min_sal.
                              FILTER (regex(?job, "%s", "i") && (?sal_type = "%s"^^xsd:string) && regex(?company, "%s", "i") && ( regex(?city, "%s", "i") || regex(?state, "%s", "i")))
                            } limit 100
                                """ % (
            u_data['keyword'], u_data['salary_type'], u_data['cname'], u_data['location'], u_data['location'])
                        )
    try:
        ret = sparql.queryAndConvert()
        res = ret["results"]["bindings"]
        if res:
            return map_job_data(res)
        return []

    except Exception as e:
        print(e)


def get_preferences(u_data):
    sparql = SPARQLWrapper("http://localhost:3030/jobs/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX ui: <http://www.w3.org/ns/ui#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
                PREFIX job: <http://www.semanticweb.org/SER531/ontologies/Team-7/Jobs#>
				SELECT ?job ?company ?city ?state ?desc ?sal_type ?salary ?min_sal ?max_sal ?date ?url 
                
                {
                    ?job_uri job:has_title ?job .
                    ?job_uri job:has_description ?desc.
                    ?job_uri job:salary_type ?sal_type.
                    ?job_uri job:expected_salary ?salary.
                    ?job_uri job:has_company ?company_uri .
                    ?company_uri job:company_name ?company .
                    ?job_uri job:has_location ?location_uri .
                    ?location_uri job:has_city ?city_uri .
                    ?city_uri job:city_name ?city .
                    ?location_uri job:has_state ?state_uri .
                    ?state_uri job:state_name ?state .
                    ?job_uri job:date_posted ?date .
                    ?job_uri job:job_url ?url .
                    ?job_uri job:max_salary ?max_sal .
                    ?job_uri job:min_salary ?min_sal .
                    FILTER (regex(?city, "%s", "i") || regex(?state, "%s", "i") || regex(?job, "%s", "i"))
                } limit 100
		
  				
                    """ % (u_data['city'], u_data['state'], u_data['keyword'])
                    )

    try:
        ret = sparql.queryAndConvert()
        res = ret["results"]["bindings"]
        if res:
            return map_job_data(res)
        return []
    except Exception as e:
        print(e)


def get_search_results(based_on_profile=False):
    if based_on_profile:
        u_data = get_user_data(session)
        return get_preferences(u_data)

    else:
        form = request.form
        cname = form['cname']
        location = form['location']
        keyword = form['keyword']
        salary_type = form['select']
        if ',' in location:
            combo = location.split(',')
            city = combo[0].strip()
            state = combo[1].strip()
            u_data = {
                'cname': cname,
                'state': state,
                'city': city,
                'keyword': keyword,
                'salary_type': salary_type
            }
            return search_by_keywords(u_data, True)

        else:
            u_data = {
                'cname': cname,
                'location': location,
                'keyword': keyword,
                'salary_type': salary_type
            }
            return search_by_keywords(u_data)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if session and 'loggedin' in session and session['loggedin']:
        global authenticated
        if request.form:
            user_data = get_search_results()
        else:
            user_data = get_search_results(True)

        return render_template('Home.html', data=user_data)
    else:
        return render_template('login.html')


def get_user_data(session):
    sparql = SPARQLWrapper("http://localhost:3030/user_info/sparql")
    sparql.setReturnFormat(JSON)
    email = session['email']
    sparql.setQuery("""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ui: <http://www.w3.org/ns/ui#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
        SELECT ?user_name ?state ?city ?keyword ?user_email
        {
          ?user usi:user_id ?user_email .
          FILTER(?user_email = "%s"^^xsd:string).
          ?user usi:user_name ?user_name .
          ?user usi:has_city_preference ?city .
          ?user usi:has_state_preference ?state .
          ?user usi:job_keyword ?keyword
        }
            """ % (email)
                    )

    try:
        ret = sparql.queryAndConvert()
        res = ret["results"]["bindings"]
        name = res[0]['user_name']['value']
        state = res[0]['state']['value']
        city = res[0]['city']['value']
        keyword = res[0]['keyword']['value']
        email = res[0]['user_email']['value']
        return {
            'name': name,
            'state': state,
            'city': city,
            'keyword': keyword,
            'email': email
        }

    except Exception as e:
        print(e)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session and 'loggedin' in session and session['loggedin']:
        profile_data = get_user_data(session)
        return render_template('Profile.html', user_data=profile_data)
    else:
        return render_template('login.html')


def add_user_preferences(session, state, city, keyword, sal_type):
    sparql = SPARQLWrapper("http://localhost:3030/user_info/update")
    sparql.setReturnFormat(JSON)
    email_replaced = session['email'].replace('@', '')
    sparql.setQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ui: <http://www.w3.org/ns/ui#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX usi: <http://www.semanticweb.org/531/team7/userinfo#>
    INSERT DATA {
    usi:user%s usi:has_state_preference "%s";
        usi:has_city_preference "%s";
        usi:has_job_type_preference "%s";
        usi:job_keyword "%s"
    }
    """ % (email_replaced, state, city, sal_type, keyword))
    try:
        ret = sparql.queryAndConvert()
        return ret["statusCode"]
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run()
