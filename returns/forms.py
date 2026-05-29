from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import OperatorReturn, LicenceReturn, VehicleEmission, VehicleAccessibility, OperatorAccess, Declaration


class DeclarationForm(forms.ModelForm):
    class Meta:
        model = Declaration
        fields = ['signed_by', 'printed_name', 'declaration_date', 'position_in_company']
        widgets = {
            'signed_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank if completing digitally',
            }),
            'printed_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank if completing digitally',
            }),
            'declaration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'position_in_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. DIRECTOR',
            }),
        }


class OperatorAccessForm(forms.ModelForm):
    class Meta:
        model = OperatorAccess
        fields = ['operator_name', 'operator_email']
        widgets = {
            'operator_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CityLink Ltd'}),
            'operator_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'operator@example.com'}),
        }

CURRENT_YEAR = 2024


class GeneralForm(forms.ModelForm):
    class Meta:
        model = OperatorReturn
        fields = ['data_year', 'operator_name', 'trading_name', 'county', 'annual_revenue', 'taxsaver', 'taxsaver_other']
        widgets = {
            'data_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100, 'value': CURRENT_YEAR}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Legal name of operator'}),
            'trading_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trading name (if different)'}),
            'county': forms.Select(attrs={'class': 'form-select'}),
            'annual_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'taxsaver': forms.Select(attrs={'class': 'form-select', 'id': 'id_taxsaver'}),
            'taxsaver_other': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details…'}),
        }

    def clean_annual_revenue(self):
        val = self.cleaned_data.get('annual_revenue')
        if val is not None and val < 0:
            raise forms.ValidationError('Revenue must be a positive number.')
        return val

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('taxsaver') == 'other' and not cleaned.get('taxsaver_other', '').strip():
            self.add_error('taxsaver_other', 'Please provide details when "Other" is selected.')
        return cleaned


_YN = [('', '— Select —'), ('true', 'Yes'), ('false', 'No')]
_SEL = {'class': 'form-select form-select-sm'}


class LicenceForm(forms.ModelForm):
    # Override boolean fields with explicit Y/N dropdowns
    on_free_travel   = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='On Free Travel Scheme (Y/N)')
    on_yasc          = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='On YASC Scheme (Y/N)')
    service_commenced = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='Has the Service Commenced (Y/N)')
    service_ceased   = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='Has the Service Ceased (Y/N)')

    class Meta:
        model = LicenceReturn
        fields = [
            'route_no', 'on_free_travel', 'on_yasc', 'date_joined',
            'service_commenced', 'service_ceased', 'date_ceased',
            'total_passenger_journeys', 'free_travel_percent', 'km_operated', 'daily_pvr',
        ]
        widgets = {
            'route_no':                 forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Route No'}),
            'date_joined':              forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'date_ceased':              forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'total_passenger_journeys': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'free_travel_percent':      forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'max': '100'}),
            'km_operated':              forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'daily_pvr':                forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
        }
        labels = {
            'km_operated': '2025 Kilometres Operated',
            'daily_pvr':   '2025 Daily PVR',
            'date_joined': 'Date Joined YASC (DD/MM/YY)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate Y/N selects from existing boolean model values
        if self.instance.pk:
            for fname in ('on_free_travel', 'on_yasc', 'service_commenced', 'service_ceased'):
                self.initial[fname] = 'true' if getattr(self.instance, fname) else 'false'

    def _clean_yn(self, field):
        val = self.cleaned_data.get(field, '')
        if val not in ('true', 'false'):
            raise forms.ValidationError('Please select Yes or No.')
        return val == 'true'

    def clean_on_free_travel(self):   return self._clean_yn('on_free_travel')
    def clean_on_yasc(self):          return self._clean_yn('on_yasc')
    def clean_service_commenced(self): return self._clean_yn('service_commenced')
    def clean_service_ceased(self):   return self._clean_yn('service_ceased')

    def clean_free_travel_percent(self):
        val = self.cleaned_data.get('free_travel_percent')
        if val is not None and not (0 <= val <= 100):
            raise forms.ValidationError('Must be between 0 and 100.')
        return val

    def clean_km_operated(self):
        val = self.cleaned_data.get('km_operated')
        if val is not None and val < 0:
            raise forms.ValidationError('Must be 0 or greater.')
        return val

    def clean_daily_pvr(self):
        val = self.cleaned_data.get('daily_pvr')
        if val is not None and val < 0:
            raise forms.ValidationError('Must be 0 or greater.')
        return val

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('service_ceased') and not cleaned.get('date_ceased'):
            self.add_error('date_ceased', 'Required when service has ceased.')
        if cleaned.get('on_yasc') and not cleaned.get('date_joined'):
            self.add_error('date_joined', 'Required when on YASC scheme.')
        return cleaned


class EmissionForm(forms.ModelForm):
    regularly_deployed = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='Regularly deployed on scheduled services?')
    make_model_correct = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='Are the make/model/engine type details correct?')
    avl_gps           = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), label='Vehicle has AVL/GPS on board?')

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
            'make': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Make'}),
            'model_version': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Model'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g. Automatic'}),
            'engine_type': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Engine type'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'euro_standard': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'seats_on_record': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'placeholder': 'On record'}),
            'correct_seats': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0', 'placeholder': 'Correct no.'}),
        }

    def _clean_yn(self, field):
        v = self.cleaned_data.get(field)
        if v == 'true':  return True
        if v == 'false': return False
        return None

    def clean_regularly_deployed(self): return self._clean_yn('regularly_deployed')
    def clean_make_model_correct(self):  return self._clean_yn('make_model_correct')
    def clean_avl_gps(self):             return self._clean_yn('avl_gps')


class AccessibilityForm(forms.ModelForm):
    mechanical_ramp         = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Mechanical access ramp?')
    centre_door_ramps       = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Equipped with centre door ramps?')
    exterior_displays       = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Exterior backlit route displays?')
    interior_stop_displays  = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Interior stop displays?')
    audio_announcements     = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Interior automated audible stop announcements?')
    yellow_handrails        = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Yellow coloured handrails?')
    priority_seating        = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Priority seating?')
    contrasting_seat_covers = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Seat covers contrasting with floor colour?')
    induction_loop          = forms.ChoiceField(choices=_YN, widget=forms.Select(attrs=_SEL), required=False, label='Induction loop system?')

    _BOOL_FIELDS = [
        'mechanical_ramp', 'centre_door_ramps', 'exterior_displays',
        'interior_stop_displays', 'audio_announcements', 'yellow_handrails',
        'priority_seating', 'contrasting_seat_covers', 'induction_loop',
    ]

    class Meta:
        model = VehicleAccessibility
        fields = [
            'res_id', 'vehicle_reg', 'wheelchair_spaces', 'wheelchair_access_type',
            'mechanical_ramp', 'centre_door_ramps', 'exterior_displays',
            'interior_stop_displays', 'audio_announcements', 'yellow_handrails',
            'priority_seating', 'contrasting_seat_covers', 'induction_loop',
        ]
        widgets = {
            'res_id': forms.HiddenInput(),
            'vehicle_reg': forms.HiddenInput(),
            'wheelchair_spaces': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'wheelchair_access_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for f in self._BOOL_FIELDS:
                self.initial[f] = 'true' if getattr(self.instance, f) else 'false'

    def _clean_yn(self, field):
        v = self.cleaned_data.get(field)
        if v == 'true':  return True
        if v == 'false': return False
        return False

    def clean_mechanical_ramp(self):         return self._clean_yn('mechanical_ramp')
    def clean_centre_door_ramps(self):       return self._clean_yn('centre_door_ramps')
    def clean_exterior_displays(self):       return self._clean_yn('exterior_displays')
    def clean_interior_stop_displays(self):  return self._clean_yn('interior_stop_displays')
    def clean_audio_announcements(self):     return self._clean_yn('audio_announcements')
    def clean_yellow_handrails(self):        return self._clean_yn('yellow_handrails')
    def clean_priority_seating(self):        return self._clean_yn('priority_seating')
    def clean_contrasting_seat_covers(self): return self._clean_yn('contrasting_seat_covers')
    def clean_induction_loop(self):          return self._clean_yn('induction_loop')


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
