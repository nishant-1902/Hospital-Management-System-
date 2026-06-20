from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.doctors.models import Department, Doctor
from apps.patients.models import Patient


class Command(BaseCommand):
    help = "Seed AHMS with demo admin, doctors, patients, and appointments."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        admin_user, created = User.objects.get_or_create(
            email="admin@ahms.local",
            defaults={
                "username": "admin",
                "first_name": "System",
                "last_name": "Admin",
                "role": User.ADMIN,
                "phone": "9000000000",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("Admin@12345")
            admin_user.save(update_fields=["password"])

        departments = {
            "Cardiology": Department.objects.get_or_create(name="Cardiology", defaults={"location": "Block A"})[0],
            "Orthopedics": Department.objects.get_or_create(name="Orthopedics", defaults={"location": "Block B"})[0],
            "General Medicine": Department.objects.get_or_create(name="General Medicine", defaults={"location": "Block C"})[0],
        }

        doctor_specs = [
            ("arjun.mehta@ahms.local", "Arjun Mehta", "Cardiology", "MD Cardiology", 12, "Mon,Tue,Thu"),
            ("nisha.rao@ahms.local", "Nisha Rao", "Orthopedics", "MS Orthopedics", 9, "Tue,Wed,Fri"),
            ("kabir.sen@ahms.local", "Kabir Sen", "General Medicine", "MD Internal Medicine", 15, "Mon,Wed,Fri"),
        ]

        doctors = []
        for index, (email, name, department_name, qualification, experience, days) in enumerate(doctor_specs, start=1):
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "first_name": name.split()[0],
                    "last_name": name.split()[-1],
                    "role": User.DOCTOR,
                    "phone": f"910000000{index}",
                },
            )
            if user_created:
                user.set_password("Doctor@12345")
                user.save(update_fields=["password"])

            doctor, _ = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "name": name,
                    "specialization": department_name,
                    "department": departments[department_name],
                    "qualification": qualification,
                    "experience_yrs": experience,
                    "available_days": days,
                    "consult_start": time(9, 0),
                    "consult_end": time(14, 0),
                },
            )
            doctors.append(doctor)

        patient_specs = [
            ("Aarav Sharma", "M", date(1988, 5, 14), "9200000001", "O+"),
            ("Meera Iyer", "F", date(1992, 8, 22), "9200000002", "A+"),
            ("Rohan Gupta", "M", date(1979, 1, 7), "9200000003", "B+"),
            ("Sana Khan", "F", date(2001, 11, 19), "9200000004", "AB+"),
            ("Dev Patel", "M", date(1968, 3, 30), "9200000005", "O-"),
        ]

        patients = []
        for name, gender, dob, phone, blood_group in patient_specs:
            patient, _ = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    "name": name,
                    "gender": gender,
                    "dob": dob,
                    "address": f"{name.split()[0]} Residency, Central Avenue",
                    "blood_group": blood_group,
                },
            )
            patients.append(patient)

        today = timezone.localdate()
        appointment_times = [
            time(9, 0),
            time(9, 30),
            time(10, 0),
            time(10, 30),
            time(11, 0),
            time(11, 30),
            time(12, 0),
            time(12, 30),
            time(13, 0),
            time(13, 30),
        ]

        for index in range(10):
            doctor = doctors[index % len(doctors)]
            patient = patients[index % len(patients)]
            appointment_date = today + timedelta(days=index // 3)
            Appointment.objects.get_or_create(
                doctor=doctor,
                date=appointment_date,
                time=appointment_times[index],
                defaults={
                    "patient": patient,
                    "status": Appointment.CONFIRMED if index % 2 == 0 else Appointment.SCHEDULED,
                    "type": Appointment.OPD,
                    "token_no": index + 1,
                    "notes": "Demo appointment generated by seed_demo_data.",
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo AHMS data."))
        self.stdout.write("Admin login: admin@ahms.local / Admin@12345")
