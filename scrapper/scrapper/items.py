# -*- coding: utf-8 -*-
from scrapy import Item,  Field
from scrapy.loader.processors import Compose, MapCompose, Join, TakeFirst, Identity

# processing utilities
import re
from w3lib.html import remove_tags
import unicodedata


# cleaning and extracting utilities
def strip_spaces(input):
    if(isinstance(input, str)):
        return input.strip('\r\n\t ')
    else:
        return list(map(strip_spaces, input))


def extract_digits(input):
    if(isinstance(input, str)):
        return ''.join(re.findall(r'\b\d+\b', input))
    else:
        return list(map(extract_digits, input))


def extract_float(input):
    if(isinstance(input, str)):
        return ''.join(re.findall(r'\d+\,\d+', input))
    else:
        return list(map(extract_float, input))


def convert_lower(input):
    if(isinstance(input, str)):
        return input.lower()
    else:
        return list(map(convert_lower, input))


def remove_accents(input):
    if(isinstance(input, str)):
        return ''.join((c for c in unicodedata.normalize('NFD', input) if unicodedata.category(c) != 'Mn'))
    else:
        return list(map(remove_accents, input))


class PropertyItem(Item):
    internal_id = Field(
        input_processor=MapCompose(strip_spaces, remove_tags),
        output_processor=TakeFirst()
    )
    name = Field(
        input_processor=MapCompose(strip_spaces, remove_accents),
        output_processor=TakeFirst()
    )
    link = Field(
        input_processor=MapCompose(strip_spaces),
        output_processor=TakeFirst()
    )
    city = Field(
        input_processor=MapCompose(strip_spaces, remove_accents),
        output_processor=Join()
    )
    price = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    bedrooms = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    bathrooms = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    parking_spots = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    surface = Field(
        input_processor=MapCompose(extract_float),
        output_processor=TakeFirst()
    )
    neighborhood = Field(
        input_processor=MapCompose(strip_spaces),
        output_processor=Join()
    )
    status = Field()
    location = Field()

    description = Field(
        input_processor=MapCompose(remove_tags, convert_lower, remove_accents, strip_spaces),
        output_proccesor=Identity()
    )

    responsible = Field(
        input_processor=MapCompose(strip_spaces, remove_accents, remove_tags),
        output_processor=TakeFirst()
    )
    stratum = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    features = Field()
    other_features = Field()
    floor_location = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    antiquity = Field(
        input_processor=MapCompose(strip_spaces),
        output_processor=TakeFirst()
    )
    contact_info = Field()
    contact_phone = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=Join()
    )
    
