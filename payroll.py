import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

class PayrollIntegration:
    def __init__(self):
        self.setup_firebase()

    def setup_firebase(self):
        cred = credentials.Certificate('path/to/serviceAccountKey.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://face-recognition-1e272-default-rtdb.firebaseio.com"
        })

    def get_attendance_data(self):
        attendance_ref = db.reference('face-recognition')
        return attendance_ref.get()

    def compute_working_hours(self, entry, exit):
        entry_time = datetime.strptime(entry, '%Y-%m-%d %H:%M:%S')
        exit_time = datetime.strptime(exit, '%Y-%m-%d %H:%M:%S')
        hours_worked = (exit_time - entry_time).total_seconds() / 3600
        return hours_worked

    def process_payroll(self):
        attendance_data = self.get_attendance_data()
        payroll_summary = {}

        if attendance_data:
            for record in attendance_data.values():
                employee_name = record['name']
                entry_time = record['entry_time']
                exit_time = record['exit_time']
                
                if exit_time:
                    hours = self.compute_working_hours(entry_time, exit_time)
                    if employee_name in payroll_summary:
                        payroll_summary[employee_name] += hours
                    else:
                        payroll_summary[employee_name] = hours

        self.update_payroll_records(payroll_summary)

    def update_payroll_records(self, payroll_data):
        payroll_ref = db.reference('payroll')
        payroll_ref.set(payroll_data)
        for employee, total_hours in payroll_data.items():
            print(f"{employee}: {total_hours} hours worked")

if __name__ == "__main__":
    payroll_handler = PayrollIntegration()
    payroll_handler.process_payroll()
