from rest_framework import serializers
from .models import (
    Cattle, Insemination, BirthRecord, Alert, Farm,
    TreatmentRecord, VaccinationRecord, PeriodicVaccinationRecord, PeriodicTreatmentRecord,
    GestationMilestone, GestationCheck
)
from django.utils import timezone
from datetime import timedelta

class CattleSerializer(serializers.ModelSerializer):
    last_insemination_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    last_calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    expected_calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    expected_insemination_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Cattle
        fields = [
            'id', 'ear_tag_no', 'breed', 'birth_date', 'gender', 'life_stage',
            'dam_id', 'sire_id', 'is_purchased', 'purchase_date', 'purchase_source',
            'last_insemination_date', 'last_calving_date', 'expected_calving_date',
            'expected_insemination_date', 'gestation_status', 'gestation_stage',
            'health_status', 'photo', 'created_at', 'updated_at', 'farm'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.photo:
            data['photo'] = self.context['request'].build_absolute_uri(instance.photo.url)
        return data

class InseminationSerializer(serializers.ModelSerializer):
    cattle_details = CattleSerializer(source='cattle', read_only=True)
    pregnancy_check_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True
    )
    insemination_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=True
    )
    expected_calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
        required=False,
        allow_null=True,
        read_only=True
    )

    class Meta:
        model = Insemination
        fields = '__all__'

    def validate(self, data):
        # Validate pregnancy check date is after insemination date
        if data.get('pregnancy_check_date') and data.get('insemination_date'):
            if data['pregnancy_check_date'] < data['insemination_date']:
                raise serializers.ValidationError({
                    'pregnancy_check_date': 'Pregnancy check date must be after insemination date'
                })
        
        # Validate pregnancy check status transitions
        if self.instance and data.get('pregnancy_check_status'):
            if self.instance.pregnancy_check_status == 'confirmed' and data['pregnancy_check_status'] != 'confirmed':
                raise serializers.ValidationError({
                    'pregnancy_check_status': 'Cannot change status once pregnancy is confirmed'
                })
        
        return data

class BirthRecordSerializer(serializers.ModelSerializer):
    calving_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
    )
    calf_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    mother_ear_tag = serializers.SerializerMethodField()
    
    class Meta:
        model = BirthRecord
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_mother_ear_tag(self, obj):
        return obj.cattle.ear_tag_no if obj.cattle else 'Unknown'

    def validate(self, data):
        # Validate that the mother is female
        cattle = data.get('cattle')
        if cattle and cattle.gender != 'female':
            raise serializers.ValidationError("Only female cattle can have birth records")

        # Validate that the mother was pregnant
        if cattle and cattle.gestation_status not in ['pregnant', 'calving']:
            raise serializers.ValidationError("Cattle must be pregnant or in calving stage to record birth")

        # Validate calving date is not in the future
        if data.get('calving_date') and data['calving_date'] > timezone.now().date():
            raise serializers.ValidationError("Calving date cannot be in the future")

        # Validate calf count and gender match
        if data.get('calf_count', 1) > 1:
            if not data.get('notes'):
                raise serializers.ValidationError("Please provide notes for multiple births")
            if ',' not in data.get('calf_gender', ''):
                raise serializers.ValidationError("For multiple births, provide genders separated by commas")
            if ',' not in data.get('calf_ear_tag', ''):
                raise serializers.ValidationError("For multiple births, provide ear tags separated by commas")
            
            # Validate number of genders matches calf count
            gender_count = len(data['calf_gender'].split(','))
            ear_tag_count = len(data['calf_ear_tag'].split(','))
            if gender_count != data['calf_count'] or ear_tag_count != data['calf_count']:
                raise serializers.ValidationError("Number of genders and ear tags must match calf count")

        # Validate ear tag format and uniqueness
        ear_tags = data.get('calf_ear_tag', '').split(',')
        for ear_tag in ear_tags:
            ear_tag = ear_tag.strip()
            if Cattle.objects.filter(ear_tag_no=ear_tag).exists():
                raise serializers.ValidationError(f"Ear tag {ear_tag} is already in use")

        # Validate complications field
        if data.get('calving_outcome') in ['complications', 'stillborn', 'died_shortly_after']:
            if not data.get('complications'):
                raise serializers.ValidationError("Please provide details about the complications")
            if not data.get('veterinary_assistance'):
                raise serializers.ValidationError("Please indicate if veterinary assistance was provided")

        return data

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
        
class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'

class TreatmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRecord
        fields = '__all__'

class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = '__all__'

class PeriodicVaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicVaccinationRecord
        fields = '__all__'

class PeriodicTreatmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTreatmentRecord
        fields = '__all__'

class GestationMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = GestationMilestone
        fields = '__all__'

class GestationCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = GestationCheck
        fields = '__all__'

class EnhancedCattleSerializer(CattleSerializer):
    gestation_progress = serializers.SerializerMethodField()
    trimester = serializers.SerializerMethodField()
    days_until_calving = serializers.SerializerMethodField()
    milestones = GestationMilestoneSerializer(source='gestation_milestones', many=True, read_only=True)
    gestation_checks = GestationCheckSerializer(many=True, read_only=True)

    class Meta(CattleSerializer.Meta):
        fields = CattleSerializer.Meta.fields + [
            'gestation_progress',
            'trimester',
            'days_until_calving',
            'milestones',
            'gestation_checks'
        ]

    def get_gestation_progress(self, obj):
        return obj.get_gestation_progress()

    def get_trimester(self, obj):
        return obj.get_trimester()

    def get_days_until_calving(self, obj):
        return obj.get_days_until_calving()

class GestationDataSerializer(serializers.Serializer):
    cattle = EnhancedCattleSerializer()
    treatment_records = TreatmentRecordSerializer(many=True)
    vaccination_records = VaccinationRecordSerializer(many=True)
    periodic_treatment_records = PeriodicTreatmentRecordSerializer(many=True)
    periodic_vaccination_records = PeriodicVaccinationRecordSerializer(many=True)
    alerts = AlertSerializer(many=True)
    gantt_data = serializers.SerializerMethodField()

    def get_gantt_data(self, obj):
        cattle = obj['cattle']
        if not cattle.last_insemination_date or cattle.gestation_status == 'not_pregnant':
            return None

        # Calculate dates and durations
        start_date = cattle.last_insemination_date
        end_date = cattle.expected_calving_date or (start_date + timedelta(days=280))
        today = timezone.now().date()
        
        # Create Gantt chart data with more detailed stages
        tasks = [
            {
                'id': f'{cattle.id}_oestrus',
                'name': 'In Oestrus',
                'start': (start_date - timedelta(days=2)).isoformat(),  # 2 days before insemination
                'end': start_date.isoformat(),
                'progress': 100,
                'type': 'stage',
                'project': None,
                'dependencies': []
            },
            {
                'id': f'{cattle.id}_insemination',
                'name': 'Insemination Day',
                'start': start_date.isoformat(),
                'end': start_date.isoformat(),
                'progress': 100,
                'type': 'milestone',
                'project': None,
                'dependencies': [f'{cattle.id}_oestrus']
            },
            {
                'id': f'{cattle.id}_early_pregnancy',
                'name': 'Early Pregnancy',
                'start': start_date.isoformat(),
                'end': (start_date + timedelta(days=90)).isoformat(),
                'progress': min(100, max(0, ((today - start_date).days / 90) * 100)) if today >= start_date else 0,
                'type': 'stage',
                'project': None,
                'dependencies': [f'{cattle.id}_insemination']
            },
            {
                'id': f'{cattle.id}_mid_pregnancy',
                'name': 'Mid Pregnancy',
                'start': (start_date + timedelta(days=91)).isoformat(),
                'end': (start_date + timedelta(days=180)).isoformat(),
                'progress': min(100, max(0, ((today - (start_date + timedelta(days=91))).days / 90) * 100)) if today >= (start_date + timedelta(days=91)) else 0,
                'type': 'stage',
                'project': None,
                'dependencies': [f'{cattle.id}_early_pregnancy']
            },
            {
                'id': f'{cattle.id}_late_pregnancy',
                'name': 'Late Pregnancy',
                'start': (start_date + timedelta(days=181)).isoformat(),
                'end': (start_date + timedelta(days=260)).isoformat(),
                'progress': min(100, max(0, ((today - (start_date + timedelta(days=181))).days / 79) * 100)) if today >= (start_date + timedelta(days=181)) else 0,
                'type': 'stage',
                'project': None,
                'dependencies': [f'{cattle.id}_mid_pregnancy']
            },
            {
                'id': f'{cattle.id}_dry_period',
                'name': 'Dry Period',
                'start': (start_date + timedelta(days=261)).isoformat(),
                'end': end_date.isoformat(),
                'progress': min(100, max(0, ((today - (start_date + timedelta(days=261))).days / 19) * 100)) if today >= (start_date + timedelta(days=261)) else 0,
                'type': 'stage',
                'project': None,
                'dependencies': [f'{cattle.id}_late_pregnancy']
            },
            {
                'id': f'{cattle.id}_expected_calving',
                'name': 'Expected Calving',
                'start': end_date.isoformat(),
                'end': end_date.isoformat(),
                'progress': 0,
                'type': 'milestone',
                'project': None,
                'dependencies': [f'{cattle.id}_dry_period']
            }
        ]

        # Add milestones from the database
        for milestone in cattle.gestation_milestones.all():
            tasks.append({
                'id': f'milestone_{milestone.id}',
                'name': milestone.get_milestone_type_display(),
                'start': milestone.due_date.isoformat(),
                'end': milestone.due_date.isoformat(),
                'progress': 100 if milestone.is_completed else 0,
                'type': 'milestone',
                'project': None,
                'dependencies': []
            })

        # Add health checks
        for check in cattle.gestation_checks.all():
            tasks.append({
                'id': f'check_{check.id}',
                'name': f'Health Check (Week {check.gestation_week})',
                'start': check.check_date.isoformat(),
                'end': check.check_date.isoformat(),
                'progress': 100,
                'type': 'milestone',
                'project': None,
                'dependencies': []
            })

        return {
            'tasks': tasks,
            'start_date': (start_date - timedelta(days=2)).isoformat(),  # Include oestrus period
            'end_date': end_date.isoformat()
        }

