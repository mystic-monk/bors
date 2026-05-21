from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import OperatorReturn, LicenceReturn, VehicleEmission, VehicleAccessibility

CURRENT_YEAR = 2024


class GeneralForm(forms.ModelForm):
    class Meta:
        model = OperatorReturn
        fields = ['data_year', 'operator_name', 'trading_name', 'county', 'annual_revenue', 'taxsaver']
        widgets = {
            'data_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100, 'value': CURRENT_YEAR}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Legal name of operator'}),
            'trading_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trading name (if different)'}),
            'county': forms.Select(attrs={'class': 'form-select'}),
            'annual_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'taxsaver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_annual_revenue(self):
        val = self.cleaned_data.get('annual_revenue')
        if val is not None and val < 0:
            raise forms.ValidationError('Revenue must be a positive number.')
        return val


class LicenceForm(forms.ModelForm):
    class Meta:
        model = LicenceReturn
        fields = [
            'licence_no', 'route_no', 'on_free_travel', 'on_yasc', 'date_joined',
            'service_commenced', 'service_ceased', 'date_ceased',
            'total_passenger_journeys', 'free_travel_percent', 'km_operated', 'daily_pvr',
        ]
        widgets = {
            'licence_no': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Licence No'}),
            'route_no': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Route No'}),
            'on_free_travel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'on_yasc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'service_commenced': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'service_ceased': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_ceased': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'total_passenger_journeys': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'free_travel_percent': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'max': '100'}),
            'km_operated': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'daily_pvr': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
        }

    def clean_free_travel_percent(self):
        val = self.cleaned_data.get('free_travel_percent')
        if val is not None and not (0 <= val <= 100):
            raise forms.ValidationError('Must be between 0 and 100.')
        return val

    def clean(self):
        cleaned = super().clean()
        ceased = cleaned.get('service_ceased')
        date_ceased = cleaned.get('date_ceased')
        if ceased and not date_ceased:
            self.add_error('date_ceased', 'Please provide the date the service ceased.')
        return cleaned


class EmissionForm(forms.ModelForm):
    class Meta:
        model = VehicleEmission
        fields = [
            'res_id', 'vehicle_reg', 'regularly_deployed', 'make', 'model_version',
            'transmission', 'engine_type', 'fuel_type', 'euro_standard',
            'make_model_correct', 'seats_on_record', 'correct_seats', 'avl_gps',
        ]
        widgets = {
            'res_id': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'RES ID'}),
            'vehicle_reg': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Reg No.'}),
            'regularly_deployed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'make': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Make'}),
            'model_version': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Model'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g. Automatic'}),
            'engine_type': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Engine type'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'euro_standard': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'make_model_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seats_on_record': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'placeholder': 'On record'}),
            'correct_seats': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'placeholder': 'Correct no.'}),
            'avl_gps': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AccessibilityForm(forms.ModelForm):
    class Meta:
        model = VehicleAccessibility
        fields = [
            'res_id', 'vehicle_reg', 'wheelchair_spaces', 'wheelchair_access_type',
            'mechanical_ramp', 'centre_door_ramps', 'exterior_displays',
            'interior_stop_displays', 'audio_announcements', 'yellow_handrails',
            'priority_seating', 'contrasting_seat_covers', 'induction_loop',
        ]
        widgets = {
            'res_id': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'RES ID'}),
            'vehicle_reg': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Reg No.'}),
            'wheelchair_spaces': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'wheelchair_access_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'mechanical_ramp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'centre_door_ramps': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'exterior_displays': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'interior_stop_displays': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'audio_announcements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'yellow_handrails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority_seating': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contrasting_seat_covers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'induction_loop': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


LicenceFormSet = inlineformset_factory(
    OperatorReturn, LicenceReturn,
    form=LicenceForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

EmissionFormSet = inlineformset_factory(
    OperatorReturn, VehicleEmission,
    form=EmissionForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

AccessibilityFormSet = inlineformset_factory(
    OperatorReturn, VehicleAccessibility,
    form=AccessibilityForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)
