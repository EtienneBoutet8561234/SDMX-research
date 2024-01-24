from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired
from pandasdmx import Request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

class AgencyForm(FlaskForm):
    agency = SelectField('Agency', validators=[DataRequired()])
    submit = SubmitField('Next')


class DataflowForm(FlaskForm):
    dataflow = SelectField('Dataflow', validators=[DataRequired()])
    submit = SubmitField('Next')

class DimensionForm(FlaskForm):
    dimension = StringField('Dimension', validators=[DataRequired()])
    value = StringField('Value')

def get_dimensions(agency, dataflow_id):
    request = Request(agency)
    try:
        dataflow_response = request.dataflow(dataflow_id)
        dataflow = dataflow_response.dataflow[dataflow_id]
    except Exception as e:
        print(f"Error retrieving dataflow: {e}")
        return []
    try:
        dsd = dataflow.structure
        if dsd is None:
            dsd_response = request.datastructure(dataflow.structure.id)
            dsd = dsd_response.structure[dataflow.structure.id]
    except Exception as e:
        print(f"Error retrieving data structure definition: {e}")
        return []
    return [dimension.id for dimension in dsd.dimensions.components]

@app.route('/', methods=['GET', 'POST'])
@app.route('/agency', methods=['GET', 'POST'])
def agency():
    form = AgencyForm()
    agencies = ['ABS', 'ABS_XML', 'BBK', 'BIS', 'CD2030', 'ECB', 'EC_COMP', 'EC_EMPL', 'EC_GROW' ,'ESTAT' ,'ILO' ,'IMF' ,'INEGI' ,'INSEE' ,'ISTAT' ,'LSD' ,'NB', 'NBB' ,'OECD' ,'SGR' ,'SPC' ,'STAT_EE', 'UNICEF', 'UNSD', 'WB', 'WB_WDI']
    form.agency.choices = [(agency, agency) for agency in agencies]
    if form.validate_on_submit():
        session['agency'] = form.agency.data
        return redirect(url_for('dataflow'))
    return render_template('agency.html', form=form)

@app.route('/dataflow', methods=['GET', 'POST'])
def dataflow():
    form = DataflowForm()
    if 'agency' in session:
        agency = session['agency']
        estat = Request(agency)
        try:
            dataflows_response = estat.dataflow()
            form.dataflow.choices = [(df.id, df.id) for df in dataflows_response.dataflow.values()]
        except Exception as e:
            print(f"Error retrieving dataflows: {e}")
    if form.validate_on_submit():
        session['dataflow'] = form.dataflow.data
        return redirect(url_for('dimensions'))
    return render_template('dataflow.html', form=form)

@app.route('/dimensions', methods=['GET', 'POST'])
def dimensions():
    if 'agency' not in session or 'dataflow' not in session:
        return redirect(url_for('agency'))

    agency = session['agency']
    dataflow = session['dataflow']
    dimensions = get_dimensions(agency, dataflow)
    if not dimensions:
        return redirect(url_for('dataflow'))

    class DynamicDimensionsForm(FlaskForm):
        submit = SubmitField('Next')
        startPeriod = StringField('Start Period')
        endPeriod = StringField('End Period')

    for dimension in dimensions:
        
        setattr(DynamicDimensionsForm, dimension, FormField(DimensionForm))

    form = DynamicDimensionsForm()
    if form.validate_on_submit():
        session['dimensions'] = {}
        for dimension in dimensions:
            session['dimensions'][dimension] = form[dimension].data['value']
            
        return redirect(url_for('getExcel'))

    return render_template('dimensions.html', form=form, dimensions=dimensions)




@app.route('/getExcel', methods=['GET', 'POST'])
def getExcel():
    if 'dimensions' not in session:
        return redirect(url_for('dimensions'))

    agency = session['agency']
    dataflow = session['dataflow']
    dimensions = session['dimensions']

    # Construct the key for the example program dynamically
    key = {dimension: dimensions.get(dimension) for dimension in dimensions}

    # Initialize a Request for the specific agency
    request_obj = Request(agency)

    try:
        # Request the data
        data_response = request_obj.data(resource_id=dataflow, key=key)

        # Convert the data to a pandas DataFrame
        df = data_response.to_pandas()

        # Write the DataFrame to an Excel file
        df.to_excel('getExcel.xlsx', engine='openpyxl')

        # Retrieve all the previously entered data
        agency_data = f"Agency: {agency}"
        dataflow_data = f"Dataflow: {dataflow}"
        dimensions_data = "Dimensions:\n"
        for dimension, value in dimensions.items():
            dimensions_data += f"{dimension}: {value}\n"

        # Create a success message
        success_message = "Excel file created successfully!"

        return render_template('success.html', agency_data=agency_data, dataflow_data=dataflow_data, dimensions_data=dimensions_data, success_message=success_message)
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return redirect(url_for('dimensions'))


if __name__ == '__main__':
    app.run(debug=True)
