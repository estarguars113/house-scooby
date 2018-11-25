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
    elif(isinstance(input, list)):
        return [i.strip('\r\n\t ') for i in input]


def extract_digits(input):
    return ''.join(re.findall(r'\b\d+\b', input))


def extract_float(input):
    return float(''.join(re.findall(r'\d+\.\d+', input)))

def parse_int(input):
    try:
        return int(input)
    except ValueError:
        return None

def convert_lower(input):
    if(isinstance(input, str)):
        return str(input).lower()
    elif(isinstance(input, list)):
        return [i.lower() for i in input]


def remove_accents(input):
    if(isinstance(input, str)):
        return ''.join(
            (c for c in unicodedata.normalize('NFD', input) if unicodedata.category(c) != 'Mn')
        )
    elif(isinstance(input, list)):
        return [remove_accents(c) for c in input]


def join_lines(input):
    return ''.join(input)


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
        input_processor=MapCompose(extract_digits, float),
        output_processor=TakeFirst()
    )
    bedrooms = Field(
        input_processor=MapCompose(extract_digits, parse_int),
        output_processor=TakeFirst()
    )
    bathrooms = Field(
        input_processor=MapCompose(remove_tags, extract_digits, parse_int),
        output_processor=TakeFirst()
    )
    parking_spots = Field(
        input_processor=MapCompose(remove_tags, extract_digits, parse_int),
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
    status = Field(
        input_processor=MapCompose(remove_accents),
        output_processor=TakeFirst(),
    )
    location = Field(
        input_processor=MapCompose(remove_accents),
        output_processor=TakeFirst(),
    )

    description = Field(
        input_processor=Compose(strip_spaces, convert_lower, remove_accents),
        output_processor=Join()
    )

    responsible = Field(
        input_processor=MapCompose(strip_spaces, remove_accents, remove_tags),
        output_processor=TakeFirst()
    )
    stratum = Field(
        input_processor=MapCompose(extract_digits, parse_int),
        output_processor=TakeFirst()
    )
    features = Field()
    other_features = Field()
    floor_location = Field(
        input_processor=MapCompose(extract_digits, parse_int),
        output_processor=TakeFirst()
    )
    total_levels = Field(
        input_processor=MapCompose(extract_digits, parse_int),
        output_processor=TakeFirst()
    )
    antiquity = Field(
        input_processor=MapCompose(remove_accents, strip_spaces),
        output_processor=TakeFirst()
    )
    contact_info = Field()
    contact_phone = Field(
        input_processor=MapCompose(extract_digits),
        output_processor=Join()
    )
    
