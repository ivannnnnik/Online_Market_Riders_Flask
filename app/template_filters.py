def price_format(value):
    value = str(value) + ' ₽'
    return value


def hidden_product_format(value):
    value = str(value)
    if len(value) > 20:
        value = value[:20] + '...'
        return value
    else:
        return value


FILTERS = [price_format, hidden_product_format]


def init_app(app):
    for func in FILTERS:
        app.add_template_filter(func)
