"""convert_country_names_to_codes

Revision ID: f1a2b3c4d5e7
Revises: e1a2b3c4d5f6
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa


revision = 'f1a2b3c4d5e7'
down_revision = 'e1a2b3c4d5f6'
branch_labels = None
depends_on = None


COUNTRY_NAME_TO_CODE = {
    'Afghanistan': 'AF',
    'Albania': 'AL',
    'Algeria': 'DZ',
    'Argentina': 'AR',
    'Australia': 'AU',
    'Austria': 'AT',
    'Bangladesh': 'BD',
    'Belgium': 'BE',
    'Brazil': 'BR',
    'Bulgaria': 'BG',
    'Canada': 'CA',
    'Chile': 'CL',
    'China': 'CN',
    'Colombia': 'CO',
    'Croatia': 'HR',
    'Czech Republic': 'CZ',
    'Denmark': 'DK',
    'Egypt': 'EG',
    'Estonia': 'EE',
    'Finland': 'FI',
    'France': 'FR',
    'Germany': 'DE',
    'Greece': 'GR',
    'Hungary': 'HU',
    'Iceland': 'IS',
    'India': 'IN',
    'Indonesia': 'ID',
    'Ireland': 'IE',
    'Israel': 'IL',
    'Italy': 'IT',
    'Japan': 'JP',
    'Kenya': 'KE',
    'Latvia': 'LV',
    'Lithuania': 'LT',
    'Malaysia': 'MY',
    'Mexico': 'MX',
    'Netherlands': 'NL',
    'New Zealand': 'NZ',
    'Nigeria': 'NG',
    'Norway': 'NO',
    'Pakistan': 'PK',
    'Peru': 'PE',
    'Philippines': 'PH',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Romania': 'RO',
    'Russia': 'RU',
    'Saudi Arabia': 'SA',
    'Serbia': 'RS',
    'Singapore': 'SG',
    'Slovakia': 'SK',
    'Slovenia': 'SI',
    'South Africa': 'ZA',
    'South Korea': 'KR',
    'Spain': 'ES',
    'Sweden': 'SE',
    'Switzerland': 'CH',
    'Thailand': 'TH',
    'Turkey': 'TR',
    'Ukraine': 'UA',
    'United Arab Emirates': 'AE',
    'United Kingdom': 'GB',
    'United States': 'US',
    'Venezuela': 'VE',
    'Vietnam': 'VN',
}


def upgrade() -> None:
    conn = op.get_bind()

    for country_name, country_code in COUNTRY_NAME_TO_CODE.items():
        conn.execute(
            sa.text("UPDATE users SET country = :code WHERE country = :name"),
            {"code": country_code, "name": country_name}
        )


def downgrade() -> None:
    conn = op.get_bind()

    for country_name, country_code in COUNTRY_NAME_TO_CODE.items():
        conn.execute(
            sa.text("UPDATE users SET country = :name WHERE country = :code"),
            {"name": country_name, "code": country_code}
        )
