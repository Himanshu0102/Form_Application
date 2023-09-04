from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class FormEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    Industry_Name = db.Column(db.String(100), nullable=False)
    Industry_Type = db.Column(db.String(100), nullable=False)
    Domain_Name = db.Column(db.String(100), nullable=False)
    Use_Case_Name = db.Column(db.String(100), nullable=False)
    Short_description = db.Column(db.String(250), nullable=False)
    Tools_Technologies_used = db.Column(db.String(250), nullable=False)
    Role_Played = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self) -> str:
        return f"{self.full_name} - {self.created_at}"
    
@app.route('/')
def index():
    tasks = FormEntry.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        city = request.form.get('city')

        for index in range(len(request.form.getlist('Industry_Name[]'))):
            industry_name = request.form.getlist('Industry_Name[]')[index]
            industry_type = request.form.getlist('Industry_Type[]')[index]
            domain_name = request.form.getlist('Domain_Name[]')[index]
            use_case_name = request.form.getlist('Use_Case_Name[]')[index]
            short_description = request.form.getlist('Short_description[]')[index]
            tools_technologies_used = request.form.getlist('Tools_&_Technologies_used[]')[index]
            role_played = request.form.getlist('Role_Played[]')[index]

            if industry_name:
                table_entry = FormEntry(
                    full_name=full_name,
                    username=username,
                    city=city,
                    Industry_Name=industry_name,
                    Industry_Type=industry_type,
                    Domain_Name=domain_name,
                    Use_Case_Name=use_case_name,
                    Short_description=short_description,
                    Tools_Technologies_used=tools_technologies_used,
                    Role_Played=role_played
                )
                db.session.add(table_entry)

        db.session.commit()

                # Create a DataFrame from the database records
        entries = FormEntry.query.all()
        data = {
            'Full Name': [entry.full_name for entry in entries],
            'Username': [entry.username for entry in entries],
            'City': [entry.city for entry in entries],
            'Industry Name': [entry.Industry_Name for entry in entries],
            'Industry Type': [entry.Industry_Type for entry in entries],
            'Domain Name': [entry.Domain_Name for entry in entries],
            'Use Case Name': [entry.Use_Case_Name for entry in entries],
            'Short Description': [entry.Short_description for entry in entries],
            'Tools & Technologies Used': [entry.Tools_Technologies_used for entry in entries],
            'Role Played': [entry.Role_Played for entry in entries],
            'Created At': [entry.created_at.strftime('%Y-%m-%d %H:%M:%S') for entry in entries],
        }

        df = pd.DataFrame(data)

        # Export the DataFrame to an Excel file in memory
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # Save the Excel file to the local system
        excel_filename = 'form_data.xlsx'
        with open(excel_filename, 'wb') as f:
            f.write(excel_buffer.read())

        # return jsonify({'message': 'Form data submitted successfully'})
        success_message = 'Form data submitted successfully and Excel file exported.'
        return jsonify({'success': True, 'message': success_message})
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error submitting form data'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)