import re
from typing import Optional

def truncate_float(f: float, digits: int):
    """
    Truncates float values to desired number of digits
    
    Args:
        f (float): Float to truncate
        digits (int): The number of digits to truncate the float to
    """
    scale_factor = 10**digits
    return int(f * scale_factor)/scale_factor

def coefficient_multiplication(term: str, truncate_digits: Optional[int]) -> str:
    """Uses regex to multiply numbers if multiplication is implied. For example, 4.2*5*ATP->21*ATP"""

    r"""
    REGEX INFO
    ^ means the pattern must occur at the start of the string

    FIRST CAPTURING GROUP (\d+(\.\d+)?)
    \d+ matches an unlimited number of continuous digits

    SECOND CAPTURING GROUP (\.d+)?
    \. matches .
    d+ matches an unlimited number of continuous digits
    ? means check for this capturing group zero or one times

    So the first and second group match a decimal number

    [*] matches the * character

    THIRD AND FOURTH CAPTURING GROUP (\d+(\.\d+)?)
    Repeat of the first and second capturing group

    [*]? matches the * character optionally. So we can have 4.2*5*ATP or 4.2*5ATP

    FIFTH CAPTURING GROUP (.*)
    . matches any character
    * means match any character an unlimited number of times
    Basically grabs everything else present after the multiplication

    """
    regex_match = re.match(r"^(\d+(\.\d+)?)[*](\d+(\.\d+)?)[*]?(.*)", term)
    if regex_match:
        first_number = float(regex_match.group(1))
        second_number = float(regex_match.group(3))
        raw_species = regex_match.group(5)
        if (first_number*second_number).is_integer():
            product = int(first_number*second_number)
        elif truncate_digits:
            product = truncate_float(first_number*second_number, truncate_digits)
        else: #If no truncate digits provided, don't truncate the float
            product = first_number*second_number
        return f"{product}{raw_species}"
    else:
        return term


def split_species_coeff(term: str) -> tuple[str, int | float]:
    """Uses regex to split a term into species and coefficients."""

    r"""
    REGEX INFO
    ^ means match must be at the start of the term
    FIRST CAPTURING GROUP (\d+(\.\d+)?)
    \d+ matches any continuous string of numbers
    SECOND CAPTURING GROUP (\.d+)
    \. matches the decimal .
    d+ matches any coninuous string of numbers
    ? means match this 0 to 1 times
    The first and second capturing group capture the decimal term in front
    
    [*]? optionally matches the asterisk *. So we can have 5*ATP or 5ATP

    THIRD CAPTURING GROUP (.*)
    .* means match any character an unlimited number of times

    """
    regex_match = re.match(r"^(\d+(\.\d+)?)[*]?(.*)", term)
    if regex_match: #Means a number is detected in front of the term
        coefficient = float(regex_match.group(1))
        if coefficient.is_integer():
            coefficient = int(coefficient)
        raw_term = regex_match.group(3)
    else: #No number found means we default to 1
        coefficient = 1
        raw_term = term
    return raw_term, coefficient

def process_reaction_side(reaction_side: str, 
                          apply_multiplication: bool, 
                          truncate_digits: Optional[int],
                          reaction_index: Optional[int] = None):
    """
    Process one side of the reaction and returns a dict of {species: coeff}
    """

    #List of terms (with coefficient)
    #For example, "A + 2*B" -> ["A", "2*B"]
    raw_term_list = [term.strip() for term in reaction_side.split("+")]

    #Apply multiplication if needed
    if apply_multiplication:
        post_mult_list = [coefficient_multiplication(term, truncate_digits=truncate_digits) for term in raw_term_list]
    else:
        post_mult_list = raw_term_list
    
    #Return list of (species, coeff)
    coeff_term_list = [split_species_coeff(term) for term in post_mult_list]

    coeff_dict: dict[str, int|float] = {}
    for s, c in coeff_term_list:
        if not s.strip():
            continue
        if s in coeff_dict:
            if reaction_index:
                raise KeyError(f"Duplicate species {s} for reaction side {reaction_side} (reaction {reaction_index})")
            else:
                raise KeyError(f"Duplicate species {s} for reaction side {reaction_side}")
        coeff_dict[s] = c

    return coeff_dict
