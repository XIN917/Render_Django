from rest_framework import serializers
from .models import Semester

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format time fields as HH:MM
        for field in ['daily_start_time', 'daily_end_time', 'pre_duration']:
            value = data.get(field)
            if value:
                data[field] = value[:5]  # Truncate to HH:MM
        return data

    def validate(self, data):
        # Validate semester date range
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError({
                    'start_date': 'Semester start date must be strictly before the end date.'
                })
            if start_date.weekday() >= 5:
                raise serializers.ValidationError({
                    'start_date': 'Semester start date cannot be on a weekend.'
                })
            if end_date.weekday() >= 5:
                raise serializers.ValidationError({
                    'end_date': 'Semester end date cannot be on a weekend.'
                })

        # Validate presentation date range
        int_presentation_date = data.get('int_presentation_date')
        last_presentation_date = data.get('last_presentation_date')
        if int_presentation_date and last_presentation_date:
            if int_presentation_date >= last_presentation_date:
                raise serializers.ValidationError({
                    'int_presentation_date': 'Initial presentation date must be strictly before the last presentation date.'
                })
            if int_presentation_date.weekday() >= 5:
                raise serializers.ValidationError({
                    'int_presentation_date': 'Initial presentation date cannot be on a weekend.'
                })
            if last_presentation_date.weekday() >= 5:
                raise serializers.ValidationError({
                    'last_presentation_date': 'Last presentation date cannot be on a weekend.'
                })

        # Check all associated slots are within the new presentation window (on update)
        instance = getattr(self, 'instance', None)
        if instance and int_presentation_date and last_presentation_date:
            from slots.models import Slot
            slots = Slot.objects.filter(track__semester=instance)
            before = [slot.date for slot in slots if slot.date < int_presentation_date]
            after = [slot.date for slot in slots if slot.date > last_presentation_date]
            errors = {}
            if before:
                before_str = [d.strftime('%Y-%m-%d') for d in sorted(set(before))]
                errors['int_presentation_date'] = (
                    f"Cannot set initial presentation date to {int_presentation_date.strftime('%Y-%m-%d')}: "
                    f"slot(s) exist before this date: {before_str}"
                )
            if after:
                after_str = [d.strftime('%Y-%m-%d') for d in sorted(set(after))]
                errors['last_presentation_date'] = (
                    f"Cannot set last presentation date to {last_presentation_date.strftime('%Y-%m-%d')}: "
                    f"slot(s) exist after this date: {after_str}"
                )
            if errors:
                raise serializers.ValidationError(errors)
        return data

    def validate_delete(self, instance):
        # Prevent deletion if there are tracks associated
        tracks = instance.track_set.all()
        if tracks.exists():
            track_names = [track.title for track in tracks]
            raise serializers.ValidationError(
                {'non_field_errors': f'Cannot delete semester: tracks are still associated with this semester: {track_names}'}
            )
        return instance
