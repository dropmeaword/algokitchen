import re
FRACRE = re.compile(ur'(\d\ +)?(\d+/\d+)\b')
UNICRE = re.compile(ur'/^[1-9][0-9]?(?:[\xbc-\xbe])$/ugm')

FRACTIONS = {
    u'1/2' : u'\u00BD',
    u'1/4' : u'\u00BC',
    u'3/4' : u'\u00BE',
    u'1/3' : u'\u2153',
    u'2/3' : u'\u2154',
    u'1/5' : u'\u2155',
    u'2/5' : u'\u2156',
    u'3/5' : u'\u2157',
    u'4/5' : u'\u2158',
    u'1/6' : u'\u2159',
    u'5/6' : u'\u215A',
    u'1/8' : u'\u215B',
    u'3/8' : u'\u215C',
    u'5/8' : u'\u215D',
    u'7/8' : u'\u215E',
}

def fractions(s):
    def subfrac(m):
        pre, post = m.groups()
        frac = FRACTIONS.get(post)
        if frac is None:
            start, end = m.span()
            return m.string[start:end]
        if pre is not None:
            frac = pre[0] + frac
        return frac
    return FRACRE.sub(subfrac, s)


"""
https://en.wikipedia.org/wiki/Number_Forms

¼	1⁄4	0.25	Vulgar Fraction One Fourth	00BC	188
½	1⁄2	0.5	Vulgar Fraction One Half	00BD	189
¾	3⁄4	0.75	Vulgar Fraction Three Fourths	00BE	190
⅐	1⁄7	0.14285	Vulgar Fraction One Seventh	2150	8528
⅑	1⁄9	0.111...	Vulgar Fraction One Ninth	2151	8529
⅒	1⁄10	0.1	Vulgar Fraction One Tenth	2152	8530
⅓	1⁄3	0.333...	Vulgar Fraction One Third	2153	8531
⅔	2⁄3	0.666...	Vulgar Fraction Two Thirds	2154	8532
⅕	1⁄5	0.2	Vulgar Fraction One Fifth	2155	8533
⅖	2⁄5	0.4	Vulgar Fraction Two Fifths	2156	8534
⅗	3⁄5	0.6	Vulgar Fraction Three Fifths	2157	8535
⅘	4⁄5	0.8	Vulgar Fraction Four Fifths	2158	8536
⅙	1⁄6	0.166...	Vulgar Fraction One Sixth	2159	8537
⅚	5⁄6	0.833...	Vulgar Fraction Five Sixths	215A	8538
⅛	1⁄8	0.125	Vulgar Fraction One Eighth	215B	8539
⅜	3⁄8	0.375	Vulgar Fraction Three Eighths	215C	8540
⅝	5⁄8	0.625	Vulgar Fraction Five Eighths	215D	8541
⅞	7⁄8	0.875	Vulgar Fraction Seven Eighths	215E	8542
"""
