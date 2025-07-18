from backend.google_integration.email_utils import send_email_via_gmail

def test_send_email():
    # Test details for sending an email
    appointment_details = {
        'patient_name': 'John Doe',
        'doctor_name': 'Dr. Ahuja',
        'appointment_date': '2023-07-22',
        'appointment_time': '10:00 AM'
    }
    
    to_email = ""  # Replace with a real email address
    
    try:
        send_email_via_gmail(to_email, "Appointment Confirmation", appointment_details)
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_send_email()
