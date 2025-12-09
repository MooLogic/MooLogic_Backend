from django.core.management.base import BaseCommand, CommandError
from core.models import Cattle, Farm
from django.utils import timezone
import random
from datetime import timedelta

BREEDS = [
    'Holstein', 'Jersey', 'Ayrshire', 'Guernsey', 'Brown Swiss', 'Sahiwal',
    'Zebu', 'Friesian', 'Red Sindhi', 'Indigenous'
]
GENDERS = ['female', 'male']
LIFE_STAGES = ['calf', 'heifer', 'cow', 'bull']
GESTATION_STATUS = ['not_pregnant', 'in_oestrus', 'missed_oestrus', 'pregnant', 'dry_off', 'calving']
GESTATION_STAGE = ['not_pregnant', 'first_trimester', 'second_trimester', 'third_trimester', 'calving']

class Command(BaseCommand):
    help = 'Seed the database with sample cattle for a given farm'

    def add_arguments(self, parser):
        parser.add_argument('farm_id', type=int, help='ID of the farm to attach cattle to')
        parser.add_argument('--count', type=int, default=50, help='Number of cattle to create')

    def handle(self, *args, **options):
        farm_id = options['farm_id']
        count = options['count']
        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            raise CommandError(f'Farm with id {farm_id} does not exist')

        created = []
        today = timezone.now().date()
        for i in range(count):
            # Randomize attributes
            gender = random.choice(GENDERS)
            # Age between 1 month and 8 years
            age_days = random.randint(30, 8 * 365)
            birth_date = today - timedelta(days=age_days)

            # Choose life stage consistent with age/gender
            if gender == 'female':
                if age_days < 365:
                    life_stage = 'calf'
                elif age_days < 2 * 365:
                    life_stage = 'heifer'
                else:
                    life_stage = 'cow'
            else:
                if age_days < 365:
                    life_stage = 'calf'
                elif age_days < 2 * 365:
                    life_stage = 'calf'
                else:
                    life_stage = 'bull'

            breed = random.choice(BREEDS)

            ear_tag = f"C-{farm.id}-{random.randint(10000,99999)}-{i}"

            # Randomly decide if purchased
            is_purchased = random.random() < 0.2
            purchase_date = None
            purchase_source = ''
            if is_purchased:
                purchase_days_ago = random.randint(1, 365 * 5)
                purchase_date = today - timedelta(days=purchase_days_ago)
                purchase_source = random.choice(['Local Market', 'Auction', 'Private Breeder', 'Import'])

            # Pregnancy attributes for females only
            last_insemination_date = None
            expected_calving_date = None
            expected_insemination_date = None
            gestation_status = 'not_pregnant'
            gestation_stage = 'not_pregnant'

            if gender == 'female' and life_stage in ['heifer', 'cow']:
                # 30% chance pregnant, 10% chance near calving
                r = random.random()
                if r < 0.3:
                    days_since_insemination = random.randint(0, 300)
                    last_insemination_date = today - timedelta(days=days_since_insemination)
                    expected_calving_date = last_insemination_date + timedelta(days=280)
                    gestation_status = 'pregnant'
                    # determine stage
                    if days_since_insemination < 90:
                        gestation_stage = 'first_trimester'
                    elif days_since_insemination < 180:
                        gestation_stage = 'second_trimester'
                    elif days_since_insemination < 270:
                        gestation_stage = 'third_trimester'
                    else:
                        gestation_stage = 'calving'
                        gestation_status = 'calving'
                elif r < 0.4:
                    # in oestrus
                    gestation_status = 'in_oestrus'
                elif r < 0.45:
                    gestation_status = 'missed_oestrus'

                # set last calving randomly for cows
                last_calving_date = None
                if life_stage == 'cow' and random.random() < 0.6:
                    last_calving_days_ago = random.randint(60, 4 * 365)
                    last_calving_date = today - timedelta(days=last_calving_days_ago)
                    expected_insemination_date = last_calving_date + timedelta(days=60)
            else:
                last_calving_date = None

            # Average daily milk for cows
            avg_daily_milk = 0
            if life_stage == 'cow':
                avg_daily_milk = round(random.uniform(5.0, 30.0), 2)

            cattle = Cattle.objects.create(
                farm=farm,
                ear_tag_no=ear_tag,
                breed=breed,
                birth_date=birth_date,
                gender=gender,
                life_stage=life_stage,
                dam_id='',
                sire_id='',
                is_purchased=is_purchased,
                purchase_date=purchase_date,
                purchase_source=purchase_source,
                last_insemination_date=last_insemination_date,
                last_calving_date=last_calving_date,
                expected_calving_date=expected_calving_date,
                expected_insemination_date=expected_insemination_date,
                gestation_status=gestation_status,
                gestation_stage=gestation_stage,
                health_status=random.choice(['healthy','sick']),
                calving_count=random.randint(0,5),
                current_lactation=random.randint(0,3),
                avg_daily_milk=avg_daily_milk
            )
            created.append(cattle)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created)} cattle for farm id {farm_id}'))
