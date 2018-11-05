# -*- coding: utf-8 -*-
from scrapy import Item,  Field
from scrapy.loader.processors import Compose, MapCompose, Join, TakeFirst, Identity

# processing utilities
import re
from w3lib.html import remove_tags
import unicodedata


# cleaning and extracting utilities
def strip_spaces(input):
    return input


def extract_digits(input):
    return re.findall(r'\b\d+\b', input)


def remove_accents(input):
    return ''.join((c for c in unicodedata.normalize('NFD', input) if unicodedata.category(c) != 'Mn'))


class PropertyItem(Item):
    internal_id = Field(
        input_processor=MapCompose(strip_spaces, remove_tags),
        output_processor=TakeFirst()
    )
    name = Field(
        input_processor=MapCompose(strip_spaces, remove_accents),
        output_processor=Join()
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
        input_processor=MapCompose(extract_digits),
        output_processor=Identity()
    )
    neighborhood = Field(
        input_processor=MapCompose(strip_spaces),
        output_processor=Join()
    )
    status = Field()
    location = Field()

    description = Field(
        input_processor=MapCompose(remove_tags, remove_accents, strip_spaces),
        output_proccesor=Identity()
    )

    responsible = Field(
        input_processor=MapCompose(strip_spaces, remove_accents, remove_tags),
        output_processor=Join()
    )
    stratum = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=TakeFirst()
    )
    features = Field()
    other_features = Field()
    floor_location = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=Identity()
    )
    antiquity = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=Identity()
    )
    contact_info = Field()
    contact_phone = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=Join()
    )
    
