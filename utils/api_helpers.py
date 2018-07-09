from rest_framework import viewsets
import time


class FilterViewSet():
    #add this class to ModelViewSets Class
    # filter_fields = ["id", "name", "price"]

    def __init__(self, *args, **kwargs):
        super(FilterViewSet, self).__init__(*args, **kwargs)

    def get_serializer_model(self):
        return self.serializer_class

    @property#making it like a field of the class (this field name is needed for filtering functionality)
    def filter_fields(self):
        serializer_model = self.get_serializer_model()
        model_class = serializer_model.Meta.model
        #return all fields of the initial instance
        current_fields = serializer_model.Meta.fields
        all_model_fields = [f.name for f in model_class._meta.get_fields()]
        if current_fields == "__all__":
            fields = all_model_fields
        else:
            fields = current_fields
        filter_fields = list()
        for field in fields:
            if field in all_model_fields:
                if model_class._meta.get_field(field).get_internal_type() != "FileField":
                    filter_fields.append(field)
        return filter_fields