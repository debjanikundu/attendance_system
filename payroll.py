import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

class PayrollIntegration:
    def __init__(self, full_day_payment):
        self.full_day_payment = full_day_payment
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
        return (exit_time - entry_time).total_seconds() / 3600  # Convert to hours

    def calculate_payment(self, hours_worked):
        if hours_worked >= 6:
            return self.full_day_payment
        elif 3 <= hours_worked < 6:
            return self.full_day_payment / 2
        else:
            return 0  # No payment for less than 3 hours

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
                    payment = self.calculate_payment(hours)

                    if employee_name in payroll_summary:
                        payroll_summary[employee_name] += payment
                    else:
                        payroll_summary[employee_name] = payment

        self.update_payroll_records(payroll_summary)

    def update_payroll_records(self, payroll_data):
        payroll_ref = db.reference('payroll')
        payroll_ref.set(payroll_data)
        for employee, total_payment in payroll_data.items():
            print(f"{employee}: Payment of {total_payment} units")

if __name__ == "__main__":
    full_day_payment = 100  # Set the full-day payment amount here
    payroll_handler = PayrollIntegration(full_day_payment)
    payroll_handler.process_payroll()

