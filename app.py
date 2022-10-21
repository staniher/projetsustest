import pickle
from flask import Flask, request, render_template, jsonify
import numpy as np
app = Flask(__name__)

# load data and extract all the vectors
with open('BERTModel.pkl', 'rb') as f:
    graduate_data = pickle.load(f)
#Background comes from the dataset
list_backgrounds = sorted([background['Background'] for background in graduate_data]) 
#list_backgrounds = sorted([item['Background'] for item in graduate_data])
#We select data from graduate_data to display in each balise select of html
list_bornwar = sorted(set([background['BornWar'] for background in graduate_data]))
list_instloc = sorted(set([background['InstitutionLocation'] for background in graduate_data]))
list_schwar = sorted(set([background['SchoolWar'] for background in graduate_data]))
list_family = sorted(set([background['Family'] for background in graduate_data]))
list_polfam = sorted(set([background['PoliticianFam'] for background in graduate_data]))
list_admfam = sorted(set([background['AdminstrativeFam'] for background in graduate_data]))
list_comfam = sorted(set([background['CompanyFam'] for background in graduate_data]))
list_degree = sorted(set([background['Degree'] for background in graduate_data]))

graduatekey_list = [item['graduatekey'] for item in graduate_data] #graduatekey comes from the dataset
#graduatekey_list = [background['graduatekey'] for background in graduate_data] 
@app.route("/", methods=['GET', 'POST'])
def template_test():
    if request.method == 'POST':
        #We obtain all the inputs from the html form
        bw= request.form.get('BornWar')
        il = request.form.get('InstitutionLocation')
        sw = request.form.get('SchoolWar')
        fa = request.form.get('Family')
        pfa = request.form.get('PoliticianFam')
        adfa = request.form.get('AdminstrativeFam')
        comfa = request.form.get('CompanyFam')
        dg = request.form.get('Degree')
        #We precise the metric we are using
        selected_metric ='cosine'
        #We concatenate all the obtained inputs to make background variable
        background= bw +  " " + il + " " + sw + " " +  fa + " " + pfa + " " + adfa + " " + comfa + " " + dg 
        try:
        # In case there is matching we recommend the 4 most matched
            selected_background = next(item for item in graduate_data if item['Background'] == background)
            similar_backgrounds = [graduate_data[i] for i in selected_background[selected_metric]]
            #We sort only IT graduate profiles who are employed
            rec_employed_profiles=[d for d in similar_backgrounds if d['Employed']=='employed'] 
            #We return the four most similar backgrounds to fit the space where we are displaying recommendations
            return render_template('index.html', similar_backgrounds=rec_employed_profiles[:4]) 
        
        except StopIteration:
        # In case there is no matching we will recommend after customizing
            #background
            Degree_No_match=dg
            return render_template('index.html', no_matching_results=Degree_No_match)
 
    else:
        #This else will execute before cliquing on Recommender. It fills selects of html form
        return render_template('index.html',list_bornwar=list_bornwar,list_instloc=list_instloc,
        list_schwar=list_schwar,list_family =list_family,list_polfam=list_polfam,
        list_admfam=list_admfam,list_comfam=list_comfam,list_degree=list_degree)
        
@app.route("/recommendations", methods=['GET'])
def get_recommendations():
    graduatekey = request.args.get('graduatekey', default=None, type=str)
    num_reco = request.args.get("number", default=5, type=int)
    distance = request.args.get("distance", default="cosine", type=str)
    field = request.args.get("field", default="graduatekey", type=str)
    if not graduatekey:
        return jsonify("Missing Corresponding background"), 400
    #elif distance not in ["cosine", "euclidean"]:
        #return jsonify("Distance can only be cosine"), 400
    elif num_reco not in range(1, 21):
        return jsonify("Can only request between 1 and 21 backgrounds"), 400
    elif graduatekey not in graduatekey_list:
        return jsonify("This graduatekey is not in supported backgrounds"), 400
    elif field not in graduate_data[0].keys():
        return jsonify("Field not available in the data"), 400
    else:
        try:
            selected_background = next(item for item in graduate_data if item['graduatekey'] == graduatekey)
            similar_backgrounds = [graduate_data[i][field] for i in selected_background[distance]]
            return jsonify(similar_backgrounds[:num_reco]), 200
        except Exception as e:
            return jsonify(str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)