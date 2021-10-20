from django_filters import rest_framework as filters
from .models import User


class UserFilter(filters.FilterSet):
    gender = filters.ChoiceFilter(choices=User.GENDER_CHOICES)
    first_name = filters.CharFilter(lookup_expr='contains')
    last_name = filters.CharFilter(lookup_expr='contains')
    distance = filters.NumberFilter(lookup_expr="lt",
                                    method="get_geo_distance")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender']

    def get_geo_distance(self, queryset, name, value):
        latitude = self.request.user.latitude
        longitude = self.request.user.longitude
        ids = []
        for u in queryset:
            u_distance = u.get_geo_distance(latitude, longitude)
            if u_distance and u_distance < value:
                ids.append(u.id)
        return queryset.filter(id__in=ids)

