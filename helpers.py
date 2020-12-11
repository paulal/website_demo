from wtforms import FloatField


class FlexibleFloatField(FloatField):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)