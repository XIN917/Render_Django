from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from tfms.models import TFM

User = get_user_model()

class Command(BaseCommand):
    help = "Seed TFMs using pre-existing students and teacher users (excluding admin)"

    def handle(self, *args, **kwargs):
        # Get seeded users
        students = list(User.objects.filter(role="student"))
        teachers = list(User.objects.filter(role="teacher", is_superuser=False))
        MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (Hello, PDF!) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000074 00000 n \n0000000178 00000 n \n0000000295 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF"

        if len(students) < 2 or len(teachers) < 2:
            self.stdout.write(self.style.ERROR("❌ At least 2 students and 2 non-admin teachers are required."))
            return

        # 🧹 Clean TFMs
        # TFM.objects.all().delete()
        # self.stdout.write("🧹 Previous TFMs deleted.")

        # 🧠 TFM 1
        tfm1 = TFM.objects.create(
            title="AI in Medical Imaging",
            description="Using deep learning to assist diagnosis.",
            file=ContentFile(MINIMAL_PDF, name="ai_medical.pdf"),
            student=students[0]
        )
        tfm1.directors.set([teachers[0]])
        tfm1.save()

        # 🔐 TFM 2
        tfm2 = TFM.objects.create(
            title="Blockchain for Education Records",
            description="A secure ledger for academic credentials.",
            file=ContentFile(MINIMAL_PDF, name="blockchain_edu.pdf"),
            student=students[1]
        )
        tfm2.directors.set(teachers[:2])  # max 2 directors
        tfm2.save()

        self.stdout.write(self.style.SUCCESS("✅ Sample TFMs created using existing users."))
