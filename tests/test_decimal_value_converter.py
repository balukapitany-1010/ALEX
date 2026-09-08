from decimal import Decimal
import pytest
from alex.esg.services.decimal_value_converter import DecimalValueConverter

def test_converter_accepts_decimal_comma():
    result = (DecimalValueConverter.to_decimal_18_4("53,95"))
    assert result == Decimal("53.9500")

def test_converter_accepts_integer():
    result = (DecimalValueConverter.to_decimal_18_4(114))
    assert result == Decimal("114.0000")

def test_converter_accepts_zero():
    result = (DecimalValueConverter.to_decimal_18_4("0"))
    assert result == Decimal("0.0000")


def test_converter_returns_none_for_none():
    assert (DecimalValueConverter.to_decimal_18_4(None) is None)

def test_converter_returns_none_for_blank():
    assert (DecimalValueConverter.to_decimal_18_4("   ") is None)

def test_converter_rounds_small_scientific_value():
    result = (DecimalValueConverter.to_decimal_18_4("6E-06"))
    assert result == Decimal("0.0000")

def test_converter_accepts_exact_scientific_value():
    result = (DecimalValueConverter.to_decimal_18_4("1E-4"))
    assert result == Decimal("0.0001")

def test_converter_rounds_to_four_decimals():
    result = (DecimalValueConverter.to_decimal_18_4("14.20838"))
    assert result == Decimal("14.2084")


def test_converter_rounds_0990099():
    result = (DecimalValueConverter.to_decimal_18_4("0.990099"))
    assert result == Decimal("0.9901")


def test_converter_rounds_1317724():
    result = (DecimalValueConverter.to_decimal_18_4("1.317724"))
    assert result == Decimal("1.3177")


def test_converter_rounds_2045455():
    result = (DecimalValueConverter.to_decimal_18_4("2.045455"))
    assert result == Decimal("2.0455")